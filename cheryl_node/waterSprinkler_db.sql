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
-- Database: `waterSprinkler_db`
--
CREATE DATABASE IF NOT EXISTS `waterSprinkler_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `waterSprinkler_db`;

-- --------------------------------------------------------

--
-- Table structure for table `systemData`
--

CREATE TABLE IF NOT EXISTS `systemData` (
  `dataID` int(10) NOT NULL AUTO_INCREMENT,
  `temperature` int(5) NOT NULL,
  `tempStatus` varchar(50) NOT NULL,
  `wetness` int(10) NOT NULL,
  `wetStatus` varchar(50) NOT NULL,
  `brightness` int(5) NOT NULL,
  `timeOfDay` varchar(50) NOT NULL,
  `sprinklerStatus` varchar(50) NOT NULL,
  PRIMARY KEY (`dataID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
