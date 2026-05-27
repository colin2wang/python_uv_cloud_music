"""
NetEase Cloud Music API utility class
"""

import re
import requests
from typing import Optional, Dict, Any

from util_config import config
from util_logging import setup_logger

logger = setup_logger(__name__)

# Constants
HTTP_OK = 200
HTTP_TOO_MANY_REQUESTS = 429
DEFAULT_TIMEOUT = 30


class MusicToolAPI:
    """NetEase Cloud Music API utility class"""
    
    _HEADERS = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': None,  # Will be set dynamically
        'priority': 'u=1, i',
        'referer': None,
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or config.get_api_base_url()).rstrip('/')
        self.session = requests.Session()
        self._setup_request_headers()

    def _setup_request_headers(self) -> None:
        """Set request headers using class constants as base"""
        headers = dict(self._HEADERS)
        headers['origin'] = self.base_url
        headers['referer'] = self.base_url
        self.session.headers.update(headers)

    def _extract_id(self, text: str, pattern_type: str = 'song') -> Optional[str]:
        """Extract song/playlist/album ID from text
        
        Args:
            text: String containing URL or numeric ID
            pattern_type: Type of ID to extract ('song', 'playlist', 'album')
        
        Returns:
            Extracted numeric ID, or None if extraction fails
        """
        if not text:
            return None
            
        text = str(text)
        patterns = {
            'song': r'song\?id=(\d+)',
            'playlist': r'playlist\?id=(\d+)',
            'album': r'album\?id=(\d+)'
        }

        # Check if it's a NetEase Cloud Music link
        if 'music.163.com' in text or '163cn.tv' in text:
            pattern = patterns.get(pattern_type, r'id=(\d+)')
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # If it's pure digits, return directly
        if text.isdigit():
            return text

        return None

    def search(self, keyword: str, limit: int = 10) -> Optional[dict]:
        """Search for songs"""
        from util_commons import random_sleep
        random_sleep(5.0, reason="Before search API request")
        try:
            response = self.session.post(
                f"{self.base_url}/Search",
                data={'keyword': keyword, 'limit': limit},
                timeout=DEFAULT_TIMEOUT
            )
            return _parse_json_response(response.text, "search")
        except requests.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return None

    def parse_song(self, song_id_or_url: str, level: str = "lossless") -> Optional[dict]:
        """Parse song information"""
        song_id = self._extract_id(song_id_or_url, 'song')
        if not song_id:
            logger.error(f"Invalid song ID or URL: {song_id_or_url}")
            return None
            
        from util_commons import random_sleep
        random_sleep(3.0, reason="Before song parsing API request")
        try:
            response = self.session.post(
                f"{self.base_url}/Song_V1",
                data={'url': song_id, 'level': level, 'type': 'json'},
                timeout=DEFAULT_TIMEOUT
            )
            return _parse_json_response(response.text, "song parsing")
        except requests.RequestException as e:
            logger.error(f"Song parsing request failed: {e}")
            return None

    def parse_playlist(self, playlist_id_or_url: str) -> Optional[dict]:
        """Parse playlist information"""
        playlist_id = self._extract_id(playlist_id_or_url, 'playlist')
        if not playlist_id:
            logger.error(f"Invalid playlist ID or URL: {playlist_id_or_url}")
            return None
            
        from util_commons import random_sleep
        random_sleep(3.0, reason="Before playlist parsing API request")
        try:
            response = self.session.get(
                f"{self.base_url}/Playlist",
                params={'id': playlist_id},
                timeout=DEFAULT_TIMEOUT
            )
            logger.info("-" * 60)
            return _parse_json_response(response.text, "playlist parsing")
        except requests.RequestException as e:
            logger.error(f"Playlist parsing request failed: {e}")
            return None

    def parse_album(self, album_id_or_url: str, level: str = "lossless") -> Optional[dict]:
        """Parse album information"""
        album_id = self._extract_id(album_id_or_url, 'album')
        if not album_id:
            logger.error(f"Invalid album ID or URL: {album_id_or_url}")
            return None
            
        from util_commons import random_sleep
        random_sleep(3.0, reason="Before album parsing API request")
        try:
            response = self.session.get(
                f"{self.base_url}/Album",
                params={'id': album_id},
                timeout=DEFAULT_TIMEOUT
            )
            return _parse_json_response(response.text, "album parsing")
        except requests.RequestException as e:
            logger.error(f"Album parsing request failed: {e}")
            return None


def _parse_json_response(response_str: str, operation: str) -> Optional[dict]:
    """Generic JSON parsing function"""
    import json
    try:
        data = json.loads(response_str)
        if isinstance(data, dict):
            status = data.get('status')
            if status is not None and status != HTTP_OK:
                logger.warning(f"API returned non-OK status {status} during {operation}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed during {operation}: {str(e)}")
        if len(response_str) < 500:  # Only log short responses to avoid large logs
            logger.error(f"Raw response: {response_str}")
        return None


def _handle_429_error(response: requests.Response) -> bool:
    """Handle HTTP 429 error (Too Many Requests)"""
    if response.status_code == HTTP_TOO_MANY_REQUESTS:
        from util_commons import random_sleep
        random_sleep(min_delay=10.0, max_delay=15.0, reason="429 Too Many Requests - API rate limit")
        return True
    return False


def _handle_429_error_json(response_str: str) -> bool:
    """Handle 429 error in JSON response"""
    import json
    try:
        data = json.loads(response_str)
        if isinstance(data, dict) and '429' in data.get('message', ''):
            from util_commons import random_sleep
            random_sleep(min_delay=10.0, max_delay=15.0, reason="429 Too Many Requests - API rate limit")
            return True
    except (json.JSONDecodeError, ValueError):
        pass
    return False