CREATE TABLE `users` (
  `_id` varchar(24) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `createdDate` bigint(20) NOT NULL,
  `lastLogin` bigint(20) DEFAULT NULL,
  `role` varchar(50) NOT NULL,
  `signUpSource` varchar(50) DEFAULT NULL,
  `state` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`_id`)
);

CREATE TABLE `brands` (
  `_id` varchar(24) NOT NULL,
  `barcode` varchar(50) DEFAULT NULL,
  `brandCode` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `categoryCode` varchar(100) DEFAULT NULL,
  `cpg_id` varchar(24) DEFAULT NULL,
  `cpg_ref` varchar(50) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `topBrand` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`_id`)
);

CREATE TABLE `receipts` (
  `_id` varchar(24) NOT NULL,
  `bonusPointsEarned` int(11) DEFAULT NULL,
  `bonusPointsEarnedReason` varchar(255) DEFAULT NULL,
  `createDate` bigint(20) NOT NULL,
  `dateScanned` bigint(20) NOT NULL,
  `finishedDate` bigint(20) DEFAULT NULL,
  `modifyDate` bigint(20) NOT NULL,
  `pointsAwardedDate` bigint(20) DEFAULT NULL,
  `pointsEarned` decimal(10,2) DEFAULT NULL,
  `purchaseDate` bigint(20) DEFAULT NULL,
  `purchasedItemCount` int(11) DEFAULT NULL,
  `rewardsReceiptStatus` varchar(50) NOT NULL,
  `totalSpent` decimal(10,2) DEFAULT NULL,
  `userId` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`_id`)
);

CREATE TABLE `rewardsReceiptItems` (
  `receipt_id` varchar(24) NOT NULL,
  `partnerItemId` varchar(50) NOT NULL,
  `barcode` varchar(50) DEFAULT NULL,
  `brandCode` varchar(100) DEFAULT NULL,
  `competitiveProduct` tinyint(1) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `discountedItemPrice` decimal(10,2) DEFAULT NULL,
  `finalPrice` decimal(10,2) DEFAULT NULL,
  `itemPrice` decimal(10,2) DEFAULT NULL,
  `itemNumber` varchar(50) DEFAULT NULL,
  `needsFetchReview` tinyint(1) DEFAULT NULL,
  `needsFetchReviewReason` varchar(100) DEFAULT NULL,
  `originalFinalPrice` decimal(10,2) DEFAULT NULL,
  `originalMetaBriteBarcode` varchar(50) DEFAULT NULL,
  `originalMetaBriteDescription` text DEFAULT NULL,
  `originalMetaBriteItemPrice` decimal(10,2) DEFAULT NULL,
  `originalMetaBriteQuantityPurchased` int(11) DEFAULT NULL,
  `originalReceiptItemText` text DEFAULT NULL,
  `pointsEarned` decimal(10,2) DEFAULT NULL,
  `pointsNotAwardedReason` varchar(255) DEFAULT NULL,
  `pointsPayerId` varchar(24) DEFAULT NULL,
  `preventTargetGapPoints` tinyint(1) DEFAULT NULL,
  `priceAfterCoupon` decimal(10,2) DEFAULT NULL,
  `quantityPurchased` int(11) DEFAULT NULL,
  `rewardsGroup` varchar(255) DEFAULT NULL,
  `rewardsProductPartnerId` varchar(24) DEFAULT NULL,
  `targetPrice` decimal(10,2) DEFAULT NULL,
  `userFlaggedBarcode` varchar(50) DEFAULT NULL,
  `userFlaggedDescription` text DEFAULT NULL,
  `userFlaggedNewItem` tinyint(1) DEFAULT NULL,
  `userFlaggedPrice` decimal(10,2) DEFAULT NULL,
  `userFlaggedQuantity` int(11) DEFAULT NULL,
  `deleted` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`receipt_id`,`partnerItemId`)
);