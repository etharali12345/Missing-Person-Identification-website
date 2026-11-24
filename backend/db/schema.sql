CREATE DATABASE IF NOT EXISTS `face_recognition_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE `face_recognition_db`;

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email_or_phone` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email_or_phone` (`email_or_phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `authority` (
  `authority_id` int(11) NOT NULL AUTO_INCREMENT,
  `authority_type` enum('service','organization') NOT NULL,
  `authority_name` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `document` varchar(255) DEFAULT NULL,
  `license_number` varchar(100) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`authority_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `missing_persons` (
  `missing_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `age` int(5) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `last_seen_location` varchar(255) DEFAULT NULL,
  `last_seen_date` date DEFAULT NULL,
  `phone_number1` varchar(20) NOT NULL,
  `phone_number2` varchar(20) DEFAULT NULL,
  `image_path` varchar(255) NOT NULL,
  `faiss_id` int(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`missing_id`),
  KEY `fk_missing_user` (`user_id`),
  CONSTRAINT `fk_missing_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `found_persons` (
  `found_id` int(11) NOT NULL AUTO_INCREMENT,
  `authority_id` int(11) DEFAULT NULL,
  `uploaded_by_admin_id` int(11) DEFAULT NULL,
  `full_name` varchar(150) DEFAULT NULL,
  `approximate_age` int(5) DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `found_location` varchar(255) DEFAULT NULL,
  `found_date` date DEFAULT NULL,
  `health_status` varchar(150) DEFAULT 'found',
  `phone_number1` varchar(20) NOT NULL,
  `phone_number2` varchar(20) DEFAULT NULL,
  `image_path` varchar(255) NOT NULL,
  `faiss_id` int(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`found_id`),
  KEY `fk_found_authority` (`authority_id`),
  KEY `fk_found_uploader` (`uploaded_by_admin_id`),
  CONSTRAINT `fk_found_authority` FOREIGN KEY (`authority_id`) REFERENCES `authority` (`authority_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_found_admin` FOREIGN KEY (`uploaded_by_admin_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `match_results` (
  `match_id` int(11) NOT NULL AUTO_INCREMENT,
  `missing_id` int(11) NOT NULL,
  `found_id` int(11) NOT NULL,
  `similarity_score` float NOT NULL,
  `status` enum('match','uncertain','no_match') DEFAULT 'uncertain',
  `match_date` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`match_id`),
  KEY `fk_match_missing` (`missing_id`),
  KEY `fk_match_found` (`found_id`),
  CONSTRAINT `fk_match_missing` FOREIGN KEY (`missing_id`) REFERENCES `missing_persons` (`missing_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_match_found` FOREIGN KEY (`found_id`) REFERENCES `found_persons` (`found_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
