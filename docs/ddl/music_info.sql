/*
 Navicat Premium Dump SQL

 Source Server         : cloud-music
 Source Server Type    : SQLite
 Source Server Version : 3045000 (3.45.0)
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3045000 (3.45.0)
 File Encoding         : 65001

 Date: 23/05/2026 06:32:19
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for music_info
-- ----------------------------
DROP TABLE IF EXISTS "music_info";
CREATE TABLE "music_info" (
  "music_id" integer NOT NULL,
  "artists" text,
  "title" text,
  "album_name" text,
  "cover_url" text,
  "lyrics" text,
  "duration" integer,
  PRIMARY KEY ("music_id")
);

PRAGMA foreign_keys = true;
