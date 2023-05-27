CREATE DATABASE IF NOT EXISTS `smart_home`;
USE `smart_home`;

CREATE TABLE IF NOT EXISTS `environment_data` (
    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `temperature` int NOT NULL,
    `brightness` int NOT NULL,
    `wetness` int NOT NULL,
    `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `system_data` (
    `field` varchar(255) NOT NULL PRIMARY KEY,
    `status` INT NOT NULL
);

INSERT INTO `system_data` (field, status) VALUES ('water_sprinkler_status', 0);
INSERT INTO `system_data` (field, status) VALUES ('wetness_value', 0);