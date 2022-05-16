CREATE TABLE `Devices` (
  `DeviceID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) DEFAULT NULL,
  `InactiveDate` varchar(45) DEFAULT NULL,
  `CreatedDate` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`DeviceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `DateAdded` datetime NOT NULL,
  `DeviceID` int DEFAULT NULL,
  `Note` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=290 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `PowerStatus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `DeviceId` int DEFAULT NULL,
  `DeviceOn` tinyint DEFAULT NULL,
  `CurrentPowerUsage` float DEFAULT NULL,
  `AveragePowerUsage` float DEFAULT NULL,
  `LastOnTime` datetime DEFAULT NULL,
  `LastOffTime` datetime DEFAULT NULL,
  `UpdateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `PowerLog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `DeviceId` int DEFAULT NULL,
  `PowerLevel` float DEFAULT NULL,
  `DateAdded` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=262237 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `MonitorStatus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `DateUpdated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
