-- ---
-- Globals
-- ---

-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

-- ---
-- Table 'user'
-- 
-- ---

DROP TABLE IF EXISTS `user`;
		
CREATE TABLE `user` (
  `uid`			INTEGER,
  `username`		CHAR(64)  NULL UNIQUE DEFAULT NULL,
  `spwd`		CHAR(92)  NULL DEFAULT NULL,
  `fwdaddr`		CHAR(320) NULL UNIQUE DEFAULT NULL,
  `salt`		CHAR(64)  NULL DEFAULT NULL,
  `hashcellphone`	CHAR(128) NULL DEFAULT NULL,
  `retrievalkey`	CHAR(64)  NULL DEFAULT NULL,
  `timecreated`		TIMESTAMP NULL DEFAULT NULL,
  `status`		INTEGER   NULL DEFAULT NULL,
  PRIMARY KEY (`uid`)
);

-- ---
-- Table 'verification'
-- 
-- ---

DROP TABLE IF EXISTS `verification`;
		
CREATE TABLE `verification` (
  `vid`		INTEGER,
  `uid`		INTEGER   NULL UNIQUE DEFAULT NULL,
  `veristring`	CHAR(32)  NULL UNIQUE DEFAULT NULL,
  `timecreated`	TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`vid`),
  FOREIGN KEY (`uid`) REFERENCES `user` (`uid`)
);

-- ---
-- Table 'alias'
-- 
-- ---

DROP TABLE IF EXISTS `alias`;
		
CREATE TABLE `alias` (
  `aid`		INTEGER,
  `uid`		INTEGER  NULL DEFAULT NULL,
  `aliasname`	CHAR(64) NULL UNIQUE DEFAULT NULL,
  PRIMARY KEY (`aid`),
  FOREIGN KEY (`uid`) REFERENCES `user` (`uid`)
);

-- ---
-- Table 'aliasrnd'
-- 
-- ---

DROP TABLE IF EXISTS `aliasrnd`;
		
CREATE TABLE `aliasrnd` (
  `rid`		INTEGER,
  `uid`		INTEGER  NULL DEFAULT NULL,
  `aid`		INTEGER  NULL DEFAULT NULL,
  `aliasname`	CHAR(64) NULL DEFAULT NULL,
  `aliasrand`	INTEGER  NULL DEFAULT NULL,
  `isactive`	BOOLEAN  NULL DEFAULT NULL,
  PRIMARY KEY (`rid`),
  UNIQUE (`aliasname`, `aliasrand`),
  FOREIGN KEY (`uid`) REFERENCES `user` (`uid`),
  FOREIGN KEY (`aid`) REFERENCES `alias` (`aid`)
);

-- ---
-- Table 'history'
-- 
-- ---

DROP TABLE IF EXISTS `history`;
		
CREATE TABLE `history` (
  `hid`		INTEGER,
  `rid`		INTEGER   NULL DEFAULT NULL,
  `issender`	BOOLEAN   NULL DEFAULT NULL,
  `cid`		INTEGER   NULL DEFAULT NULL,
  `timestamp`	TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`hid`),
  FOREIGN KEY (`rid`) REFERENCES `aliasrnd` (`rid`),
  FOREIGN KEY (`cid`) REFERENCES `contact` (`cid`)
);

-- ---
-- Table 'contact'
-- 
-- ---

DROP TABLE IF EXISTS `contact`;
		
CREATE TABLE `contact` (
  `cid`		INTEGER,
  `hashcontact`	CHAR(128) NULL DEFAULT NULL,
  `missed`	INTEGER	  NULL DEFAULT NULL,
  `isblocked`	BOOLEAN	  NULL DEFAULT NULL,
  `ishuman`	ENUM	  NULL DEFAULT NULL,
  PRIMARY KEY (`cid`)
);

-- ---
-- Foreign Keys 
-- ---

-- ALTER TABLE `alias`		ADD CONSTRAINT `fk_alias_user` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);
-- ALTER TABLE `verification`	ADD CONSTRAINT `fk_verification_user` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);
-- ALTER TABLE `aliasrnd`	ADD CONSTRAINT `fk_aliasrnd_user` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);
-- ALTER TABLE `aliasrnd`	ADD CONSTRAINT `fk_aliasrnd_alias` FOREIGN KEY (`aid`) REFERENCES `alias` (`aid`);
-- ALTER TABLE `history`	ADD CONSTRAINT `fk_history_aliasrnd` FOREIGN KEY (`rid`) REFERENCES `aliasrnd` (`rid`);
-- ALTER TABLE `history`	ADD CONSTRAINT `fk_history_contact` FOREIGN KEY (`cid`) REFERENCES `contact` (`cid`);

-- ---
-- Table Properties
-- ---

-- ALTER TABLE `user`		ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `verification`	ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `alias`		ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `aliasrnd`	ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `history`	ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `contact`	ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ---
-- Test Data
-- ---

-- INSERT INTO `user` (`uid`, `username`, `spwd`, `fwdaddr`, `salt`, `hashcellphone`, `retrievalkey`, `timecreated`, `status`) VALUES
-- ('', '', '', '', '', '', '', '', '');
-- INSERT INTO `verification` (`vid`, `uid`, `veristring`, `timecreated`) VALUES
-- ('', '', '', '');
-- INSERT INTO `alias` (`aid`, `aliasname`, `isactive`) VALUES
-- ('', '', '');
-- INSERT INTO `aliasrnd` (`rid`, `uid`, `aid`, `aliasname`, `aliasrand`, `isactive`) VALUES
-- ('', '', '', '', '', '');
-- INSERT INTO `history` (`hid`, `rid`, `issender`, `cid`, `timestamp`) VALUES
-- ('', '', '', '', '');
-- INSERT INTO `contact` (`cid`, `hashcontact`, `missed`, `isblocked`, `ishuman`) VALUES
-- ('', '', '', '', '');

