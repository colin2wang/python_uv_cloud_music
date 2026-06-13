"""
Shared album info loader for album processing modules.
"""

from pathlib import Path
from typing import Optional, Dict

from src.util.util_logging import setup_logger

logger = setup_logger(__name__)


def load_album_info(album_folder: Path) -> Optional[Dict]:
    """
    Load album information from album_info.txt in the given folder.

    Args:
        album_folder: Path to the album folder

    Returns:
        Dictionary with album info keys (album_name, album_artist, album_id,
        publish_date, song_count), or None if loading failed.
    """
    album_info_file = album_folder / 'album_info.txt'

    if not album_info_file.exists():
        logger.warning(f"album_info.txt not found in {album_folder}")
        return None

    try:
        with open(album_info_file, 'r', encoding='utf-8') as f:
            content = f.read()

        album_info = {}
        key_map = {
            'album': 'album_name',
            'artist': 'album_artist',
            'album id': 'album_id',
            'publish date': 'publish_date',
            'song count': 'song_count',
        }

        for line in content.split('\n'):
            line = line.strip()
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            key_lower = key.strip().lower()
            if key_lower in key_map:
                album_info[key_map[key_lower]] = value.strip()

        logger.info(
            f"Album info loaded: {album_info.get('album_name', 'Unknown')} - "
            f"{album_info.get('album_artist', 'Unknown Artist')}"
        )
        if 'album_id' in album_info:
            logger.info(f"Album ID: {album_info['album_id']}")

        return album_info

    except Exception as e:
        logger.error(f"Failed to load album_info.txt: {e}")
        return None
