"""
Utility functions for Music Library Organizer

This module provides common utility functions used across the project.
"""
import random
import re
import time
from pathlib import Path
from typing import Optional

from config_manager import config
from logging_config import setup_logger

# Create logger for utils module
logger = setup_logger(__name__)

# Supported audio formats
AUDIO_EXTENSIONS = {'.mp3', '.mp2', '.mp1', '.flac', '.m4a', '.mp4', '.aac'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

# MIME type mapping for images
IMAGE_MIME_TYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.bmp': 'image/bmp',
    '.gif': 'image/gif',
}


def get_audio_extension(file_path: str | Path) -> str:
    """
    Get the audio file extension in lowercase.

    Args:
        file_path: Path to the audio file

    Returns:
        Lowercase extension including the dot (e.g., '.mp3')
    """
    return Path(file_path).suffix.lower()


def is_audio_file(file_path: str | Path) -> bool:
    """
    Check if a file is an audio file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        True if the file is an audio file, False otherwise
    """
    return get_audio_extension(file_path) in AUDIO_EXTENSIONS


def get_image_mime_type(image_path: str | Path) -> str:
    """
    Get the MIME type for an image file based on its extension.

    Args:
        image_path: Path to the image file

    Returns:
        MIME type string (default: 'image/jpeg')
    """
    ext = Path(image_path).suffix.lower()
    return IMAGE_MIME_TYPES.get(ext, 'image/jpeg')


def get_mp4_image_format(image_path: str | Path) -> int:
    """
    Get the MP4 image format constant for an image file.

    Args:
        image_path: Path to the image file

    Returns:
        MP4Cover format constant
    """
    from mutagen.mp4 import MP4Cover
    ext = Path(image_path).suffix.lower()
    return MP4Cover.FORMAT_PNG if ext == '.png' else MP4Cover.FORMAT_JPEG


def clean_filename(filename: str, replacement: Optional[str] = None) -> str:
    """
    Clean illegal characters from a filename.

    Args:
        filename: Original filename
        replacement: Replacement character for illegal chars (default: from config)

    Returns:
        Cleaned filename
    """
    if replacement is None:
        replacement = config.get_illegal_char_replacement()
    return re.sub(r'[<>:"/\\|?*]', replacement, filename)


def parse_music_filename(filename: str) -> dict:
    """
    Parse music file filename to extract metadata.

    Expected formats:
        - {index} - {artist} - {title}
        - {artist} - {title}

    Args:
        filename: Filename without extension

    Returns:
        Dictionary with 'track_number', 'artist', and 'title'
    """
    result = {
        'track_number': '',
        'artist': '',
        'title': ''
    }

    clean_name = filename.strip()

    # Pattern with index: "001 - Artist - Title"
    pattern_with_index = r'^(\d+)\s*-\s*(.+?)\s*-\s*(.+)$'
    match = re.match(pattern_with_index, clean_name)

    if match:
        result['track_number'] = match.group(1).strip()
        result['artist'] = match.group(2).strip()
        result['title'] = match.group(3).strip()
        return result

    # Pattern without index: "Artist - Title"
    pattern_without_index = r'^(.+?)\s*-\s*(.+)$'
    match = re.match(pattern_without_index, clean_name)

    if match:
        result['artist'] = match.group(1).strip()
        result['title'] = match.group(2).strip()
        return result

    # Fallback: use whole filename as title
    result['title'] = clean_name
    return result


def truncate_filename(filename: str, max_length: int = 200) -> str:
    """
    Truncate filename if it exceeds maximum length.

    Args:
        filename: Original filename
        max_length: Maximum allowed length

    Returns:
        Truncated filename if necessary
    """
    if len(filename) <= max_length:
        return filename

    # Simple truncation
    return filename[:max_length]


def find_cover_image(folder_path: str | Path) -> Optional[Path]:
    """
    Find cover image in a folder.

    Looks for 'cover.jpg' first, then any image file.

    Args:
        folder_path: Path to the folder to search

    Returns:
        Path to cover image or None if not found
    """
    folder = Path(folder_path)

    # Look for cover.jpg first
    for ext in IMAGE_EXTENSIONS:
        cover_path = folder / f'cover{ext}'
        if cover_path.exists():
            return cover_path

    # Look for any image file
    for ext in IMAGE_EXTENSIONS:
        for img_file in folder.glob(f'*{ext}'):
            if img_file.name.lower() != 'cover.jpg':
                return img_file

    return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "10.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary values.

    Args:
        dictionary: Dictionary to traverse
        keys: Sequence of keys to follow
        default: Default value if any key is missing

    Returns:
        Value at the nested path or default
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def random_sleep(max_delay: float = None, reason: str = "General rate limiting"):
    """
    Add random delay to avoid frequent requests

    Args:
        max_delay: Maximum delay in seconds (default: from config)
        reason: Reason for the delay (for logging purposes)
    """
    if max_delay is None:
        max_delay = config.get_random_delay_max()
    delay = random.uniform(1.0, max_delay)
    logger.info(f"Sleeping for {delay:.2f} seconds... ({reason})")
    time.sleep(delay)
