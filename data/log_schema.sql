-- ---
-- Globals
-- ---

-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

-- ---
-- Table 'mail'
-- 
-- ---

DROP TABLE IF EXISTS `mail`;
		
CREATE TABLE `mail` (
  `mid`			INTEGER,
  `peer`		CHAR(32)  NULL DEFAULT NULL,
  `mailfrom`		CHAR(64)  NULL DEFAULT NULL,
  `rcpttos`		CHAR(512)  NULL DEFAULT NULL,
  `data`		BLOB   NULL DEFAULT NULL,
  `timestamp`		TIMESTAMP  NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`mid`)
);

