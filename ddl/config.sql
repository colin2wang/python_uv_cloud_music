/*
 Navicat Premium Dump SQL

 Source Server         : cloud-music
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 23/05/2026 06:20:47
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for config
-- ----------------------------
DROP TABLE IF EXISTS "config";
CREATE TABLE "config" (
  "name" TEXT NOT NULL,
  "value" TEXT,
  PRIMARY KEY ("name")
);

PRAGMA foreign_keys = true;
