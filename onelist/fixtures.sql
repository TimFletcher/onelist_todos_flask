# Sequel Pro dump
# Version 2492
# http://code.google.com/p/sequel-pro
#
# Host: localhost (MySQL 5.1.51)
# Database: onelist
# Generation Time: 2011-04-22 18:23:15 -0600
# ************************************************************

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- DROP TABLE IF EXISTS `accounts_user`;
-- 
-- CREATE TABLE `accounts_user` (
--   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
--   `email` varchar(100) NOT NULL,
--   `password` varchar(60) NOT NULL,
--   `first_name` varchar(50) DEFAULT '',
--   `last_name` char(50) DEFAULT '',
--   `is_active` binary(1) NOT NULL DEFAULT '1',
--   PRIMARY KEY (`id`)
-- ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` (`id`,`email`,`password`,`first_name`,`last_name`,`is_active`)
VALUES
	(1,'test@test.com','sha1$huj9heME$8653756aaed11fdbfce799d27644866efa291efd','Tim','Fletcher',X'31'),
	(2,'foo@bar.com','sha1$LhTlGkh5$148eb8d3056362ebfff421357120903db473930d','Ben','Holden',X'31');

/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;



LOCK TABLES `lists_list` WRITE;
/*!40000 ALTER TABLE `lists_list` DISABLE KEYS */;
INSERT INTO `lists_list` (`id`,`user_id`,`hash`)
VALUES
	(1,1,'68813d67bbb8e184f1395355ca22d39421f6f8b2'),
	(2,2,'20bcb790799c3e069c60c8da7fe44dcf16893af0');

/*!40000 ALTER TABLE `lists_list` ENABLE KEYS */;
UNLOCK TABLES;



LOCK TABLES `lists_listitem` WRITE;
/*!40000 ALTER TABLE `lists_listitem` DISABLE KEYS */;
INSERT INTO `lists_listitem` (`id`,`list_id`,`text`,`complete`)
VALUES
  (1,1,'Take cat to vet',0),
  (2,1,'Clean house',0),
  (3,1,'Buy birthday card for sis',0),
  (4,1,'Go to gym',0),
  (5,2,'Take bike to shop',0),
  (6,2,'Buy flowers',0),
  (7,2,'Take dog out for a walk',0),
  (8,2,'Fix sink',0);
/*!40000 ALTER TABLE `lists_listitem` ENABLE KEYS */;
UNLOCK TABLES;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;