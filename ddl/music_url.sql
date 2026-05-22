/*
 Navicat Premium Dump SQL

 Source Server         : cloud-music
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 23/05/2026 06:20:59
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for music_url
-- ----------------------------
DROP TABLE IF EXISTS "music_url";
CREATE TABLE "music_url" (
  "music_id" integer NOT NULL,
  "quality" text NOT NULL,
  "url" text,
  PRIMARY KEY ("music_id", "quality")
);

PRAGMA foreign_keys = true;
