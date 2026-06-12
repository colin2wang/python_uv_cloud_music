"""
Utility functions for file operations
"""

import re
from pathlib import Path
from typing import Union

from src.util.util_config import config
from src.util.util_logging import setup_logger

logger = setup_logger(__name__)


def get_audio_extension(file_path: Union[str, Path]) -> str:
    """Get audio file extension"""
    return Path(file_path).suffix.lower()


def get_image_mime_type(image_path: str) -> str:
    """Get MIME type for image file"""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.bmp': 'image/bmp',
        '.gif': 'image/gif'
    }
    return mime_types.get(ext, 'image/jpeg')


def get_mp4_image_format(image_path: str) -> int:
    """Get MP4 image format for cover art"""
    ext = Path(image_path).suffix.lower()
    formats = {
        '.jpg': 1,
        '.jpeg': 1,
        '.png': 2
    }
    return formats.get(ext, 1)


def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters"""
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32)
    # Remove leading/trailing whitespace and dots
    cleaned = cleaned.strip(' .')
    return cleaned


def _get_download_dir() -> str:
    """Get download directory path"""
    return config.get_download_dir()


def _get_default_quality() -> str:
    """Get default quality level"""
    return config.get_default_quality()


def _get_max_retries() -> int:
    """Get maximum retry count"""
    return config.get_max_retries()


def _should_use_next_music_tool() -> bool:
    """Check if NextMusicTool should be used"""
    return config.should_use_next_music_tool()


def _should_write_metadata() -> bool:
    """Check if metadata should be written"""
    return config.should_write_metadata()


def _should_write_lyrics() -> bool:
    """Check if lyrics should be written"""
    return config.should_write_lyrics()


def _should_write_cover() -> bool:
    """Check if cover should be written"""
    return config.should_write_cover()


def _get_timeout() -> int:
    """Get download timeout value"""
    return config.get_timeout()


def _get_max_lyric_length() -> int:
    """Get maximum lyrics length"""
    return config.get_max_lyric_length()


def _should_add_index() -> bool:
    """Check if index should be added to filenames"""
    return config.should_add_index()


def _get_index_format() -> str:
    """Get index format string"""
    return config.get_index_format()