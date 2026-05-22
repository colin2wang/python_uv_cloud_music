"""
Utility functions for Music Library Organizer

This module provides common utility functions used across the project.
"""
import random
import re
import time
from pathlib import Path
from typing import Optional

from util_config import config
from util_logging import setup_logger
from tqdm import tqdm
from util_database import MusicDB

# Create logger for utils module
logger = setup_logger(__name__)

# Database instance
db = MusicDB()

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


def random_sleep(max_delay: float = None, min_delay: float = 1.0, reason: str = "General rate limiting"):
    """
    Add random delay to avoid frequent requests

    Args:
        max_delay: Maximum delay in seconds (default: from config)
        min_delay: Minimum delay in seconds (default: 1.0)
        reason: Reason for the delay (for logging purposes)
    """
    if max_delay is None:
        max_delay = config.get_random_delay_max()
    delay = random.uniform(min_delay, max_delay)
    logger.info(f"Random sleeping for {delay:.2f} seconds (range: {min_delay:.2f}-{max_delay:.2f}s)... (Reason: {reason})")
    
    # Show simple text progress during sleep
    start_time = time.time()
    end_time = start_time + delay
    
    while time.time() < end_time:
        remaining = end_time - time.time()
        if remaining > 0:
            # Display countdown in console
            print(f"\rWaiting ({reason}): {remaining:.2f}s remaining...", end="", flush=True)
            time.sleep(min(0.1, remaining))
        else:
            break
    
    # Clear the line after completion
    print("\r" + " " * 60 + "\r", end="", flush=True)
    logger.info(f"Sleep completed.")


def ensure_download_interval():
    """
    Ensure minimum interval between downloads by checking database timestamp.
    
    This function should be called at the beginning of download_song_and_resources.
    It reads the last download timestamp from database and waits if necessary
    to maintain the configured download interval.
    """
    import os
    
    download_interval = config.get_download_interval()
    
    # Get current timestamp
    current_time = time.time()
    
    # Check if last download timestamp exists in database
    last_timestamp_str = db.get_config('last_download_timestamp')
    
    if last_timestamp_str:
        try:
            last_timestamp = float(last_timestamp_str)
            
            # Calculate elapsed time since last download
            elapsed_time = current_time - last_timestamp
            
            # If less than required interval, wait for the remaining time
            if elapsed_time < download_interval:
                wait_time = download_interval - elapsed_time
                logger.info(f"Last download was {elapsed_time:.2f}s ago. Waiting {wait_time:.2f}s to maintain {download_interval}s interval...")
                random_sleep(max_delay=wait_time, min_delay=wait_time, reason="Maintaining download interval")
            else:
                logger.info(f"Sufficient time has passed since last download ({elapsed_time:.2f}s >= {download_interval}s). No wait needed.")
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing last download timestamp: {e}. Waiting full interval.")
            # If timestamp is corrupted, wait full interval
            _wait_full_interval(download_interval)
    else:
        logger.info(f"No previous download record found. Waiting full interval ({download_interval}s)...")
        _wait_full_interval(download_interval)


def update_last_download_timestamp():
    """
    Update the last download timestamp in database.
    
    This function should be called at the end of download_song_and_resources
    to record when the current download completed.
    """
    try:
        current_timestamp = str(time.time())
        db.upsert_config('last_download_timestamp', current_timestamp)
        logger.debug("Updated last download timestamp in database.")
    except Exception as e:
        logger.error(f"Failed to write last download timestamp to database: {e}")


def _wait_full_interval(interval: float):
    """
    Wait for the full download interval.
    
    Args:
        interval: Interval in seconds to wait
    """
    logger.info(f"Waiting {interval:.2f} seconds before starting download...")
    random_sleep(max_delay=interval, min_delay=interval, reason="Initial download wait")


def main():
    """
    Test function for random_sleep utility
    """
    print("Testing random_sleep function...")
    
    # Test 1: Default parameters
    print("\nTest 1: Using default parameters")
    random_sleep(reason="Test 1 - Default settings")
    
    # Test 2: Custom delay range
    print("\nTest 2: Custom delay range (2-3 seconds)")
    random_sleep(max_delay=3.0, min_delay=2.0, reason="Test 2 - Custom range")
    
    # Test 3: Short delay
    print("\nTest 3: Short delay (0.5-1 second)")
    random_sleep(max_delay=1.0, min_delay=0.5, reason="Test 3 - Short delay")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
