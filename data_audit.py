import json

def load_json_lines(file_path):
    with open(file_path, 'r') as f:
        content = f.read().strip()
        try:
            # Try JSON array
            return json.loads(content)
        except json.JSONDecodeError:
            # fallback line by line JSON objects
            f.seek(0)
            data = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"JSON error in {file_path} line {line_num}: {e}")
            return data

# Load users and receipts
users = load_json_lines('users.json')
receipts = load_json_lines('receipts.json')

print(f"Loaded {len(users)} users and {len(receipts)} receipts")

user_ids = set(u.get('_id', {}).get('$oid') for u in users if u.get('_id'))
print(f"Unique users found: {len(user_ids)}")

# Check FK: receipts referencing missing users
missing_users = []
for r in receipts:
    user_id = r.get('userId')
    if user_id not in user_ids:
        missing_users.append(r.get('_id', {}).get('$oid'))

print(f"Receipts referencing missing users: {len(missing_users)}")
if missing_users:
    print("Sample receipts with missing users:", missing_users[:5])

# Check duplicates in users
seen = set()
duplicates = set()
for u in users:
    uid = u.get('_id', {}).get('$oid')
    if uid in seen:
        duplicates.add(uid)
    else:
        seen.add(uid)
print(f"Duplicate user IDs found: {len(duplicates)}")

# Date sanity checks
def convert_timestamp(ts):
    if isinstance(ts, dict) and '$date' in ts:
        return int(ts['$date'])
    elif isinstance(ts, int):
        return ts
    return None

bad_date_order = []
for r in receipts:
    create = convert_timestamp(r.get('createDate'))
    finished = convert_timestamp(r.get('finishedDate'))
    if create and finished and finished < create:
        bad_date_order.append(r.get('_id', {}).get('$oid'))
print(f"Receipts with finishedDate earlier than createDate: {len(bad_date_order)}")

# Purchased item count check
count_mismatch = []
for r in receipts:
    item_count = r.get('purchasedItemCount')
    items_list = r.get('rewardsReceiptItemList', [])
    if item_count != len(items_list):
        count_mismatch.append(r.get('_id', {}).get('$oid'))
print(f"Receipts with purchasedItemCount mismatch: {len(count_mismatch)}")
if count_mismatch:
    print("Sample receipts with item count mismatch:", count_mismatch[:5])

