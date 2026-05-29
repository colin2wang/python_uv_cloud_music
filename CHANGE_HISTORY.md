# Change History

This document records all significant changes to the Music Library Organizer project, organized by date in reverse chronological order.

---

## Update Rules

### Documentation Guidelines
- Each daily entry must not exceed 200 words
- Use concise English descriptions focusing on key changes
- List modified files when relevant
- Highlight new features, bug fixes, and improvements separately
- Maintain reverse chronological order (newest first)
- Use clear section headers with dates
- Avoid redundant details; focus on impact and functionality
- Group related changes under unified headings
- Preserve technical accuracy while ensuring readability

---

## 2026-05-27

### Import Structure Refactoring in Interactive Download Script

Reorganized import statements in `interactive_process.py` to use modular utility modules. Moved download functions (`download_song`, `download_album`, `download_playlist`) from `process_cloud_music.py` to newly created `util_music_downloader.py`. Removed unused imports including duplicate `sys` and `pathlib.Path`. Improved code organization and separation of concerns by isolating download functionality into dedicated utility module. Modified files: `interactive_process.py`.

---

### Method Renaming for Metadata Interval Control

Renamed download interval related methods to better reflect their actual usage for metadata fetching. Changed `download_interval` configuration to `get_metadata_interval` in `config.yml`. Renamed `ensure_download_interval()` → `ensure_get_metadata_interval()`, `finish_download()` → `finish_get_metadata()`, and `get_download_interval()` → `get_get_metadata_interval()`. Updated database timestamp key from `last_download_timestamp` to `last_get_metadata_timestamp`. Modified files: `config.yml`, `util_config.py`, `util_commons.py`, `util_music_downloader.py`, `util_music_metadata.py`.

---

## 2026-05-25

### Code Quality Improvements

Updated song ID format in test script and reorganized logging output. Changed default song ID from numeric `26427662` to string `"1832966854"` for consistency. Reordered logging statements in main block for better readability. Updated `.gitignore` to exclude AI plugin cache directory (`.proxyai/`). Modified files: `tool_next_music_v2.py`, `.gitignore`.

---

## 2026-05-24

### Database Initialization Optimization

Optimized database initialization logic to avoid unnecessary table recreation on every run. Implemented conditional check in `MusicDB.__init__()` to only create tables when the database file doesn't exist. Prevents potential data loss and improves startup performance by skipping redundant DDL operations. Modified files: `util_database.py`.

---

## 2026-05-23

### Music Library Models & Database Management Utilities

Added comprehensive music library models and database management utilities. Created `model` package with basic and extra models including `Config`, `MusicInfo`, `MusicURL`, `AlbumMetadata`, `SongMetadata`, and `PlaylistMetadata` classes. Added DDL scripts for `config`, `music_info`, and `music_url` tables in ddl/ directory. Implemented `MusicDB` class for database operations including upsert, query, and config management. Enhanced database interaction across multiple modules with proper connection handling. Updated `util_database.py` with comprehensive database management functions. Modified files: `model/`, `ddl/`, `util_database.py`, `util_commons.py`, `util_config.py`, `interactive_process.py`, `process_cloud_music.py`, `tool_next_music_v1.py`, `tool_next_music_v2.py`, and several process scripts.

---

### Download Interval Control Enhancement

Enhanced download interval control mechanism with database-based timestamp storage. Updated `ensure_download_interval()` and `update_last_download_timestamp()` functions to use database instead of file-based storage for last download timestamps. Implemented proper database connection handling with `MusicDB` instance in `util_commons.py`. Added `get_download_interval()` method in `util_config.py` with default 30-second interval. Improved error handling for timestamp parsing and database operations. Ensures more reliable interval enforcement between downloads to prevent API rate limiting. Modified files: `util_commons.py`, `util_config.py`, `process_cloud_music.py`.

---

### API Call Optimization

Optimized API call execution by moving `api.parse_song()` call from general execution flow to the else block of `config.should_use_next_music_tool()` condition. This prevents unnecessary API calls when Next Music Tool is enabled, improving efficiency and reducing API usage. When Next Music Tool is configured, the application now bypasses the original API call entirely, relying solely on Next Music Tool data. When Next Music Tool is disabled, the original API call executes as before. Modified file: `process_cloud_music.py`.

## 2026-05-21

### Album Artist Tag & Filename Fixer

Created `process_album_artist_fix.py` for batch fixing artist tags and filenames in album folders. Detects '/' separator in artist tags and converts to array format with ', ' delimiter. Rebuilds filenames based on corrected artist information following standard naming rules: "{index} - {artist} - {song_name}" or "{artist} - {song_name}". Intelligently parses original filenames to extract song name and track index, then reconstructs with proper artist formatting. Handles both '/' and '_' separators in filenames while preserving other underscores in song titles. Operates independently without API calls or CMUSIC_ID checks. Modified files: `process_album_artist_fix.py`, `process_cloud_music.py` (fixed NoneType error in ar_name handling).

---

### Download Interval Control Implementation

Implemented download interval control mechanism to prevent API rate limiting. Added `download_interval` configuration (default: 30s) in `config.yml`. Created `ensure_download_interval()` function that checks `last_download.txt` timestamp and waits if necessary to maintain configured interval between downloads. Added `update_last_download_timestamp()` function to record completion time after each download. Refactored waiting logic to reuse existing `random_sleep()` method for consistency. Modified `download_song_and_resources()` to call interval check at start and update timestamp at end. Ensures minimum 30-second gap between consecutive downloads. Modified files: `config.yml`, `config_manager.py`, `utils.py`, `process_cloud_music.py`.

---

### NextMusic API Response Caching & Enhanced Logging

Implemented caching mechanism for NextMusicTool API calls during retry loops. Added `next_music_cache` dictionary to store responses from `get_song_info`, `get_song_url`, and `get_song_lyric`. Prevents redundant API calls when retrying due to quality mismatch or temporary failures. Cache automatically invalidates on failure to ensure fresh data. Enhanced logging shows "Fetching..." on first call and "✅ Cache hit" with details when reusing cached responses. Significantly reduces API load and improves retry efficiency. Modified `process_cloud_music.py` to add caching logic with comprehensive logging.

---

### Random Sleep Enhancement with Progress Bar

Enhanced `random_sleep()` function with visual progress bar using tqdm. Real-time countdown display during API rate limiting delays shows elapsed time, remaining time, and completion percentage. Displays reason for waiting (e.g., "Between processing songs", "API retry"). Replaced all `time.sleep()` calls with `random_sleep()` across codebase including `process_album_lyrics_fix.py` and `tool_next_music_v2.py`. Ensures consistent rate limiting behavior throughout application. Supports both fixed delays and random ranges. Every wait operation logs its purpose for better debugging. Improves user experience during rate limiting periods with clear visual feedback.

---

## 2026-05-19

### Enhanced Rate Limiting & 429 Error Handling

Enhanced `random_sleep` function with `min_delay` parameter (default: 1.0s) for flexible delay control. Implemented comprehensive 429 error handling across all API calls including metadata requests, music/cover downloads, and NextMusic API methods. Smart error detection identifies 429 errors through HTTP status codes and response content analysis. 429 errors trigger 10-15 second random delays; other transient errors use 10-20 second delays with automatic retry. Enhanced warning-level logging with descriptive reason strings for easy identification of rate limiting events. Modified `utils.py` and `process_cloud_music.py`. Prevents API bans and improves download success rates during high-load periods.

---

## 2026-05-18

### Download Progress Bar Implementation

Added visual progress bar for music file downloads using tqdm. Real-time download progress display shows percentage completion, downloaded size vs total size with automatic unit scaling (KB/MB), download speed, and estimated time remaining. Progress bar description includes song index and filename. Graceful fallback when file size is unavailable from server. Enhanced user experience during batch downloads. Added `tqdm>=4.66.0` package dependency.

---

## 2026-05-17

### Interactive Mode Enhancements & Download Statistics

Added comprehensive user action logging in `interactive_process.py` for download method selection, input parameters, track index selections, and continue/exit decisions. Implemented download statistics grouped by file extension (MP3, FLAC, M4A, etc.) using `_count_downloaded_songs()` function. Only counts audio files, excludes lyrics and cover images. Fixed indexes configuration issue where saved track indexes were not used as defaults for album and playlist downloads. Updated `scripts/cloud-music.cmd` with `--help`, `--folder-only`, and `--git-pull` parameters. Fixed Cmder terminal compatibility by refactoring if blocks to goto labels to avoid command truncation errors with Chinese characters.

---

## 2026-05-13

### NextMusic AES-GCM Encryption Implementation

Complete implementation of encrypted API communication with AES-GCM encryption. Added `NextMusicToolV2` class supporting new encryption format with `_get_encryption_key`, `_encrypt_data`, and `_decrypt_data` methods. Fixed tag and ciphertext combination order in decryption logic. Added retry mechanism and random backoff strategy for network fluctuations. Integrated `cryptography` library dependency. Improved logging system replacing print outputs. Optimized return value type consistency and enhanced exception handling. Created comprehensive API documentation and test scripts. Resolved initial 400 error debugging issues and successfully integrated encryption with main download workflow.

---

## 2026-04-27

### Interactive Mode Enhancement & Progress Tracking

Added music total count in output logs for better tracking. Enhanced interactive method user interface and workflow. Updated README.md with latest features. Fixed re-run logic issues.

---

## 2026-04-24

### Interactive Download Interface

Added user-friendly interactive download method (`interactive_process.py`). Menu-driven interface for selecting download type (song/album/playlist). Guided input process with validation. Simplified user experience for non-technical users.

---

## 2026-04-17 to 2026-04-16

### Retry Logic Improvements

Fixed multiple retry-related issues. Improved reliability of failed request recovery. Better handling of temporary network failures. Enhanced error detection and retry triggers.

---

## 2026-04-14 to 2026-04-13

### NextMusicTool Integration

Replaced original URL resolution with NextMusicTool. Added configuration switch to enable/disable NextMusicTool usage. Fixed multiple retry issues during integration. Updated logging system for better debugging. Resolved various compatibility issues.

---

## 2026-04-08

### Smart Retry Mechanism

Added intelligent retry mechanism for API requests. Automatic retry on failed requests with configurable retry attempts. Improved resilience against temporary failures. Better error handling and recovery.

---

## 2026-04-06 to 2026-03-31

### Code Refactoring & Logging Optimization

Major refactoring across multiple modules. Removed unused imports in config and processing files. Optimized import module order. Renamed `process_from_folders.py` to Folder List Utility with English comments. Enhanced logging infrastructure with archived log management. Updated logging output methods for folder traversal. Improved log organization and rotation. Added album cover redownload functionality. Added `imagesize` package for efficient image resolution detection. Fixed album cover download issues.

---

## 2026-03-27 to 2026-03-22

### Utility Functions & Folder Processing

Moved common methods into `utils.py` for better code reuse. Added batch processing functions for existing music libraries with `process_with_folder` functionality. Automated metadata fixing for existing collections. Updated comments and improved documentation.

---

## 2026-03-21 to 2026-03-18

### Lyrics Processing Improvements

Fixed multiple lyrics-related issues. Check if lyrics already added to avoid duplicates. Skip files that are already fixed. Resolved "lyric not finished" issue. Improved lyrics parsing and embedding.

---

## 2026-03-14

### Metadata Writing Fixes

Fixed issue where metadata was not being appended to audio files. Ensured proper ID3 tag writing for MP3 files. Fixed Vorbis comments for FLAC files. Improved MP4 tag handling for M4A/AAC files.

---

## 2026-03-11 to 2026-03-10

### API Endpoint & Path Issues

Changed to different API site for better reliability. Fixed file path too long issue on Windows systems. Implemented intelligent filename truncation. Better handling of long artist/album names.

---

## 2026-03-08 to 2026-03-05

### Album Organization Enhancements

Added release date to album folder names and `album_info.txt` in format `Artist - Album Name (YYYY-MM-DD)` for better chronological organization. Removed emoji characters for better cross-platform compatibility. Updated album ID handling and storage.

---

## 2026-03-04 to 2026-03-03

### Configuration System & Documentation

Added YAML-based configuration system (`config.yml`, `config_manager.py`) for centralized configuration management. Easy customization without code changes supporting all major settings (API, download, metadata, network, logging). Created comprehensive README.md with installation instructions, usage examples, API reference, configuration guide, and troubleshooting section. Major code restructuring for better maintainability.

---

## 2026-03-01

### Playlist Support & Artist Tag Fixes

Added complete playlist download functionality with ability to extract all songs and support selective track downloads. Proper metadata handling for playlist tracks. Fixed artist tag issues in metadata writing with proper handling of multiple artists. Corrected ID3 TPE1 tag formatting. Improved artist name parsing.

---

## 2026-02-28

### Cover Art & Logging Updates

Updated cover page resolution to 320x320 for better quality. Major logging utility updates with structured logging format. Better log level management. Fixed logger initialization issues.

---

## 2026-02-26 to 2026-02-25

### Download Logic & Methods

Implemented core downloading functionality including audio file download with streaming, metadata extraction and embedding, cover art download and embedding, and lyrics retrieval and saving. Refined download methods for better performance. Added comprehensive logging throughout the application.

---

## 2026-02-24

### Project Initialization

Initial project setup and structure. Basic API client implementation. Core download functionality. Initial file structure. Dependency configuration.

---

**Note**: This project follows semantic versioning (SemVer). Version numbers follow the MAJOR.MINOR.PATCH format where:
- **MAJOR** version indicates incompatible API changes
- **MINOR** version indicates added functionality in a backward-compatible manner  
- **PATCH** version indicates backward-compatible bug fixes

For detailed commit history, see the git log or visit the repository.