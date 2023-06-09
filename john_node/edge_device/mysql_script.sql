CREATE DATABASE IF NOT EXISTS `smart_home`;
USE `smart_home`;

CREATE TABLE IF NOT EXISTS `appliance_status` (
    `appliance_id` int(11) NOT NULL,
    `appliance_name` varchar(255) NOT NULL,
    `status` INT NOT NULL,
    `status_value` INT DEFAULT NULL,
    `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`appliance_id`)
);

INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (1, 'Room 1 Light', 0);
INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (2, 'Corridor Light', 0);
INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (3, 'Room 2 Light', 0);
INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (4, 'Room 1 Aircon', 0);
INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (5, 'Room 2 Aircon', 0);
INSERT INTO `appliance_status` (appliance_id, appliance_name, status) VALUES (6, 'Ventilating Fan', 0);

CREATE TABLE IF NOT EXISTS `appliance_uptime` (
    `appliance_id` int(11) NOT NULL,
    `date` DATE NOT NULL,
    `uptime` INT NOT NULL,
    `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`appliance_id`, `date`),
    FOREIGN KEY (`appliance_id`) REFERENCES `appliance_status` (`appliance_id`)
);

DELIMITER //

CREATE TRIGGER update_uptime_trigger
AFTER UPDATE ON `appliance_status`
FOR EACH ROW
BEGIN
    IF OLD.status = 1 AND NEW.status = 0 THEN
        -- Calculate the time difference between `updated_on` and the current time
        SET @seconds_diff = TIMESTAMPDIFF(SECOND, OLD.updated_on, NOW());

        -- Get the current date and time
        SET @current_datetime = NOW();

        -- Check if the row exists for the current year and month
        SELECT COUNT(*) INTO @row_count
        FROM `appliance_uptime`
        WHERE `appliance_id` = NEW.appliance_id
        AND `date` = DATE(@current_datetime);

        IF @row_count > 0 THEN
            -- Update the existing row
            UPDATE `appliance_uptime`
            SET `uptime` = `uptime` + @seconds_diff
            WHERE `appliance_id` = NEW.appliance_id
            AND `date` = DATE(@current_datetime);
        ELSE
            -- Insert a new row
            INSERT INTO `appliance_uptime` (`appliance_id`, `date`, `uptime`)
            VALUES (NEW.appliance_id, @current_datetime, @seconds_diff);
        END IF;
    END IF;
END //

DELIMITER ;

CREATE TABLE IF NOT EXISTS `people_in_room` (
    `room_id` int(11) NOT NULL,
    `people_count` INT NOT NULL,
    `created_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`room_id`)
);

INSERT INTO `people_in_room` (room_id, people_count) VALUES (1, 0);
INSERT INTO `people_in_room` (room_id, people_count) VALUES (2, 0);