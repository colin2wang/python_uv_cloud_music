# Music Library Organizer

A powerful Python-based tool for organizing, downloading, and managing your digital music library with automatic metadata tagging, cover art embedding, and interactive download interface.

## Features

- **Multi-format Support**: Works with MP3, FLAC, M4A, AAC, and other popular audio formats
- **Automatic Metadata Tagging**: Embeds title, artist, album, track number, year, lyrics, and NetEase Cloud Music ID directly into audio files
- **Cover Art Integration**: Automatically downloads and embeds high-quality album artwork (320x320)
- **Lyrics Download**: Saves synchronized lyrics files (.lrc) alongside your music
- **Playlist Management**: Extract and download entire playlists with a single command
- **Album Processing**: Download complete albums with proper track ordering, metadata, and dedicated album folders
- **Smart Search**: Find songs by keyword and preview before downloading
- **Batch Processing**: Efficiently process multiple tracks simultaneously
- **Quality Selection**: Choose from multiple quality levels (standard, exhigh, lossless, hires, sky, jyeffect, jymaster)
- **Intelligent Filename Handling**: Automatically cleans special characters and adds track numbering
- **Album Folder Organization**: Creates structured album folders with description files and cover art
- **Folder Utilities**: Built-in tools for processing existing music libraries in batch
- **Configurable Behavior**: YAML-based configuration for customization without code changes
- **Interactive Mode**: User-friendly interactive interface for easy song/album/playlist downloads
- **Smart Retry Logic**: Automatic retry mechanism for failed API requests with configurable attempts
- **NextMusicTool Integration**: Optional integration with NextMusicTool for enhanced URL resolution
- **Progress Tracking**: Real-time progress display with estimated completion time for batch operations

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install Dependencies

Using pip:
```bash
pip install requests mutagen pyyaml imagesize
```

Or using uv (recommended):
```bash
uv sync
```

## Quick Start

### Interactive Mode (Recommended)

The easiest way to use the tool is through the interactive interface:

```bash
python interactive_process.py
```

This will guide you through:
- Selecting download method (single song, album, or playlist)
- Entering resource IDs
- Choosing quality level
- Specifying which tracks to download (for albums/playlists)

Your preferences are automatically saved for next time!

### Download a Single Song

```python
from process_cloud_music import download_song

# Download a song by ID
download_song("12345678", level="lossless")
```

### Download an Album

```python
from process_cloud_music import download_album

# Download complete album
download_album("87654321", index_ids=[], level="lossless")

# Download specific tracks from album (e.g., tracks 4, 6, 15)
download_album("87654321", index_ids=[4, 6, 15], level="lossless")
```

### Download a Playlist

```python
from process_cloud_music import download_playlist

# Download complete playlist
download_playlist("11223344", index_ids=[], level="lossless")

# Download specific tracks from playlist
download_playlist("11223344", index_ids=[1, 3, 5], level="lossless")
```

## Configuration

All settings are managed through `config.yml`. The tool loads configuration automatically on startup.

### Complete Configuration Options

```yaml
# API Configuration
api:
  base_url: "https://musicapi.example.com"

# Download Configuration
download:
  default_dir: "downloads"              # Default download directory
  default_quality: "lossless"           # Audio quality
                                        # Options: standard, exhigh, lossless,
                                        #          hires, sky, jyeffect, jymaster
  add_index_to_filename: true           # Add track numbers to filenames
  index_format: "03d"                   # Number format (e.g., 001, 002)

# Filename Configuration
filename:
  pattern: "{index} - {artist} - {title}"  # Filename pattern
                                           # Variables: index, artist, title, album
  illegal_char_replacement: "_"         # Replace illegal characters
  artist_delimiter_replacement: ", "    # Artist delimiter replacement

# Metadata Configuration
metadata:
  write_metadata: true                  # Write song metadata
  write_cover: true                     # Embed cover art
  write_lyrics: true                    # Save and embed lyrics
  max_lyric_length: 1000                # Maximum lyric length
  use_next_music_tool: false            # Use NextMusicTool for URL resolution

# Network Configuration
network:
  timeout: 30                           # Request timeout in seconds
  random_delay_max: 2.5                 # Max random delay between requests
  api_delay_min: 1.0                    # Minimum delay between API calls
  max_retries: 1                        # Number of retries for failed requests

# Logging Configuration
logging:
  level: "INFO"                         # Log level
                                        # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: true                  # Output to console
  file_output: true                     # Output to file
  log_file: "logs/app.log"             # Log file path
```

### Filename Pattern Variables

Available variables for customizing filename patterns:
- `{index}` - Track number (formatted according to `index_format`)
- `{artist}` - Artist name
- `{title}` - Song title
- `{album}` - Album name

### Quality Level Descriptions

- **standard**: Standard quality (128kbps) - Smallest file size
- **exhigh**: High quality (320kbps) - Good balance of quality and size
- **lossless**: Lossless quality (FLAC/WAV) - CD quality (default)
- **hires**: Hi-Res quality - Higher than CD quality
- **sky**: Immersive surround sound - Spatial audio
- **jyeffect**: HD surround sound - Enhanced stereo
- **jymaster**: Ultra-clear master - Studio master quality

The system includes smart retry logic that automatically tries alternative quality levels if the preferred level is unavailable.



### Output Structure

Downloaded files are organized as follows:

**Individual Songs:**
```
downloads/
├── 001 - Artist Name - Song Title.mp3
├── 001 - Artist Name - Song Title.lrc
├── 001 - Artist Name - Song Title.jpg
├── 002 - Artist Name - Song Title II.flac
├── 002 - Artist Name - Song Title II.lrc
└── 002 - Artist Name - Song Title II.jpg
```

**Albums:**
```
downloads/
├── Artist Name - Album Name (2024-01-01)/
│   ├── album_info.txt          # Album description
│   ├── cover.jpg               # Album cover
│   ├── 001 - Artist - Track 1.flac
│   ├── 002 - Artist - Track 2.flac
│   └── ...
```

## API Reference

### Core Functions

#### `download_song(song_id: str, level: str = "lossless")`
Download a single song with all associated resources.

**Parameters:**
- `song_id` (str): Unique identifier for the song
- `level` (str): Audio quality level (default: "lossless")

#### `download_album(album_id: str, index_ids: list = [], level: str = "lossless")`
Download songs from an album with automatic folder organization.

**Features:**
- Creates dedicated album folder with format: `Artist - Album Name (Release Date)`
- Generates `album_info.txt` with album details and description
- Downloads and saves album cover art
- Embeds track numbers in filenames and metadata
- Supports selective track downloading

**Parameters:**
- `album_id` (str): Unique identifier for the album
- `index_ids` (list): List of track numbers to download (empty list for all tracks)
- `level` (str): Audio quality level (default: "lossless")

**Example:**
```python
# Download complete album
from process_cloud_music import download_album

# Complete album
download_album("87654321", level="lossless")

# Specific tracks only (tracks 4, 6, 15)
download_album("87654321", index_ids=[4, 6, 15], level="lossless")
```

#### `download_playlist(playlist_id: str, index_ids: list, level: str = "lossless")`
Download songs from a playlist.

**Parameters:**
- `playlist_id` (str): Unique identifier for the playlist
- `index_ids` (list): List of track indices to download (empty list for all tracks)
- `level` (str): Audio quality level (default: "lossless")

### Utility Functions

#### `get_song_metadata_by_song_id(song_id: str, level: str = "lossless")`
Retrieve detailed metadata for a song without downloading.

**Returns:** Dictionary containing song information and download URL

#### `prepare_album_folder(album_metadata: dict, download_dir: str = None) -> str | None`
Create album folder with description file and cover image.

**Returns:** Path to the created album folder or None if failed

**Features:**
- Creates properly named album folder
- Generates comprehensive album information file
- Downloads and saves high-quality album cover

#### `write_metadata_to_file(file_path: str, metadata: Dict[str, Any]) -> bool`
Embed metadata into an existing audio file.

**Returns:** Boolean indicating success/failure

**Supported Formats:**
- MP3: ID3 tags (TIT2, TPE1, TALB, TRCK, TYER, APIC, COMM)
- FLAC: Vorbis comments (TITLE, ARTIST, ALBUM, TRACKNUMBER, LYRICS)
- M4A/AAC: MP4 tags (©nam, ©ART, ©alb, trkn, ©lyr, covr)

#### `download_song_and_resources(metadata: Dict[str, Any], download_dir: str, idx: int) -> bool`
Download song and all related resources (lyrics, cover art) with metadata embedding.

**Returns:** Boolean indicating success/failure

**Process:**
1. Downloads audio file
2. Writes metadata tags
3. Downloads and saves lyrics (.lrc file)
4. Downloads and saves cover art (.jpg file)
5. Embeds cover art into audio file

## Advanced Usage

### Interactive Download Tool

Use the interactive mode for a user-friendly experience:

```bash
python interactive_process.py
```

Features:
- Menu-driven interface for selecting download type
- Remembers your last used settings
- Supports selective track downloads for albums/playlists
- Input validation and confirmation
- Progress tracking and error handling

Example session:
```
Welcome to Cloud Music Interactive Download Tool!

Please select download method:
1. Download single song by Song ID
2. Download album by Album ID
3. Download playlist by Playlist ID
0. Exit

Enter your choice [1]: 2
Enter Album ID: 361790100
Enter quality level [lossless]: 
Enter track numbers to download (or press Enter for all): 1,3,5

Parsed indexes: [1, 3, 5]
Total count: 3
Are these indexes correct? (yes/no) [yes]: yes
```

### Custom API Endpoint

You can configure a custom API endpoint in `config.yml`:

```yaml
api:
  base_url: "https://your-custom-api.com"
```

Or programmatically:
```python
from process_cloud_music import MusicToolAPI

api = MusicToolAPI(base_url="https://your-custom-api.com")
```

### Batch Processing Existing Music Libraries

The tool includes utilities for processing existing music folder structures:

```python
from process_from_folders import process_folders, iterate_folders, list_folders
from process_album_lyrics_fix import fix_album_lyrics
from process_album_cover_redownload import redownload_album_cover

# List all album folders in a directory
folders = list_folders("J:\\Music")
print(f"Found {len(folders)} albums")

# Process all album folders with a specific function
results = process_folders(
    "J:\\Music",
    fix_album_lyrics,
    show_progress=True,
    stop_on_error=False
)

# Or iterate manually for custom processing
for folder in iterate_folders("J:\\Music"):
    redownload_album_cover(folder)
```

Available utility functions:
- **list_folders()**: Get sorted list of all subdirectories
- **iterate_folders()**: Iterator for memory-efficient folder processing
- **process_folders()**: Batch process with progress tracking and error handling
- **fix_album_lyrics()**: Fix and update lyrics for existing albums
- **redownload_album_cover()**: Re-download and embed album covers

### Error Handling

All functions include comprehensive error handling and logging. Failed downloads are logged but don't interrupt batch processing.

### Smart Retry Mechanism

The tool implements intelligent retry logic for API requests:

```python
from process_cloud_music import get_song_metadata_by_song_id

# Automatically retries up to configured max_retries times
metadata = get_song_metadata_by_song_id("12345678", level="lossless")

# Retries help handle:
# - Temporary network failures
# - API rate limiting
# - Quality level unavailability
# - Server-side errors
```

Configure retry behavior in `config.yml`:
```yaml
network:
  max_retries: 1              # Number of retry attempts
  random_delay_max: 2.5       # Random delay between requests
  api_delay_min: 1.0          # Minimum delay between API calls
```

### NextMusicTool Integration

Optionally integrate with NextMusicTool for enhanced URL resolution:

```yaml
metadata:
  use_next_music_tool: true   # Enable NextMusicTool integration
```

When enabled, the tool will use NextMusicTool to resolve song URLs, which may provide better availability or quality options.

### Logging

The tool uses Python's built-in logging module. Configure logging in `logging_config.py` to customize output format and destination.

Logs are saved to the `logs/` directory with automatic rotation and archiving.

## Technical Details

### Supported Metadata Formats

- **ID3 Tags** (MP3): TIT2 (title), TPE1 (artist), TALB (album), TRCK (track), TYER (year), APIC (cover), COMM (lyrics), TXXX (NetEase Cloud Music ID)
- **Vorbis Comments** (FLAC): TITLE, ARTIST, ALBUM, TRACKNUMBER, LYRICS, CMUSIC_ID
- **MP4 Tags** (M4A/AAC): ©nam, ©ART, ©alb, trkn, ©lyr, covr, ----:CMUSIC_ID

### File Naming Convention

Files are named using the pattern:
```
{track_number} - {artist} - {title}.{extension}
```

Special characters are automatically replaced with underscores to ensure cross-platform compatibility.

## Project Structure

```
.
├── process_cloud_music.py              # Main processing logic and API client
├── interactive_process.py              # Interactive download interface
├── process_from_folders.py             # Folder listing and batch processing utilities
├── process_album_cover_redownload.py   # Album cover re-download utility
├── process_album_lyrics_fix.py         # Lyrics correction utility
├── process_album_metadata_fix.py       # Album metadata correction utility
├── config_manager.py                   # Configuration management
├── config.yml                          # YAML configuration file
├── logging_config.py                   # Logging configuration
├── utils.py                            # Utility functions
├── tool_next_music.py                  # NextMusicTool integration
├── pyproject.toml                      # Project dependencies
├── api_docs/                           # API documentation
│   ├── get_song.md
│   ├── get_album.md
│   └── get_playlist.md
├── logs/                               # Log files
└── downloads/                          # Default download directory
```

## Limitations

- Requires valid song/album/playlist IDs from the supported music source
- Download quality depends on source availability
- Some regions may have restricted access

## Troubleshooting

### Common Issues

**Issue: "No available quality"**
- The requested song may not be available in any quality level
- Try a different quality level (e.g., "exhigh" instead of "lossless")
- Check if the song ID is correct
- The song may have been removed from the platform

**Issue: "JSON parsing failed"**
- Network connectivity issues
- API endpoint may be temporarily unavailable
- Check your internet connection
- Try again after a few moments (the tool has built-in retry logic)

**Issue: "Metadata writing failed"**
- File format may not support metadata embedding
- Check file permissions in the download directory
- Ensure the file is not open in another application
- Some DRM-protected files cannot be modified

**Issue: Slow download speed**
- Check your internet connection
- The source server may be experiencing high load
- Try downloading during off-peak hours
- Consider using a lower quality level for faster downloads

**Issue: Missing lyrics or cover art**
- Not all songs have lyrics or cover art available
- The API may not return this information for some tracks
- Check the logs for specific error messages

### Getting Help

If you encounter issues:
1. Check the log files in the `logs/` directory
2. Verify your configuration in `config.yml`
3. Ensure you're using the latest version of dependencies
4. Review the API documentation in `api_docs/`

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests for:
- Bug fixes
- New features
- Format support improvements
- Documentation enhancements

## License

This project is provided as-is for educational and personal use only.

## Disclaimer

This tool is designed for organizing personally licensed music. Please respect copyright laws and terms of service of music platforms. Only download content you have the right to use.

## Acknowledgments

- Built with [requests](https://pypi.org/project/requests/) for HTTP operations
- Metadata handling powered by [mutagen](https://pypi.org/project/mutagen/)
- Package management by [uv](https://github.com/astral-sh/uv)

---

**Enjoy your organized music library!**
