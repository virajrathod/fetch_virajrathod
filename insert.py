import json
import mysql.connector
from datetime import datetime
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('insert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database connection config
db_config = {
    'host': '10.100.106.151',
    'user': 'viraj.rathod',
    'password': 'i4#O9BhTO436OH8',
    'database': 'viraj'
}

# Improved JSON loader to handle multiple JSON objects or array
def load_json(file_path):
    logger.info(f"Loading JSON file: {file_path}")
    data = []
    with open(file_path, 'r') as file:
        content = file.read().strip()
        try:
            # Try to parse as JSON array
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: parse line by line (newline-delimited JSON)
            logger.warning(f"File {file_path} is not a JSON array, loading line-by-line.")
            file.seek(0)
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in {file_path} line {line_num}: {e}")
    return data

def convert_timestamp(timestamp):
    if isinstance(timestamp, dict) and '$date' in timestamp:
        # timestamp could be int or string millis
        ts = timestamp['$date']
        if isinstance(ts, int):
            return ts
        elif isinstance(ts, str) and ts.isdigit():
            return int(ts)
    elif isinstance(timestamp, int):
        return timestamp
    return None

def insert_data():
    try:
        logger.info("Connecting to MySQL database")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Load data
        users_data = load_json('users.json')
        brands_data = load_json('brands.json')
        receipts_data = load_json('receipts.json')

        # Insert Users first (to fix FK issues)
        logger.info("Inserting users...")
        user_ids = set()
        for user in tqdm(users_data, desc="Users"):
            user_id = user.get('_id', {}).get('$oid')
            if not user_id:
                logger.warning(f"User missing _id, skipping: {user}")
                continue
            if user_id in user_ids:
                continue
            user_ids.add(user_id)
            active = user.get('active', False)
            created_date = convert_timestamp(user.get('createdDate'))
            last_login = convert_timestamp(user.get('lastLogin'))
            role = user.get('role')
            sign_up_source = user.get('signUpSource')
            state = user.get('state')

            insert_user = """
            INSERT INTO users (_id, active, createdDate, lastLogin, role, signUpSource, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE active=VALUES(active), lastLogin=VALUES(lastLogin)
            """
            cursor.execute(insert_user, (user_id, active, created_date, last_login, role, sign_up_source, state))

        conn.commit()
        logger.info("Users inserted successfully.")

        # Insert Brands next
        logger.info("Inserting brands...")
        brand_ids = set()
        for brand in tqdm(brands_data, desc="Brands"):
            brand_id = brand.get('_id', {}).get('$oid')
            if not brand_id:
                logger.warning(f"Brand missing _id, skipping: {brand}")
                continue
            if brand_id in brand_ids:
                continue
            brand_ids.add(brand_id)
            barcode = brand.get('barcode')
            brand_code = brand.get('brandCode')
            category = brand.get('category')
            category_code = brand.get('categoryCode')
            cpg_id = brand.get('cpg', {}).get('$id', {}).get('$oid') if brand.get('cpg') else None
            cpg_ref = brand.get('cpg', {}).get('$ref') if brand.get('cpg') else None
            name = brand.get('name')
            top_brand = brand.get('topBrand', False)

            insert_brand = """
            INSERT INTO brands (_id, barcode, brandCode, category, categoryCode, cpg_id, cpg_ref, name, topBrand)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), barcode=VALUES(barcode)
            """
            cursor.execute(insert_brand, (brand_id, barcode, brand_code, category, category_code, cpg_id, cpg_ref, name, top_brand))

        conn.commit()
        logger.info("Brands inserted successfully.")

        # Insert Receipts and Receipt Items last
        logger.info("Inserting receipts and items...")
        receipt_ids = set()
        for receipt in tqdm(receipts_data, desc="Receipts"):
            receipt_id = receipt.get('_id', {}).get('$oid')
            if not receipt_id:
                logger.warning(f"Receipt missing _id, skipping: {receipt}")
                continue
            if receipt_id in receipt_ids:
                continue
            receipt_ids.add(receipt_id)

            user_id = receipt.get('userId')
            if not user_id or user_id not in user_ids:
                logger.warning(f"Receipt {receipt_id} references missing userId {user_id}, skipping insert.")
                continue  # Skip FK invalid records

            insert_receipt = """
            INSERT INTO receipts (_id, bonusPointsEarned, bonusPointsEarnedReason, createDate, dateScanned, finishedDate,
                                 modifyDate, pointsAwardedDate, pointsEarned, purchaseDate, purchasedItemCount,
                                 rewardsReceiptStatus, totalSpent, userId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE totalSpent=VALUES(totalSpent), pointsEarned=VALUES(pointsEarned)
            """
            cursor.execute(insert_receipt, (
                receipt_id,
                receipt.get('bonusPointsEarned'),
                receipt.get('bonusPointsEarnedReason'),
                convert_timestamp(receipt.get('createDate')),
                convert_timestamp(receipt.get('dateScanned')),
                convert_timestamp(receipt.get('finishedDate')),
                convert_timestamp(receipt.get('modifyDate')),
                convert_timestamp(receipt.get('pointsAwardedDate')),
                float(receipt.get('pointsEarned', 0)) if receipt.get('pointsEarned') else None,
                convert_timestamp(receipt.get('purchaseDate')),
                receipt.get('purchasedItemCount'),
                receipt.get('rewardsReceiptStatus'),
                float(receipt.get('totalSpent', 0)) if receipt.get('totalSpent') else None,
                user_id
            ))

            # Insert receipt items
            items = receipt.get('rewardsReceiptItemList', [])
            for item in items:
                insert_item = """
                INSERT INTO rewardsReceiptItems (
                    receipt_id, barcode, brandCode, competitiveProduct, description, discountedItemPrice, finalPrice,
                    itemPrice, itemNumber, needsFetchReview, needsFetchReviewReason, originalFinalPrice,
                    originalMetaBriteBarcode, originalMetaBriteDescription, originalMetaBriteItemPrice,
                    originalMetaBriteQuantityPurchased, originalReceiptItemText, partnerItemId, pointsEarned,
                    pointsNotAwardedReason, pointsPayerId, preventTargetGapPoints, priceAfterCoupon, quantityPurchased,
                    rewardsGroup, rewardsProductPartnerId, targetPrice, userFlaggedBarcode, userFlaggedDescription,
                    userFlaggedNewItem, userFlaggedPrice, userFlaggedQuantity, deleted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_item, (
                    receipt_id,
                    item.get('barcode'),
                    item.get('brandCode'),
                    item.get('competitiveProduct', False),
                    item.get('description'),
                    float(item.get('discountedItemPrice', 0)) if item.get('discountedItemPrice') else None,
                    float(item.get('finalPrice', 0)) if item.get('finalPrice') else None,
                    float(item.get('itemPrice', 0)) if item.get('itemPrice') else None,
                    item.get('itemNumber'),
                    item.get('needsFetchReview', False),
                    item.get('needsFetchReviewReason'),
                    float(item.get('originalFinalPrice', 0)) if item.get('originalFinalPrice') else None,
                    item.get('originalMetaBriteBarcode'),
                    item.get('originalMetaBriteDescription'),
                    float(item.get('originalMetaBriteItemPrice', 0)) if item.get('originalMetaBriteItemPrice') else None,
                    item.get('originalMetaBriteQuantityPurchased'),
                    item.get('originalReceiptItemText'),
                    item.get('partnerItemId'),
                    float(item.get('pointsEarned', 0)) if item.get('pointsEarned') else None,
                    item.get('pointsNotAwardedReason'),
                    item.get('pointsPayerId'),
                    item.get('preventTargetGapPoints', False),
                    float(item.get('priceAfterCoupon', 0)) if item.get('priceAfterCoupon') else None,
                    item.get('quantityPurchased'),
                    item.get('rewardsGroup'),
                    item.get('rewardsProductPartnerId'),
                    float(item.get('targetPrice', 0)) if item.get('targetPrice') else None,
                    item.get('userFlaggedBarcode'),
                    item.get('userFlaggedDescription'),
                    item.get('userFlaggedNewItem', False),
                    float(item.get('userFlaggedPrice', 0)) if item.get('userFlaggedPrice') else None,
                    item.get('userFlaggedQuantity'),
                    item.get('deleted', False)
                ))

        conn.commit()
        logger.info("Receipts and items inserted successfully.")

    except mysql.connector.Error as err:
        logger.error(f"MySQL Error: {err}")
    except Exception as e:
        logger.error(f"General Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    insert_data()

