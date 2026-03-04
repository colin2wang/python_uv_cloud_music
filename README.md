# Music Library Organizer

A powerful Python-based tool for organizing, downloading, and managing your digital music library with automatic metadata tagging and cover art embedding.

## Features

- 🎵 **Multi-format Support**: Works with MP3, FLAC, M4A, AAC, and other popular audio formats
- 🏷️ **Automatic Metadata Tagging**: Embeds title, artist, album, track number, and lyrics directly into audio files
- 🖼️ **Cover Art Integration**: Automatically downloads and embeds high-quality album artwork
- 📝 **Lyrics Download**: Saves synchronized lyrics files alongside your music
- 🎼 **Playlist Management**: Extract and download entire playlists with a single command
- 💿 **Album Processing**: Download complete albums with proper track ordering and metadata
- 🔍 **Smart Search**: Find songs by keyword and preview before downloading
- 📦 **Batch Processing**: Efficiently process multiple tracks simultaneously
- 🎯 **Quality Selection**: Choose from multiple quality levels (standard, high quality, lossless)
- ⚡ **Intelligent Filename Handling**: Automatically cleans special characters and adds track numbering

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install Dependencies

Using pip:
```bash
pip install requests mutagen pyyaml
```

Or using uv (recommended):
```bash
uv sync
```

## Quick Start

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

### Using the Configuration File

The tool now supports YAML-based configuration through `config.yml`. This allows you to customize behavior without modifying code.

**Key Configuration Options:**

```yaml
# download: Default download settings
default_dir: "downloads"          # Download directory
default_quality: "lossless"        # Audio quality (lossless/exhigh/standard)
add_index_to_filename: true        # Add track numbers to filenames
index_format: "03d"                # Number format (e.g., 001, 002)

# metadata: Control what gets embedded
write_metadata: true               # Write song metadata
write_cover: true                  # Embed cover art
write_lyrics: true                 # Save and embed lyrics

# network: Connection settings
timeout: 30                        # Request timeout in seconds
random_delay_max: 2.5              # Max random delay between requests
```

### Quality Levels

The tool supports multiple quality tiers:
- `lossless` - Highest quality (FLAC/WAV)
- `exhigh` - High quality (320kbps)
- `standard` - Standard quality (128kbps)

The system will automatically fall back to lower qualities if the preferred level is unavailable.

### Output Structure

Downloaded files are organized as follows:
```
downloads/
├── 001 - Artist Name - Song Title.mp3
├── 001 - Artist Name - Song Title.lrc
├── 001 - Artist Name - Song Title.jpg
├── 002 - Artist Name - Song Title II.flac
├── 002 - Artist Name - Song Title II.lrc
└── 002 - Artist Name - Song Title II.jpg
```

## API Reference

### Core Functions

#### `download_song(song_id: str, level: str = "lossless")`
Download a single song with all associated resources.

**Parameters:**
- `song_id` (str): Unique identifier for the song
- `level` (str): Audio quality level (default: "lossless")

#### `download_album(album_id: str, index_ids: list, level: str = "lossless")`
Download songs from an album.

**Parameters:**
- `album_id` (str): Unique identifier for the album
- `index_ids` (list): List of track numbers to download (empty list for all tracks)
- `level` (str): Audio quality level (default: "lossless")

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

#### `write_metadata_to_file(file_path: str, metadata: Dict[str, Any])`
Embed metadata into an existing audio file.

**Returns:** Boolean indicating success/failure

#### `download_song_and_resources(metadata: Dict[str, Any], download_dir: str, idx: int)`
Download song and all related resources (lyrics, cover art) with metadata embedding.

**Returns:** Boolean indicating success/failure

## Advanced Usage

### Custom API Endpoint

You can configure a custom API endpoint in `config.yml`:

```yaml
api:
  base_url: "https://your-custom-api.com"
```

Or programmatically:
```python
api = NeteaseMusicToolAPI(base_url="https://your-custom-api.com")
```

### Error Handling

All functions include comprehensive error handling and logging. Failed downloads are logged but don't interrupt batch processing.

### Logging

The tool uses Python's built-in logging module. Configure logging in `logging_config.py` to customize output format and destination.

## Technical Details

### Supported Metadata Formats

- **ID3 Tags** (MP3): TIT2 (title), TPE1 (artist), TALB (album), TRCK (track), TYER (year), APIC (cover), COMM (lyrics)
- **Vorbis Comments** (FLAC): TITLE, ARTIST, ALBUM, TRACKNUMBER, LYRICS
- **MP4 Tags** (M4A/AAC): ©nam, ©ART, ©alb, trkn, ©lyr, covr

### File Naming Convention

Files are named using the pattern:
```
{track_number} - {artist} - {title}.{extension}
```

Special characters are automatically replaced with underscores to ensure cross-platform compatibility.

## Project Structure

```
.
├── process_cloud_music.py    # Main processing logic
├── config_manager.py         # Configuration management
├── config.yml                # YAML configuration file
├── logging_config.py         # Logging configuration
├── pyproject.toml            # Project dependencies
├── test_config.py            # Configuration test script
├── api_docs/                 # API documentation
│   ├── get_song.md
│   ├── get_album.md
│   └── get_playlist.md
└── downloads/                # Default download directory
```

## Limitations

- Requires valid song/album/playlist IDs from the music platform
- Download quality depends on source availability
- Some regions may have restricted access

## Troubleshooting

### Common Issues

**Issue: "No available quality"**
- The requested song may not be available in any quality level
- Try a different song or check if the ID is correct

**Issue: "JSON parsing failed"**
- Network connectivity issues
- API endpoint may be temporarily unavailable

**Issue: "Metadata writing failed"**
- File format may not support metadata embedding
- Check file permissions in the download directory

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

**Enjoy your organized music library! 🎵**
