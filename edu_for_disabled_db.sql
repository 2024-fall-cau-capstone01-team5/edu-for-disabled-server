-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: edu_for_disabled
-- ------------------------------------------------------
-- Server version	8.0.40-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `answers`
--

DROP TABLE IF EXISTS `answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `answers` (
  `learning_log_id` int NOT NULL,
  `answer` varchar(50) NOT NULL,
  `question` varchar(100) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sceneId` varchar(30) NOT NULL,
  `hash_num` int NOT NULL AUTO_INCREMENT,
  `response` varchar(50) NOT NULL,
  PRIMARY KEY (`hash_num`),
  KEY `fk_learning_log_id` (`learning_log_id`),
  CONSTRAINT `fk_learning_log_id` FOREIGN KEY (`learning_log_id`) REFERENCES `learning_logs` (`learning_log_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1382 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `character`
--

DROP TABLE IF EXISTS `character`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character` (
  `user_id` varchar(20) NOT NULL,
  `profile_name` varchar(20) NOT NULL,
  `toggle` float DEFAULT NULL,
  `prop` float DEFAULT NULL,
  `eyeShape` float DEFAULT NULL,
  `bodyShape` float DEFAULT NULL,
  `bodyColor` float DEFAULT NULL,
  PRIMARY KEY (`user_id`,`profile_name`),
  CONSTRAINT `fk_profiles` FOREIGN KEY (`user_id`, `profile_name`) REFERENCES `profiles` (`user_id`, `profile_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `learning_list`
--

DROP TABLE IF EXISTS `learning_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `learning_list` (
  `user_id` varchar(20) NOT NULL,
  `profile_name` varchar(20) NOT NULL,
  `scenario_id` int NOT NULL,
  KEY `scenario_id` (`scenario_id`),
  KEY `fk_profile_user` (`user_id`,`profile_name`),
  KEY `fk_profile_name` (`profile_name`),
  CONSTRAINT `fk_profile_name` FOREIGN KEY (`profile_name`) REFERENCES `profiles` (`profile_name`) ON DELETE CASCADE,
  CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`, `profile_name`) REFERENCES `profiles` (`user_id`, `profile_name`) ON DELETE CASCADE,
  CONSTRAINT `learning_list_ibfk_1` FOREIGN KEY (`user_id`, `profile_name`) REFERENCES `profiles` (`user_id`, `profile_name`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `learning_list_ibfk_2` FOREIGN KEY (`scenario_id`) REFERENCES `scenario` (`scenario_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `learning_logs`
--

DROP TABLE IF EXISTS `learning_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `learning_logs` (
  `learning_log_id` int NOT NULL AUTO_INCREMENT,
  `scenario_id` int NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `profile_name` varchar(20) NOT NULL,
  `time` timestamp NOT NULL,
  PRIMARY KEY (`learning_log_id`),
  KEY `scenario_id` (`scenario_id`),
  KEY `learning_logs_ibfk_1` (`user_id`,`profile_name`),
  CONSTRAINT `learning_logs_ibfk_1` FOREIGN KEY (`user_id`, `profile_name`) REFERENCES `profiles` (`user_id`, `profile_name`) ON DELETE CASCADE,
  CONSTRAINT `learning_logs_ibfk_2` FOREIGN KEY (`scenario_id`) REFERENCES `scenario` (`scenario_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=515 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `learning_report`
--

DROP TABLE IF EXISTS `learning_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `learning_report` (
  `learning_log_id` int NOT NULL,
  `completed` varchar(100) NOT NULL,
  `agile` varchar(100) NOT NULL,
  `accuracy` varchar(100) NOT NULL,
  `context` varchar(100) NOT NULL,
  `pronunciation` varchar(100) NOT NULL,
  `review` varchar(300) NOT NULL,
  PRIMARY KEY (`learning_log_id`),
  CONSTRAINT `fk_learning_report_log_id` FOREIGN KEY (`learning_log_id`) REFERENCES `learning_logs` (`learning_log_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `profiles`
--

DROP TABLE IF EXISTS `profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles` (
  `user_id` varchar(20) NOT NULL,
  `profile_name` varchar(20) NOT NULL,
  `icon_url` varchar(50) NOT NULL,
  PRIMARY KEY (`user_id`,`profile_name`),
  UNIQUE KEY `profile_name` (`profile_name`),
  CONSTRAINT `profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scenario`
--

DROP TABLE IF EXISTS `scenario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scenario` (
  `scenario_id` int NOT NULL AUTO_INCREMENT,
  `title` varbinary(20) NOT NULL,
  `scene_cnt` int DEFAULT NULL,
  PRIMARY KEY (`scenario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statics`
--

DROP TABLE IF EXISTS `statics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statics` (
  `learning_log_id` int NOT NULL,
  `correct_response_cnt` int NOT NULL,
  `timeout_response_cnt` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`learning_log_id`),
  CONSTRAINT `statics_ibfk_1` FOREIGN KEY (`learning_log_id`) REFERENCES `learning_logs` (`learning_log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(20) NOT NULL,
  `password` varchar(60) NOT NULL,
  `user_name` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-10 18:19:34
