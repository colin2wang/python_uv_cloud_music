# Change History

This document records all significant changes to the Music Library Organizer project, organized by date in reverse chronological order.

---

## 2026-05-21

### Random Sleep Enhancement with Progress Bar

#### New Features
- **Progress Bar for Wait Times**: Enhanced `random_sleep()` function with visual progress bar using `tqdm`
  - Real-time countdown display during API rate limiting delays
  - Shows elapsed time, remaining time, and completion percentage
  - Displays reason for waiting (e.g., "Between processing songs", "API retry")
  - Updates every 0.1 seconds for smooth progress visualization
  - Maintains precise delay timing while providing user feedback

#### Code Standardization
- **Unified Sleep Mechanism**: Replaced all `time.sleep()` calls with `random_sleep()` across the codebase
  - `process_album_lyrics_fix.py`: Converted 2 fixed-delay waits to use `random_sleep()`
  - `tool_next_music_v2.py`: Converted 3 retry delays to use `random_sleep()` with appropriate ranges
  - Ensures consistent rate limiting behavior throughout the application
  - All waits now show progress bars and include descriptive reason strings

#### Implementation Details
- **Backward Compatibility**: Maintained existing API with optional `min_delay` parameter
- **Flexible Configuration**: Supports both fixed delays (min=max) and random ranges
- **Enhanced Logging**: Every wait operation logs its purpose for better debugging
- **User Experience**: Visual progress feedback reduces uncertainty during long waits

#### Files Modified
- `utils.py`: Enhanced `random_sleep()` with tqdm progress bar integration
- `process_album_lyrics_fix.py`: Replaced `time.sleep()` calls with `random_sleep()`
- `tool_next_music_v2.py`: Replaced `time.sleep()` calls with `random_sleep()`

#### Benefits
Improved user experience during rate limiting periods, consistent wait behavior across all modules, better observability of delay reasons, and maintains compliance with API rate limiting policies through unified control

---

## 2026-05-19

### Enhanced Rate Limiting & 429 Error Handling

#### New Features
- **Enhanced `random_sleep` Function**: Added `min_delay` parameter (default: 1.0s) for flexible delay control while maintaining backward compatibility

- **Comprehensive 429 Error Handling**: Implemented rate limit detection and recovery across all API calls including metadata requests, music/cover downloads, and NextMusic API methods (`get_song_info`, `get_song_lyric`, `get_song_url`)

#### Implementation Details
- **Smart Error Detection**: Identifies 429 errors through HTTP status codes and response content analysis ("429 Too Many Requests")

- **Intelligent Retry Strategy**: 429 errors trigger 10-15 second random delays; other transient errors use existing 10-20 second delays with automatic retry

- **Enhanced Logging**: Warning-level logs with descriptive reason strings for easy identification of rate limiting events

#### Files Modified
- `utils.py`: Enhanced `random_sleep()` function
- `process_cloud_music.py`: Added 429 handling in metadata retrieval and all download operations

#### Benefits
Prevents API bans, improves download success rates during high-load periods, provides automatic recovery, and maintains compliance with API rate limiting policies

---

## 2026-05-18

### Download Progress Bar Implementation

#### New Features
- **Download Progress Bar**: Added visual progress bar for music file downloads using `tqdm`
  - Real-time download progress display with percentage completion
  - Shows downloaded size vs total size with automatic unit scaling (KB/MB)
  - Displays download speed and estimated time remaining
  - Includes song index and filename in progress bar description
  - Graceful fallback when file size is unavailable from server
  - Enhanced user experience during batch downloads

#### Dependencies
- Added `tqdm>=4.66.0` package for progress bar functionality

---

## 2026-05-17

### Interactive Mode Enhancements & Download Statistics

#### New Features
- **User Action Logging**: Added comprehensive logging for all user interactions in `interactive_process.py`
  - Download method selection (song/album/playlist) with descriptive names
  - Input parameters logging (IDs, quality settings)
  - Track index selections and parsing results with input/output tracking
  - Continue/exit decisions for session tracking
  - Enhanced debugging and troubleshooting capabilities through detailed logs

- **Download Statistics**: Added download statistics grouped by file extension
  - Implemented `_count_downloaded_songs()` function to scan and count audio files by format
  - Supports multiple formats: MP3, FLAC, M4A, AAC, WAV, OGG, WMA, MP2, MP1
  - Only counts audio files, excludes lyrics (.lrc) and cover image files
  - Displays statistics after album and playlist downloads complete
  - Shows formatted output with per-extension counts and total summary

#### Bug Fixes
- **Indexes Configuration**: Fixed issue where saved track indexes were not being used as defaults
  - Album download now properly loads and suggests previous indexes as default input
  - Playlist download now properly loads and suggests previous indexes as default input
  - Users can press Enter to reuse last selected tracks without re-typing
  - Improved user experience for repeated downloads of same content
  - Better handling of empty indexes list conversion to string format

### Startup Script Enhancements

#### New Features
- **Enhanced Command-Line Interface**: Updated `scripts/cloud-music.cmd` with advanced parameter support
  - Added `--help` parameter to display comprehensive usage information
  - Added `--folder-only` parameter to switch to project directory only, skipping all subsequent steps
  - Renamed `--git` to `--git-pull` with support for specifying remote source
  - Default remote source is "origin", can be customized via second parameter
  - Improved user experience with clear help documentation and examples

#### Bug Fixes
- **Cmder/Terminal Compatibility**: Fixed command parsing issues in Cmder and other terminal emulators
  - **Problem**: Using `if` statement blocks with parentheses caused command truncation errors (`'cho' is not recognized`)
  - **Root Cause**: Multi-line `if` blocks with Chinese characters triggered encoding and parsing issues in Cmder
  - **Solution**: Refactored script to use `goto` labels instead of `if` blocks for parameter handling
  - Removed problematic commands: `chcp 65001 >nul`, `setlocal enabledelayedexpansion`, `cls`
  - Used English-only text to avoid character encoding issues
  - Added error suppression (`2>nul`) to `cd /d` command for cleaner output
  - All parameters are now checked before directory changes to prevent context issues

#### Usage Examples
- `cloud-music.cmd` - Normal operation: open download folder and start script
- `cloud-music.cmd --help` - Display help information
- `cloud-music.cmd --folder-only` - Only switch to project directory
- `cloud-music.cmd --git-pull` - Pull from default remote (origin)
- `cloud-music.cmd --git-pull upstream` - Pull from specified remote source

---

## 2026-05-13

### NextMusic AES-GCM Encryption Implementation

**Commits:** `1b0fab4`, `0398646`, `abc4bd6`

#### Major Features
- **NextMusicTool V2 with AES-GCM Encryption**: Complete implementation of encrypted API communication
  - Added `NextMusicToolV2` class to support the new AES-GCM encryption format
  - Implemented `_get_encryption_key`, `_encrypt_data`, and `_decrypt_data` methods
  - Fixed the order of tag and ciphertext combination in decryption logic (ciphertext + tag)
  
- **Enhanced Security & Reliability**
  - Added retry mechanism and random backoff strategy to handle network fluctuations
  - Integrated `cryptography` library dependency
  - Improved logging system to replace original print outputs
  - Optimized return value type consistency and enhanced exception handling

- **API Integration Progress**
  - Created comprehensive API documentation and test scripts
  - Resolved initial "Invalid session or payload" (400 error) debugging issues
  - Successfully integrated encryption with main download workflow

---

## 2026-04-27

### Interactive Mode Enhancement & Progress Tracking

**Commits:** `d7ad1a5`, `4bf4fed`, `f1034fe`, `612788b`

#### Improvements
- **Progress Display**: Added music total count in output logs for better tracking
- **Interactive Method Updates**: Enhanced user interface and workflow
- **Documentation**: Updated README.md with latest features
- **Bug Fixes**: Fixed re-run logic issues

---

## 2026-04-24

### Interactive Download Interface

**Commit:** `ba5cbbf`

#### New Feature
- **Interactive Mode**: Added user-friendly interactive download method (`interactive_process.py`)
  - Menu-driven interface for selecting download type (song/album/playlist)
  - Guided input process with validation
  - Simplified user experience for non-technical users

---

## 2026-04-17 to 2026-04-16

### Retry Logic Improvements

**Commits:** `b3c30f6`, `f870335`

#### Bug Fixes
- **Retry Mechanism**: Fixed multiple retry-related issues
  - Improved reliability of failed request recovery
  - Better handling of temporary network failures
  - Enhanced error detection and retry triggers

---

## 2026-04-14 to 2026-04-13

### NextMusicTool Integration

**Commits:** `d21eb08`, `df37c74`, `85f48ac`, `dcc9948`, `4b1dd26`, `9a036ff`, `6307880`, `9177638`, `3d7f1cd`

#### Major Integration
- **NextMusicTool Replacement**: Replaced original URL resolution with NextMusicTool
  - Added configuration switch to enable/disable NextMusicTool usage
  - Fixed multiple retry issues during integration
  - Updated logging system for better debugging
  - Resolved various compatibility issues

---

## 2026-04-08

### Smart Retry Mechanism

**Commits:** `c48b0c5`, `376f0d9`, `7652391`

#### New Feature
- **Retry Logic**: Added intelligent retry mechanism for API requests
  - Automatic retry on failed requests
  - Configurable retry attempts
  - Improved resilience against temporary failures
  - Better error handling and recovery

---

## 2026-04-06 to 2026-03-31

### Code Refactoring & Logging Optimization

**Commits:** `7149948`, `3e5e25b`, `43bfb6a`, `eedc5e0`, `56cc89b`, `7e33516`

#### Refactoring
- **Code Structure**: Major refactoring across multiple modules
  - Removed unused imports in `config_manager.py`, `process_album_lyrics_fix.py`, `process_album_metadata_fix.py`
  - Optimized import module order in `process_cloud_music.py`
  - Renamed `process_from_folders.py` to Folder List Utility with English comments
  
- **Logging System**: Enhanced logging infrastructure
  - Added archived log management
  - Updated logging output methods for folder traversal
  - Improved log organization and rotation

- **New Utilities**: Added album cover redownload functionality
- **Dependencies**: Added `imagesize` package for efficient image resolution detection
- **Bug Fixes**: Fixed album cover download issues

---

## 2026-03-27 to 2026-03-22

### Utility Functions & Folder Processing

**Commits:** `946b049`, `cd39536`, `e5446f3`, `7bcb7f6`

#### Enhancements
- **Common Utilities**: Moved common methods into `utils.py` for better code reuse
- **Folder Processing**: Added batch processing functions for existing music libraries
  - `process_with_folder` functionality for bulk operations
  - Automated metadata fixing for existing collections
  - Comment updates and documentation improvements

---

## 2026-03-21 to 2026-03-18

### Lyrics Processing Improvements

**Commits:** `5ab2109`, `fda03b3`, `243c7e4`, `6440fa4`, `86a4786`

#### Bug Fixes
- **Lyrics Handling**: Fixed multiple lyrics-related issues
  - Check if lyrics already added to avoid duplicates
  - Skip files that are already fixed
  - Resolved "lyric not finished" issue
  - Improved lyrics parsing and embedding

---

## 2026-03-14

### Metadata Writing Fixes

**Commits:** `9d319d0`, `33ef11a`

#### Bug Fixes
- **Metadata Appending**: Fixed issue where metadata was not being appended to audio files
  - Ensured proper ID3 tag writing for MP3 files
  - Fixed Vorbis comments for FLAC files
  - Improved MP4 tag handling for M4A/AAC files

---

## 2026-03-11 to 2026-03-10

### API Endpoint & Path Issues

**Commits:** `271845f`, `e676e56`

#### Changes
- **API Endpoint**: Changed to different API site for better reliability
- **File Paths**: Fixed file path too long issue on Windows systems
  - Implemented intelligent filename truncation
  - Better handling of long artist/album names

---

## 2026-03-08 to 2026-03-05

### Album Organization Enhancements

**Commits:** `7a3f775`, `a9fd759`, `3bf750e`

#### Improvements
- **Release Dates**: Added release date to album folder names and `album_info.txt`
  - Format: `Artist - Album Name (YYYY-MM-DD)`
  - Better chronological organization
- **Emoji Removal**: Removed emoji characters for better cross-platform compatibility
- **Album ID**: Updated album ID handling and storage

---

## 2026-03-04 to 2026-03-03

### Configuration System & Documentation

**Commits:** `0d4763c`, `d95246c`, `f70b14a`

#### Major Additions
- **Configuration Files**: Added YAML-based configuration system (`config.yml`, `config_manager.py`)
  - Centralized configuration management
  - Easy customization without code changes
  - Support for all major settings (API, download, metadata, network, logging)
  
- **Documentation**: Created comprehensive README.md
  - Installation instructions
  - Usage examples
  - API reference
  - Configuration guide
  - Troubleshooting section

- **Code Refactoring**: Major code restructuring for better maintainability

---

## 2026-03-01

### Playlist Support & Artist Tag Fixes

**Commits:** `63c4479`, `02f453a`, `594c5e4`, `4d6d314`

#### New Features
- **Playlist Download**: Added complete playlist download functionality
  - Extract all songs from playlist
  - Support selective track downloads
  - Proper metadata handling for playlist tracks

#### Bug Fixes
- **Artist Tags**: Fixed artist tag issues in metadata writing
  - Proper handling of multiple artists
  - Correct ID3 TPE1 tag formatting
  - Improved artist name parsing

---

## 2026-02-28

### Cover Art & Logging Updates

**Commits:** `a8d2e0e`, `40da1a0`, `35dc01b`

#### Improvements
- **Cover Resolution**: Updated cover page resolution to 320x320 for better quality
- **Logging System**: Major logging utility updates
  - Structured logging format
  - Better log level management
  - Fixed logger initialization issues

---

## 2026-02-26 to 2026-02-25

### Download Logic & Methods

**Commits:** `5a83dd9`, `b9e50ea`, `0774225`

#### Core Development
- **Download Logic**: Implemented core downloading functionality
  - Audio file download with streaming
  - Metadata extraction and embedding
  - Cover art download and embedding
  - Lyrics retrieval and saving
  
- **Method Updates**: Refined download methods for better performance
- **Logging Integration**: Added comprehensive logging throughout the application

---

## 2026-02-24

### Project Initialization

**Commit:** `f16d4e8`

#### Initial Setup
- **Project Init**: Initial project setup and structure
  - Basic API client implementation
  - Core download functionality
  - Initial file structure
  - Dependency configuration

---

---

## Future Roadmap

### Planned Features
- [ ] Support for additional music platforms (QQ Music, Kugou, etc.)
- [ ] Web-based GUI interface with React/Vue
- [ ] Download queue management with pause/resume functionality
- [ ] Duplicate detection and prevention system
- [ ] Automatic library organization and cleanup tools
- [ ] Integration with popular music players (Foobar2000, MusicBee, etc.)
- [ ] Export playlists to various formats (M3U, PLS, XSPF)
- [ ] Command-line argument parser for non-interactive batch operations
- [ ] Docker containerization for easy deployment
- [ ] Automated testing suite with CI/CD pipeline
- [ ] Album ID file generation enhancement with QR codes
- [ ] Batch metadata editing interface
- [ ] Cloud sync support for library backup

### Potential Improvements
- Enhanced error recovery mechanisms with detailed diagnostics
- More granular quality selection per song or album
- Custom metadata field mapping and transformation rules
- Plugin architecture for community extensions
- Database backend (SQLite) for advanced library management
- REST API for remote control and integration
- Multi-threaded downloads for faster processing
- Bandwidth throttling and scheduling options
- Advanced search and filtering capabilities

---

**Note**: This project follows semantic versioning (SemVer). Version numbers follow the MAJOR.MINOR.PATCH format where:
- **MAJOR** version indicates incompatible API changes
- **MINOR** version indicates added functionality in a backward-compatible manner  
- **PATCH** version indicates backward-compatible bug fixes

For detailed commit history, see the git log or visit the repository.
