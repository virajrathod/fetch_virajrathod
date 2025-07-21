-- 1. Top 5 brands by receipts scanned for most recent month
SELECT b.Name AS BrandName, COUNT(DISTINCT r._id) AS ReceiptsScanned
FROM receipts r
JOIN rewardsReceiptItems ri ON r._id = ri.receipt_id
JOIN brands b ON ri.barcode = b.barcode
WHERE r.createDate >= DATE_FORMAT(NOW(), '%Y-%m-01') -- First day of current month
GROUP BY b.Name
ORDER BY ReceiptsScanned DESC
LIMIT 5;
-- -> 
-- Swanson	11
-- Tostitos	11
-- Cracker Barrel Cheese	10
-- Prego	4
-- Diet Chris Cola	4

-- 2. Compare the top 5 brands by receipts scanned in the most recent month versus the previous month
WITH ReceiptBrands AS (
    SELECT r._id AS receipt_id, b.name AS brand_name, FROM_UNIXTIME(r.createDate / 1000) AS converted_date,
        DATE_FORMAT(FROM_UNIXTIME(r.createDate / 1000), '%Y-%m') AS yr_month
    FROM receipts r
    JOIN rewardsReceiptItems rri ON r._id = rri.receipt_id
    JOIN brands b ON rri.barcode = b.barcode
    WHERE r.createDate IS NOT NULL
),
BrandCounts AS (
    SELECT yr_month, brand_name, COUNT(DISTINCT receipt_id) AS receipt_count
    FROM ReceiptBrands
    WHERE yr_month IN ('2021-02', '2021-03')  -- Feb and March 2021 only
    GROUP BY yr_month, brand_name
),
RankedBrands AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY yr_month ORDER BY receipt_count DESC) AS rank
    FROM BrandCounts
)
SELECT rb_march.brand_name AS march_brand, rb_march.rank AS march_rank, rb_march.receipt_count AS march_receipts,
    rb_feb.brand_name AS feb_brand, rb_feb.rank AS feb_rank, rb_feb.receipt_count AS feb_receipts
FROM RankedBrands rb_march
LEFT JOIN RankedBrands rb_feb
ON rb_march.brand_name = rb_feb.brand_name AND rb_feb.yr_month = '2021-02'
WHERE rb_march.yr_month = '2021-03' AND rb_march.rank <= 5
ORDER BY rb_march.rank;

-- 3. Average spend from receipts with 'Accepted' or 'Rejected' status
SELECT rewardsReceiptStatus, AVG(totalSpent) AS AvgSpend
FROM receipts
WHERE rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY rewardsReceiptStatus;
-- -> REJECTED	23.326056 has the highest average spend

-- 4. Total number of items purchased from receipts with 'Accepted' or 'Rejected' 
SELECT rewardsReceiptStatus, SUM(purchasedItemCount) AS TotalItems
FROM receipts
WHERE rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY rewardsReceiptStatus;
-- -> REJECTED 173 has the highest total items purchased

-- 5. Brand with most spend among users created in last 6 months (from Sept 2020)
SELECT b.name AS BrandName, SUM(CAST(r.totalSpent AS DECIMAL(10,2))) AS TotalSpend
FROM users u
JOIN receipts r ON u._id = r.userId
JOIN rewardsReceiptItems ri ON r._id = ri.receipt_id
JOIN brands b ON ri.barcode = b.barcode
WHERE DATE(FROM_UNIXTIME(u.createdDate / 1000)) >= '2020-09-01'
GROUP BY b.name
ORDER BY TotalSpend DESC
LIMIT 1;
-- -> Tostitos 15799.37

-- 6. Brand with most transactions among users created in last 6 months (from Sept 2020)
SELECT b.name AS BrandName, COUNT(DISTINCT r._id) AS TotalTransactions
FROM users u
JOIN receipts r ON u._id = r.userId
JOIN rewardsReceiptItems ri ON r._id = ri.receipt_id
JOIN brands b ON ri.barcode = b.barcode
WHERE DATE(FROM_UNIXTIME(u.createdDate / 1000)) >= '2020-09-01'
GROUP BY b.name
ORDER BY TotalTransactions DESC
LIMIT 1;
-- -> Swanson 11