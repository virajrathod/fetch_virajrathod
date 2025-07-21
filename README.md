# README - Data Quality and Foreign Key Constraint Issue Explanation

## Problem:

When inserting receipt data into the `receipts` table, I encountered foreign key constraint errors:

    ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails
    (`viraj`.`receipts`, CONSTRAINT `receipts_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `users` (`_id`))

This means some receipts reference `userId`s that do not exist in the `users` table at insert time.

## Root Cause:

- The receipts were attempted to be inserted **before or without inserting the related users**.
- Or some receipts have `userId` values that are missing or malformed compared to the user `_id`s.
- Additionally, recreating (dropping and re-creating) tables reset the data, so inserts must follow the correct order.

## Additional Notes:

- Similar ordering is necessary for `brands` and `rewardsReceiptItems` (which depend on receipts).
- Improved JSON parsing is necessary to avoid failures due to malformed input.
