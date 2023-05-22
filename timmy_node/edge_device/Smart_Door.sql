-- phpMyAdmin SQL Dump
-- version 5.0.4deb2+deb11u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 22, 2023 at 09:25 PM
-- Server version: 10.5.19-MariaDB-0+deb11u2
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Smart Door`
--
CREATE DATABASE IF NOT EXISTS `Smart Door` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `Smart Door`;

-- --------------------------------------------------------

--
-- Table structure for table `History`
--

CREATE TABLE IF NOT EXISTS `History` (
  `history_id` int(11) NOT NULL AUTO_INCREMENT,
  `profile_id` int(11) NOT NULL,
  `time` time NOT NULL DEFAULT current_timestamp(),
  `date` date NOT NULL DEFAULT current_timestamp(),
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `bmi` float DEFAULT NULL,
  `in_house` int(11) NOT NULL,
  PRIMARY KEY (`history_id`),
  KEY `profile_id_fk` (`profile_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Profile`
--

CREATE TABLE IF NOT EXISTS `Profile` (
  `profile_id` int(11) NOT NULL AUTO_INCREMENT,
  `rfid_id` int(11) NOT NULL,
  `name` varchar(70) NOT NULL,
  `birthday` date NOT NULL,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `bmi` float DEFAULT NULL,
  `in_house` tinyint(1) NOT NULL,
  PRIMARY KEY (`profile_id`),
  KEY `rfid_id_fk` (`rfid_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `RFID`
--

CREATE TABLE IF NOT EXISTS `RFID` (
  `rfid_id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(15) NOT NULL,
  PRIMARY KEY (`rfid_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Settings`
--

CREATE TABLE IF NOT EXISTS `Settings` (
  `settings_id` int(11) NOT NULL AUTO_INCREMENT,
  `door_height` float NOT NULL DEFAULT 210,
  `distance_in_detection` float NOT NULL DEFAULT 50,
  `distance_out_detection` float NOT NULL DEFAULT 50,
  `time_close` int(11) NOT NULL DEFAULT 5,
  `time_detection` int(11) NOT NULL DEFAULT 10,
  `time_face_detection` int(11) NOT NULL DEFAULT 10,
  PRIMARY KEY (`settings_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Stranger`
--

CREATE TABLE IF NOT EXISTS `Stranger` (
  `stranger_id` int(11) NOT NULL AUTO_INCREMENT,
  `time` time NOT NULL DEFAULT current_timestamp(),
  `date` date NOT NULL DEFAULT current_timestamp(),
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`stranger_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `History`
--
ALTER TABLE `History`
  ADD CONSTRAINT `History_ibfk_1` FOREIGN KEY (`profile_id`) REFERENCES `Profile` (`profile_id`);

--
-- Constraints for table `Profile`
--
ALTER TABLE `Profile`
  ADD CONSTRAINT `Profile_ibfk_1` FOREIGN KEY (`rfid_id`) REFERENCES `RFID` (`rfid_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
