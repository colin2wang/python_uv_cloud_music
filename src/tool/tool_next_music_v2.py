"""
NextMusic Tool - A class-based wrapper for NextMusic API with AES-GCM encryption
"""
import base64
import json
import os
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from curl_cffi import requests

from src.model.basic import MusicInfo, MusicURL
from src.util.util_commons import random_sleep
from src.util.util_database import MusicDB
from src.util.util_logging import setup_logger

# Create logger
logger = setup_logger(__name__)

MAX_RETRY = 5

HEADERS = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://wyapi.toubiec.cn',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}


class NextMusicToolV2:
    """NextMusic API tool for getting song URLs with AES-GCM encryption"""

    def __init__(self, db_path: str = None):
        """Initialize NextMusicToolV2 with database connection
        
        Args:
            db_path: Path to SQLite database file. Defaults to 'cloud-music.db'
        """
        self.db = MusicDB(db_path)
        logger.info("NextMusicToolV2 initialized with database caching")

    @staticmethod
    def encrypt_payload(payload: dict, base64_key: str) -> str:
        """Encrypt payload using AES-GCM"""
        payload['timestamp'] = int(time.time() * 1000)
        plain_text = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        key = base64.b64decode(base64_key)
        iv = os.urandom(12)
        aesgcm = AESGCM(key)
        encrypted = aesgcm.encrypt(iv, plain_text, None)

        cipher_text = encrypted[:-16]
        auth_tag = encrypted[-16:]

        return f"{base64.b64encode(iv).decode('utf-8')}.{base64.b64encode(auth_tag).decode('utf-8')}.{base64.b64encode(cipher_text).decode('utf-8')}"

    @staticmethod
    def decrypt_response(response_data: str, base64_key: str) -> dict:
        """Decrypt response using AES-GCM"""
        parts = response_data.split('.')
        iv = base64.b64decode(parts[0])
        auth_tag = base64.b64decode(parts[1])
        cipher_text = base64.b64decode(parts[2])
        key = base64.b64decode(base64_key)
        aesgcm = AESGCM(key)
        decrypted_bytes = aesgcm.decrypt(iv, cipher_text + auth_tag, None)
        return json.loads(decrypted_bytes.decode('utf-8'))

    def _fetch_session_key(self, attempt: int, max_retries: int) -> dict:
        """Fetch session key from NextMusic API
        
        Args:
            attempt: Current retry attempt number
            max_retries: Maximum retry count
            
        Returns:
            Dictionary containing key_id, key_token, and aes_key
        """
        logger.info(f"Attempt {attempt}/{max_retries} - Fetching session key...")
        # impersonate="chrome120" is the key! It makes the website firewall think this is a real Chrome browser request
        key_res = requests.post("https://nextmusic.toubiec.cn/api/key", headers=HEADERS, impersonate="chrome120")
        key_res.raise_for_status()

        key_info = key_res.json().get('data', {})
        key_id = key_info.get('keyId')
        key_token = key_info.get('keyToken')
        aes_key = key_info.get('key')
        logger.info(f"   [Success] Got KeyId: {key_id}")
        
        return {
            'key_id': key_id,
            'key_token': key_token,
            'aes_key': aes_key
        }

    def get_song_info(self, song_id: str, max_retries: int = MAX_RETRY) -> MusicInfo:
        """Get song info from NextMusic API with retry mechanism and database caching
        
        Returns:
            MusicInfo object containing music_id, artist, title, album
        """
        # Check database first
        try:
            song_id_int = int(song_id)
            cached_info = self.db.get_music_info(song_id_int)
            if cached_info:
                logger.info(f"Cache hit for song info (SongID: {song_id})")
                return MusicInfo.from_db_row(cached_info)
        except Exception as e:
            logger.warning(f"Failed to query cache: {str(e)}")
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                key_data = self._fetch_session_key(attempt, max_retries)

                logger.info(f"\nRequesting song info (SongID: {song_id})...")
                url_payload = {
                    "id": song_id
                }

                request_body = {
                    "keyId": key_data['key_id'],
                    "keyToken": key_data['key_token'],
                    "data": self.encrypt_payload(url_payload, key_data['aes_key'])
                }

                logger.debug(json.dumps(request_body, indent=2))
                song_res = requests.post("https://nextmusic.toubiec.cn/api/getSongInfo", json=request_body, headers=HEADERS,
                                         impersonate="chrome120")
                logger.debug(song_res.text)
                song_res.raise_for_status()
                response_json = song_res.json()

                if 'ciphertext' in response_json:
                    logger.info("\nServer returned ciphertext, decrypting...")
                    decrypted_data = self.decrypt_response(response_json['ciphertext'], key_data['aes_key'])
                    logger.info("\n==== Decryption Result [get_song_info] ====")
                    logger.info(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
                    # Extract model fields only, discard other values
                    data = decrypted_data.get('data', {})
                    result = MusicInfo(
                        music_id=int(data.get('id', song_id)),
                        artist=data.get('singer'),
                        title=data.get('name'),
                        album=data.get('album'),
                        cover_url=data.get('picimg'),  # API returns picimg field as cover URL
                        lyrics=None,  # Lyrics not included in song info
                        duration=data.get('duration')
                    )
                else:
                    logger.info("\n==== Parsing Result (Unencrypted) ====")
                    logger.info(json.dumps(response_json, indent=4, ensure_ascii=False))
                    # Extract model fields only, discard other values
                    data = response_json.get('data', {})
                    result = MusicInfo(
                        music_id=int(data.get('id', song_id)),
                        artist=data.get('singer'),
                        title=data.get('name'),
                        album=data.get('album'),
                        cover_url=data.get('picimg'),  # API returns picimg field as cover URL
                        lyrics=None,  # Lyrics not included in song info
                        duration=data.get('duration')
                    )
                
                # Save to database before returning
                try:
                    self.db.upsert_music_info(
                        music_id=result.music_id,
                        artists=result.artist,
                        title=result.title,
                        album_name=result.album,
                        cover_url=result.cover_url,
                        lyrics=result.lyrics,
                        duration=result.duration
                    )
                    logger.info(f"Saved song info to database (SongID: {result.music_id})")
                except Exception as e:
                    logger.error(f"Failed to save to database: {str(e)}")
                
                return result
                
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Waiting before retry...")
                    random_sleep(min_delay=10.0, max_delay=20.0, reason="Next Music Tool get_song_info retrying...")
                else:
                    logger.error(f"Maximum retry count reached ({max_retries})")
        
        logger.error(f"All retries failed, last error: {str(last_error)}")
        return None

    def get_song_lyric(self, song_id: str, max_retries: int = MAX_RETRY) -> str:
        """Get song lyric from NextMusic API with retry mechanism and database caching
        
        Returns:
            Lyric string, or None if not found
        """
        # Check database first
        try:
            song_id_int = int(song_id)
            cached_info = self.db.get_music_info(song_id_int)
            if cached_info and cached_info.get('lyrics'):
                logger.info(f"Cache hit for song lyric (SongID: {song_id})")
                return cached_info['lyrics']
        except Exception as e:
            logger.warning(f"Failed to query cache: {str(e)}")
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                logger.info(f"Retrying... (Attempt {attempt}/{max_retries})")
                random_sleep(min_delay=30.0, max_delay=35.0, reason="Next Music Tool fetching song lyric retrying...")

            try:
                random_sleep(max_delay=3.0, reason="Next Music Tool fetching song lyric")
                key_data = self._fetch_session_key(attempt, max_retries)

                logger.info(f"\nRequesting song lyric (SongID: {song_id})...")
                lyric_payload = {
                    "id": song_id
                }

                request_body = {
                    "keyId": key_data['key_id'],
                    "keyToken": key_data['key_token'],
                    "data": self.encrypt_payload(lyric_payload, key_data['aes_key'])
                }

                logger.debug(json.dumps(request_body, indent=2))
                lyric_res = requests.post("https://nextmusic.toubiec.cn/api/getSongLyric", json=request_body, headers=HEADERS,
                                         impersonate="chrome120")
                logger.debug(lyric_res.text)
                lyric_res.raise_for_status()
                response_json = lyric_res.json()

                if 'ciphertext' in response_json:
                    logger.info("\nServer returned ciphertext, decrypting...")
                    decrypted_data = self.decrypt_response(response_json['ciphertext'], key_data['aes_key'])
                    logger.info("\n==== Decryption Result [get_song_lyric] ====")
                    logger.info(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
                    # Extract lyric only, discard other values
                    data = decrypted_data.get('data', {})
                    lyric = data.get('lrc')
                else:
                    logger.info("\n==== Parsing Result (Unencrypted) ====")
                    logger.info(json.dumps(response_json, indent=4, ensure_ascii=False))
                    # Extract lyric only, discard other values
                    data = response_json.get('data', {})
                    lyric = data.get('lrc')
                
                # Save lyric to database before returning
                if lyric:
                    try:
                        song_id_int = int(song_id)
                        self.db.upsert_music_info(music_id=song_id_int, lyrics=lyric)
                        logger.info(f"Saved song lyric to database (SongID: {song_id_int})")
                    except Exception as e:
                        logger.error(f"Failed to save lyric to database: {str(e)}")
                
                return lyric
                
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                # if attempt < max_retries:
                #     logger.info(f"Waiting before retry...")
                #     random_sleep(min_delay=10.0, max_delay=20.0, reason="Next Music Tool get_song_lyric retrying...")
                # else:
                #     logger.error(f"Maximum retry count reached ({max_retries})")
        
        logger.error(f"All retries failed, last error: {str(last_error)}")
        return None

    def get_song_url(self, song_id: str, level: str = "lossless", max_retries: int = MAX_RETRY) -> MusicURL:
        """Get song URL from NextMusic API with retry mechanism and database caching
        
        Returns:
            MusicURL object containing music_id, quality, and url
        """
        # Check database first
        try:
            song_id_int = int(song_id)
            cached_url = self.db.get_music_url(song_id_int, level)
            if cached_url:
                logger.info(f"Cache hit for song URL (SongID: {song_id}, Quality: {level})")
                return MusicURL(music_id=song_id_int, quality=level, url=cached_url)
        except Exception as e:
            logger.warning(f"Failed to query cache: {str(e)}")
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                logger.info(f"Retrying... (Attempt {attempt}/{max_retries})")
                random_sleep(min_delay=30.0, max_delay=35.0, reason="Next Music Tool fetching song lyric retrying...")

            try:
                random_sleep(max_delay=3.0, reason="Next Music Tool fetching song playback URL")
                key_data = self._fetch_session_key(attempt, max_retries)

                logger.info(f"\nRequesting song playback URL (SongID: {song_id})...")
                url_payload = {
                    "id": song_id,
                    "level": level
                }

                request_body = {
                    "keyId": key_data['key_id'],
                    "keyToken": key_data['key_token'],
                    "data": self.encrypt_payload(url_payload, key_data['aes_key'])
                }

                logger.debug(json.dumps(request_body, indent=2))
                song_res = requests.post("https://nextmusic.toubiec.cn/api/getSongUrl", json=request_body, headers=HEADERS,
                                         impersonate="chrome120")
                logger.debug(song_res.text)
                song_res.raise_for_status()
                response_json = song_res.json()

                if 'ciphertext' in response_json:
                    logger.info("\nServer returned ciphertext, decrypting...")
                    decrypted_data = self.decrypt_response(response_json['ciphertext'], key_data['aes_key'])
                    logger.info("\n==== Decryption Result [get_song_url] ====")
                    logger.info(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
                    if 'data' in decrypted_data and 'url' in decrypted_data['data']:
                        logger.info(f"\nSong direct URL obtained successfully: {decrypted_data['data']['url']}")
                        # Extract model fields only, discard other values (size, etc.)
                        data = decrypted_data['data']
                        result = MusicURL(
                            music_id=int(data.get('id', song_id)),
                            quality=data.get('level', level),
                            url=data.get('url')
                        )
                        
                        # Save to database before returning
                        try:
                            self.db.upsert_music_url(
                                music_id=result.music_id,
                                quality=result.quality,
                                url=result.url
                            )
                            logger.info(f"Saved song URL to database (SongID: {result.music_id}, Quality: {result.quality})")
                        except Exception as e:
                            logger.error(f"Failed to save URL to database: {str(e)}")
                        
                        return result
                else:
                    logger.info("\n==== Parsing Result (Unencrypted) [get_song_url] ====")
                    logger.info(json.dumps(response_json, indent=4, ensure_ascii=False))
                    # Extract model fields only, discard other values
                    data = response_json.get('data', {})
                    result = MusicURL(
                        music_id=int(data.get('id', song_id)),
                        quality=data.get('level', level),
                        url=data.get('url')
                    )
                    
                    # Save to database before returning
                    try:
                        self.db.upsert_music_url(
                            music_id=result.music_id,
                            quality=result.quality,
                            url=result.url
                        )
                        logger.info(f"Saved song URL to database (SongID: {result.music_id}, Quality: {result.quality})")
                    except Exception as e:
                        logger.error(f"Failed to save URL to database: {str(e)}")
                    
                    return result

                return None
                
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                # if attempt < max_retries:
                #     logger.info(f"Waiting before retry...")
                #     random_sleep(min_delay=10.0, max_delay=20.0, reason="Next Music Tool get_song_url retrying...")
                # else:
                #     logger.error(f"Maximum retry count reached ({max_retries})")
        
        logger.error(f"All retries failed, last error: {str(last_error)}")
        return None


if __name__ == "__main__":
    # Initialize the tool
    tool = NextMusicToolV2()

    # Get song URL (use standard quality as default safe test)
    song_id = "1832966854"
    result_1 = tool.get_song_info(song_id)
    logger.info(f"Song info: {result_1}")

    result_2 = tool.get_song_lyric(song_id)  # Test the new lyric method
    logger.info(f"Song lyric: {result_2}")

    result_3 = tool.get_song_url(song_id, level="standard")
    logger.info(f"Song URL: {result_3}")

