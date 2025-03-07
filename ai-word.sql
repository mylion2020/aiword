/*
Navicat MySQL Data Transfer

Source Server         : aiword
Source Server Version : 50744
Source Host           : localhost:3306
Source Database       : ai-word

Target Server Type    : MYSQL
Target Server Version : 50744
File Encoding         : 65001

Date: 2025-02-27 12:11:42
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for book
-- ----------------------------
DROP TABLE IF EXISTS `book`;
CREATE TABLE `book` (
  `book_id` int(11) NOT NULL AUTO_INCREMENT,
  `book_name` varchar(256) NOT NULL,
  `stage` varchar(20) DEFAULT NULL,
  `owner` int(11) DEFAULT NULL,
  PRIMARY KEY (`book_id`),
  KEY `book_book_id_IDX` (`book_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='词书记录表';

-- ----------------------------
-- Table structure for book_word
-- ----------------------------
DROP TABLE IF EXISTS `book_word`;
CREATE TABLE `book_word` (
  `book_id` int(11) NOT NULL DEFAULT '0' COMMENT '单词所属词书的id',
  `word` varchar(100) NOT NULL COMMENT 'word',
  `mean` varchar(100) DEFAULT NULL COMMENT '在本词书的含义',
  KEY `book_word_book_id_IDX` (`book_id`) USING BTREE,
  CONSTRAINT `book_word_book_FK` FOREIGN KEY (`book_id`) REFERENCES `book` (`book_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='书籍单词记录表';

-- ----------------------------
-- Table structure for log
-- ----------------------------
DROP TABLE IF EXISTS `log`;
CREATE TABLE `log` (
  `date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `user_id` int(11) NOT NULL,
  KEY `log_date_IDX` (`date`) USING BTREE,
  KEY `log_user_FK` (`user_id`),
  CONSTRAINT `log_user_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='日志表';

-- ----------------------------
-- Table structure for plan
-- ----------------------------
DROP TABLE IF EXISTS `plan`;
CREATE TABLE `plan` (
  `book_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `new_word` int(11) NOT NULL,
  `review` int(11) DEFAULT NULL,
  KEY `plan_user_id_IDX` (`user_id`) USING BTREE,
  KEY `plan_book_FK` (`book_id`),
  CONSTRAINT `plan_book_FK` FOREIGN KEY (`book_id`) REFERENCES `book` (`book_id`),
  CONSTRAINT `plan_user_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='学习计划表';

-- ----------------------------
-- Table structure for system
-- ----------------------------
DROP TABLE IF EXISTS `system`;
CREATE TABLE `system` (
  `set_name` char(20) NOT NULL,
  `set_value` json DEFAULT NULL,
  PRIMARY KEY (`set_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='系统参数';

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `phone` varchar(11) NOT NULL,
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(20) NOT NULL,
  `birthday` date DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `avator` varchar(255) DEFAULT NULL,
  `openid` varchar(50) DEFAULT NULL,
  `owner` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='用户表';

-- ----------------------------
-- Table structure for user_word
-- ----------------------------
DROP TABLE IF EXISTS `user_word`;
CREATE TABLE `user_word` (
  `user_id` int(11) NOT NULL COMMENT '单词学习记录所属用户id',
  `rem_rank` int(11) NOT NULL DEFAULT '0' COMMENT '熟悉程度等级（0最低，5最高）',
  `learn_date` date NOT NULL COMMENT '学习时间或筛选加入时间',
  `word` varchar(100) NOT NULL COMMENT '单词',
  `status` tinyint(2) NOT NULL COMMENT '单词所属状态。1.新学；2.复习；3.掌握',
  `note` varchar(255) DEFAULT NULL COMMENT '用户对单词的备注',
  `review_count` int(11) DEFAULT NULL COMMENT '复习次数',
  `error_count` int(11) DEFAULT NULL COMMENT '做错次数',
  `review_date` date DEFAULT NULL COMMENT '最近一次复习日期',
  `review_plan` date DEFAULT NULL COMMENT '下次复习时间',
  `detail` varchar(255) DEFAULT NULL COMMENT '系统考虑要记录的一些细节',
  KEY `user_word_user_id_IDX` (`user_id`) USING BTREE,
  CONSTRAINT `user_word_user_FK` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户单词学习记录表';

-- ----------------------------
-- Table structure for word_list
-- ----------------------------
DROP TABLE IF EXISTS `word_list`;
CREATE TABLE `word_list` (
  `audio` varchar(255) DEFAULT NULL,
  `bnc` varchar(255) DEFAULT NULL,
  `collins` varchar(255) DEFAULT NULL,
  `definition` text,
  `detail` varchar(255) DEFAULT NULL,
  `exchange` varchar(255) DEFAULT NULL,
  `frq` varchar(255) DEFAULT NULL,
  `oxford` varchar(255) DEFAULT NULL,
  `phonetic` varchar(255) DEFAULT NULL,
  `pos` varchar(255) DEFAULT NULL,
  `tag` varchar(255) DEFAULT NULL,
  `translation` varchar(255) DEFAULT NULL,
  `word` varchar(255) DEFAULT NULL,
  KEY `word_list_word_IDX` (`word`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
