import json
import os
import random
import re
import time
import urllib.parse
from pathlib import Path

import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, COMM, TYER
from mutagen.mp4 import MP4, MP4Cover

from config_manager import config
from logging_config import setup_logger
from tool_next_music import NextMusicTool
from utils import (
    get_audio_extension, get_image_mime_type,
    get_mp4_image_format, clean_filename
)

# Create logger
logger = setup_logger(__name__)


class MusicToolAPI:
    """
    Music API Client

    Provides methods to interact with the music source API,
    including search, song parsing, playlist parsing, and album parsing.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize the Music API client.

        Args:
            base_url: Base URL for the API endpoint (default: from config)
        """
        self.base_url = (base_url or config.get_api_base_url()).rstrip('/')
        self.session = requests.Session()
        
        # Set browser-simulated request headers (excluding HTTP/2 pseudo-headers)
        self.session.headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': base_url,
            'priority': 'u=1, i',
            'referer': base_url,
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        })

    def _extract_id(self, text: str, pattern_type: str = 'song') -> str:
        """
        Extract ID from URL or text

        Args:
            text: Input text which may contain a URL or ID
            pattern_type: Type of pattern to match ('song', 'playlist', or 'album')

        Returns:
            Extracted numeric ID or original text if no ID found
        """
        text = str(text) if text is not None else ""
        if not text:
            return text

        patterns = {
            'song': r'song\?id=(\d+)',
            'playlist': r'playlist\?id=(\d+)',
            'album': r'album\?id=(\d+)'
        }

        if 'music.163.com' in text or '163cn.tv' in text:
            pattern = patterns.get(pattern_type, r'id=(\d+)')
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        if text.isdigit():
            return text

        return text

    # ==================== 1. Search Function ====================

    def search(self, keyword: str, limit: int = 10) -> str:
        """
        Search for songs by keyword

        Args:
            keyword: Search term to find songs
            limit: Maximum number of results to return (default: 10)

        Returns:
            JSON response string containing search results
        """

        random_sleep(5.0)
        response = self.session.post(
            f"{self.base_url}/Search",
            data={'keyword': keyword, 'limit': limit}
        )
        return response.text

    # ==================== 2. Single Song Parsing ====================

    def parse_song(self, song_id_or_url: str, level: str = "lossless") -> str:
        """
        Parse song details from ID or URL

        Args:
            song_id_or_url: Song ID or URL to parse
            level: Audio quality level ('lossless', 'exhigh', 'standard', etc.)

        Returns:
            JSON response string containing song details
        """
        song_id = self._extract_id(song_id_or_url, 'song')

        random_sleep(3.0)
        response = self.session.post(
            f"{self.base_url}/Song_V1",
            data={'url': song_id, 'level': level, 'type': 'json'}
        )
        return response.text

    # ==================== 3. Playlist Parsing ====================

    def parse_playlist(self, playlist_id_or_url: str) -> str:
        """
        Parse playlist details from ID or URL

        Args:
            playlist_id_or_url: Playlist ID or URL to parse

        Returns:
            JSON response string containing playlist details
        """
        playlist_id = self._extract_id(playlist_id_or_url, 'playlist')

        random_sleep(3.0)
        response = self.session.get(
            f"{self.base_url}/Playlist",
            params={'id': playlist_id}
        )
        logger.info("-" * 60)
        return response.text

    # ==================== 4. Album Parsing ====================

    def parse_album(self, album_id_or_url: str) -> str:
        """
        Parse album details from ID or URL

        Args:
            album_id_or_url: Album ID or URL to parse

        Returns:
            JSON response string containing album details
        """
        album_id = self._extract_id(album_id_or_url, 'album')

        random_sleep(3.0)
        response = self.session.get(
            f"{self.base_url}/Album",
            params={'id': album_id}
        )
        return response.text


# ==================== Usage Examples ====================

# Define quality level list that will be try if fail with input level (in order of preference)
# TRY_QUALITY_LEVELS = ["lossless", "exhigh", "standard"]
TRY_QUALITY_LEVELS = ["standard"]

def random_sleep(max_delay: float = None):
    """
    Add random delay to avoid frequent requests

    Args:
        max_delay: Maximum delay in seconds (default: from config)
    """
    if max_delay is None:
        max_delay = config.get_random_delay_max()
    delay = random.uniform(1.0, max_delay)
    logger.info(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


def get_song_ids_by_playlist_id(playlist_id: str) -> dict:
    """
    Extract song IDs from playlist ID.

    Args:
        playlist_id: Playlist ID (e.g., "70512345")

    Returns:
        Dictionary containing playlist information and song ID list
    """
    api = MusicToolAPI(config.get_api_base_url())

    logger.info("=" * 60)
    logger.info("Extract Songs from Playlist ID")
    logger.info("=" * 60)
    logger.info(f"Playlist ID: {playlist_id}")
    logger.info("-" * 60)

    # Call playlist parsing interface
    playlist_result_str = api.parse_playlist(playlist_id)

    try:
        playlist_result = json.loads(playlist_result_str)

        if playlist_result.get('status') != 200:
            logger.error(f"\nPlaylist parsing failed: {playlist_result.get('message', 'Unknown error')}")
            return {
                "success": False,
                "message": playlist_result.get('message', 'Playlist parsing failed'),
                "playlist_id": playlist_id
            }

        # Extract playlist data section
        data_section = playlist_result.get('data', {})
        if not data_section:
            logger.error(f"\nData section not found")
            return {"success": False, "message": "Data section not found", "playlist_id": playlist_id}

        playlist_info = data_section.get('playlist', {})
        if not playlist_info:
            logger.error(f"\nPlaylist info not found")
            return {"success": False, "message": "Playlist info not found", "playlist_id": playlist_id}

        playlist_name = playlist_info.get('name', 'Unknown Playlist')
        playlist_creator = playlist_info.get('creator', 'Unknown Creator')
        track_count = playlist_info.get('trackCount', 0)
        song_list = playlist_info.get('tracks', [])

        logger.info(f"\nPlaylist parsed successfully!")
        logger.info(f"Playlist Name: {playlist_name}")
        logger.info(f"Creator: {playlist_creator}")
        logger.info(f"Track Count: {len(song_list)}")
        logger.info("-" * 60)

        # Extract all song IDs
        song_ids = []
        song_details = []

        for i, song in enumerate(song_list, 1):
            song_id = song.get('id')
            song_name = song.get('name', 'Unknown Song')
            # Handle artist information
            song_artists = song.get('artists', 'Unknown Artist')

            if song_id:
                song_ids.append(str(song_id))
                song_details.append({
                    "id": str(song_id),
                    "name": song_name,
                    "artists": song_artists,
                    "index": i
                })
                logger.info(f"{i:2d}. [{song_id}] {song_name} - {song_artists}")
            else:
                logger.warning(f"{i:2d}. Invalid song data: {song}")

        result = {
            "success": True,
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "playlist_creator": playlist_creator,
            "song_count": len(song_ids),
            "song_ids": song_ids,
            "song_details": song_details,
            "raw_data": playlist_result
        }

        logger.info(f"\nSuccessfully extracted {len(song_ids)} song IDs")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"\nJSON parsing failed: {str(e)}")
        return {"success": False, "message": f"JSON parsing failed: {str(e)}", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"\nError occurred during processing: {str(e)}")
        return {"success": False, "message": f"Processing failed: {str(e)}", "playlist_id": playlist_id}


def get_song_ids_by_album_id(album_id: str) -> dict:
    """
    Extract song IDs from album ID.

    Args:
        album_id: Album ID (e.g., "361790100")

    Returns:
        Dictionary containing album information and song ID list
    """
    api = MusicToolAPI(config.get_api_base_url())

    logger.info("=" * 60)
    logger.info("Extract Songs from Album ID")
    logger.info("=" * 60)
    logger.info(f"Album ID: {album_id}")
    logger.info("-" * 60)

    # Call album parsing interface
    album_result_str = api.parse_album(album_id)

    try:
        album_result = json.loads(album_result_str)

        if album_result.get('status') != 200:
            logger.error(f"\nAlbum parsing failed: {album_result.get('message', 'Unknown error')}")
            return {
                "success": False,
                "message": album_result.get('message', 'Album parsing failed'),
                "album_id": album_id
            }

        # Extract album data
        album_data = album_result.get('data', {}).get('album', {})
        if not album_data:
            logger.error(f"\nAlbum data not found")
            return {"success": False, "message": "Album data not found", "album_id": album_id}

        album_name = album_data.get('name', 'Unknown Album')
        album_artist = album_data.get('artist', 'Unknown Artist')
        album_publish_time = album_data.get('publishTime')
        song_list = album_data.get('songs', [])

        logger.info(f"\nAlbum parsed successfully!")
        logger.info(f"Album Name: {album_name}")
        logger.info(f"Artist: {album_artist}")
        if album_publish_time:
            publish_date = time.strftime('%Y-%m-%d', time.localtime(album_publish_time / 1000))
            logger.info(f"Publish Date: {publish_date}")
        logger.info(f"Song Count: {len(song_list)}")
        logger.info("-" * 60)

        # Extract all song IDs
        song_ids = []
        song_details = []

        for i, song in enumerate(song_list, 1):
            song_id = song.get('id')
            song_name = song.get('name', 'Unknown Song')
            song_artists = song.get('artists', 'Unknown Artist')

            if song_id:
                song_ids.append(str(song_id))
                song_details.append({
                    "id": str(song_id),
                    "name": song_name,
                    "artists": song_artists,
                    "index": i
                })
                logger.info(f"{i:2d}. [{song_id}] {song_name} - {song_artists}")
            else:
                logger.warning(f"{i:2d}. Invalid song data: {song}")

        result = {
            "success": True,
            "album_id": album_id,
            "album_name": album_name,
            "album_artist": album_artist,
            "album_publish_time": album_publish_time,
            "song_count": len(song_ids),
            "song_ids": song_ids,
            "song_details": song_details,
            "raw_data": album_result
        }

        logger.info(f"\nSuccessfully extracted {len(song_ids)} song IDs")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"\nJSON parsing failed: {str(e)}")
        return {"success": False, "message": f"JSON parsing failed: {str(e)}", "album_id": album_id}
    except Exception as e:
        logger.error(f"\nError occurred during processing: {str(e)}")
        return {"success": False, "message": f"Processing failed: {str(e)}", "album_id": album_id}


def get_song_metadata_by_song_id(song_id: str, level: str = "lossless") -> dict:
    """
    Extract song information by song ID.

    Args:
        song_id: Song ID (e.g., "186016")
        level: Quality level (standard, exhigh, lossless, hires)

    Returns:
        Dictionary containing detailed song information with download links
    """
    try:
        api = MusicToolAPI(config.get_api_base_url())

        try_quality_level = config.get_default_quality()

        # Use default quality from config if not specified
        if level is None:
            try_quality_level = level

        # Get max retries from config
        max_retries = config.get_max_retries()

        logger.info("=" * 60)
        logger.info("Extract Song Metadata by Song ID")
        logger.info("=" * 60)
        logger.info(f"Song ID: {song_id}")
        logger.info(f"Quality Level: {level}")
        logger.info(f"Max Retries: {max_retries}")
        logger.info("-" * 60)

        result = None
        used_level = None

        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                if retry_count > 0:
                    logger.info(f"Retry {retry_count}/{max_retries} for quality {try_quality_level}...")
                    random_sleep()

                result_str = api.parse_song(song_id, try_quality_level)

                try:
                    result_json = json.loads(result_str)

                    # Replace url using Next Music Tool
                    next_music_tool = NextMusicTool()
                    # next_music_tool = NextMusicTool(token=NEXT_MUSIC_TOKEN)
                    response = next_music_tool.get_song_url(song_id, try_quality_level)
                    result_json['data']['url'] = response.get('data', {}).get('url')
                    result_json['data']['level'] = response.get('data', {}).get('level')
                    result_json['data']['size'] = response.get('data', {}).get('size')

                    if result_json.get('status') == 200 and result_json.get('data', {}).get('url'):
                        # Set result first
                        result = result_json

                        # Check if actual quality matches requested quality
                        actual_level = result_json.get('data', {}).get('level', '')
                        if actual_level and actual_level != try_quality_level:
                            logger.warning(
                                f"Quality mismatch: expected: [{try_quality_level}], actual: [{actual_level}]. Retrying...")
                            retry_count += 1
                            continue

                        used_level = try_quality_level
                        logger.info(f"Found available quality: {try_quality_level}")
                        success = True
                        break
                    else:
                        error_msg = result_json.get('data', {}).get('msg', 'Unknown reason')
                        logger.warning(
                            f"Quality {try_quality_level} not available (attempt {retry_count + 1}): {error_msg}")
                        # Retry for temporary failures, but not for permanent unavailability
                        if retry_count < max_retries:
                            retry_count += 1
                            continue
                        else:
                            # Max retries reached, move to next quality level
                            break
                except json.JSONDecodeError:
                    logger.error(f"Quality {try_quality_level} parsing failed (attempt {retry_count + 1})")
                    retry_count += 1
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Network request failed (Quality {try_quality_level}, attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                continue
            except Exception as e:
                logger.error(
                    f"Unknown error occurred while getting quality {try_quality_level} (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                continue

        if not result:
            return {"success": False, "message": "No available quality", "tried_levels": TRY_QUALITY_LEVELS}

        if result and result.get('status') == 200:
            data = result['data']
            logger.info(f"\nExtraction successful!\n")
            logger.info(f"Song Name: {data['name']}")
            logger.info(f"Artist: {data['ar_name']}")
            logger.info(f"Album: {data['al_name']}")
            logger.info(f"Actual quality: {used_level or data['level']}")
            logger.info(f"File Size: {data['size']}")
            logger.info(f"Download/Play URL: {data['url']}")
            logger.info(f"Cover Image: {data['pic']}")

            # Return actually used quality
            result['used_quality'] = used_level or data['level']

            if data.get('lyric'):
                logger.info(f"\nLyrics:")
                logger.info(data['lyric'][:500] + "..." if len(data['lyric']) > 500 else data['lyric'])

            return result
        else:
            logger.error(f"\nExtraction failed: {result.get('data', {}).get('msg', 'Unknown error')}")
            return result

    except Exception as e:
        logger.error(f"Critical error occurred while getting song metadata: {str(e)}")
        return {"success": False, "message": f"Failed to get metadata: {str(e)}", "song_id": song_id}


def _write_mp3_metadata(audio_file: ID3, metadata: dict) -> None:
    """Write metadata to MP3 file."""
    song_name = metadata.get('name', '')
    artist = metadata.get('ar_name', '').split(',')
    album = metadata.get('al_name', '')
    lyric = metadata.get('lyric', '')
    cover_path = metadata.get('cover_path', '')
    track_number = metadata.get('track_number', '')
    song_id = metadata.get('id', '')

    # Title
    if song_name:
        audio_file.add(TIT2(encoding=3, text=song_name))

    # Artist
    if artist:
        audio_file.add(TPE1(encoding=3, text=artist))

    # Album
    if album:
        audio_file.add(TALB(encoding=3, text=album))

    # Year
    audio_file.add(TYER(encoding=3, text=str(time.localtime().tm_year)))

    # Track number
    if track_number:
        from mutagen.id3 import TRCK
        audio_file.add(TRCK(encoding=3, text=track_number))

    # NetEase Cloud Music Song ID
    if song_id:
        from mutagen.id3 import TXXX
        audio_file.add(TXXX(encoding=3, desc='CMUSIC_ID', text=song_id))

    # Comments (lyrics)
    # Note: Use encoding=1 (UTF-16 with BOM) to properly preserve newlines in lyrics
    if lyric:
        audio_file.add(COMM(encoding=1, lang='eng', desc='', text=lyric))

    # Cover image
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, 'rb') as img_file:
                img_data = img_file.read()
                audio_file.add(APIC(
                    encoding=3,
                    mime=get_image_mime_type(cover_path),
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=img_data
                ))
        except Exception as e:
            logger.warning(f"Cover image writing failed: {e}")


def _write_flac_metadata(audio_file: FLAC, metadata: dict) -> None:
    """Write metadata to FLAC file."""
    song_name = metadata.get('name', '')
    artist = metadata.get('ar_name', '').split(',')
    album = metadata.get('al_name', '')
    lyric = metadata.get('lyric', '')
    cover_path = metadata.get('cover_path', '')
    track_number = metadata.get('track_number', '')
    song_id = metadata.get('id', '')

    if song_name:
        audio_file['TITLE'] = song_name
    if artist:
        audio_file['ARTIST'] = artist
    if album:
        audio_file['ALBUM'] = album
    if lyric:
        audio_file['LYRICS'] = lyric
    if track_number:
        audio_file['TRACKNUMBER'] = track_number
    if song_id:
        audio_file['CMUSIC_ID'] = song_id

    # Add cover
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, 'rb') as img_file:
                img_data = img_file.read()
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = get_image_mime_type(cover_path)
                picture.data = img_data
                audio_file.add_picture(picture)
        except Exception as e:
            logger.warning(f"Cover image writing failed: {e}")


def _write_mp4_metadata(audio_file: MP4, metadata: dict) -> None:
    """Write metadata to MP4/AAC file."""
    song_name = metadata.get('name', '')
    artist = metadata.get('ar_name', '').split(',')
    album = metadata.get('al_name', '')
    lyric = metadata.get('lyric', '')
    cover_path = metadata.get('cover_path', '')
    track_number = metadata.get('track_number', '')
    song_id = metadata.get('id', '')

    # Create metadata dictionary
    mp4_tags = {}

    if song_name:
        mp4_tags['\xa9nam'] = song_name
    if artist:
        mp4_tags['\xa9ART'] = artist
    if album:
        mp4_tags['\xa9alb'] = album
    if lyric:
        mp4_tags['\xa9lyr'] = lyric[:config.get_max_lyric_length()]
    if track_number:
        mp4_tags['trkn'] = [(int(track_number), 0)]
    if song_id:
        mp4_tags['----:CMUSIC_ID'] = song_id.encode('utf-8')

    # Add cover
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, 'rb') as img_file:
                img_data = img_file.read()
                mp4_tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path))]
        except Exception as e:
            logger.warning(f"Cover image writing failed: {e}")

    if audio_file.tags is None:
        audio_file.add_tags()
    audio_file.tags.update(mp4_tags)


def write_metadata_to_file(file_path: str | Path, metadata: dict) -> bool:
    """
    Write metadata to audio file.

    Args:
        file_path: Audio file path
        metadata: Dictionary containing song information metadata

    Returns:
        bool: Whether writing was successful
    """
    file_path = Path(file_path)
    ext = get_audio_extension(file_path)

    logger.info(f"Writing metadata to {file_path.name}...")

    try:
        match ext:
            case '.mp3' | '.mp2' | '.mp1':
                audio_file = ID3(file_path)
                _write_mp3_metadata(audio_file, metadata)
                audio_file.save()
            case '.flac':
                audio_file = FLAC(file_path)
                _write_flac_metadata(audio_file, metadata)
                audio_file.save()
            case '.m4a' | '.mp4' | '.aac':
                audio_file = MP4(file_path)
                _write_mp4_metadata(audio_file, metadata)
                audio_file.save()
            case _:
                logger.warning(f"Unsupported file format: {ext}")
                return False

        logger.info("Metadata written successfully!")
        return True

    except Exception as e:
        logger.error(f"Metadata writing failed: {e}")
        return False


def _write_mp3_cover(audio_file: ID3, cover_path: str | Path) -> None:
    """Write cover image to MP3 file."""
    with open(cover_path, 'rb') as img_file:
        img_data = img_file.read()
        audio_file.add(APIC(
            encoding=3,
            mime=get_image_mime_type(cover_path),
            type=3,  # Cover (front)
            desc='Cover',
            data=img_data
        ))


def _write_flac_cover(audio_file: FLAC, cover_path: str | Path) -> None:
    """Write cover image to FLAC file."""
    with open(cover_path, 'rb') as img_file:
        img_data = img_file.read()
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.mime = get_image_mime_type(cover_path)
        picture.data = img_data
        audio_file.add_picture(picture)


def _write_mp4_cover(audio_file: MP4, cover_path: str | Path) -> None:
    """Write cover image to MP4/AAC file."""
    with open(cover_path, 'rb') as img_file:
        img_data = img_file.read()
        if audio_file.tags is None:
            audio_file.add_tags()
        audio_file.tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path))]


def write_picture_to_file(file_path: str | Path) -> bool:
    """
    Write image file in the same directory to audio file.

    Args:
        file_path: Audio file path

    Returns:
        bool: Whether writing was successful
    """
    file_path = Path(file_path)
    file_dir = file_path.parent
    file_base_name = file_path.stem

    # Look for image files with the same name
    cover_path = None
    for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        potential_cover = file_dir / f"{file_base_name}{ext}"
        if potential_cover.exists():
            cover_path = potential_cover
            logger.info(f"Found cover image: {cover_path.name}")
            break

    if not cover_path:
        logger.warning("No image file found with the same name")
        return False

    ext = get_audio_extension(file_path)
    logger.info(f"Writing image to {file_path.name}...")

    try:
        match ext:
            case '.mp3' | '.mp2' | '.mp1':
                audio_file = ID3(file_path)
                _write_mp3_cover(audio_file, cover_path)
                audio_file.save()
                logger.info("MP3 cover image written successfully!")
            case '.flac':
                audio_file = FLAC(file_path)
                _write_flac_cover(audio_file, cover_path)
                audio_file.save()
                logger.info("FLAC cover image written successfully!")
            case '.m4a' | '.mp4' | '.aac':
                audio_file = MP4(file_path)
                _write_mp4_cover(audio_file, cover_path)
                audio_file.save()
                logger.info("MP4/AAC cover image written successfully!")
            case _:
                logger.warning(f"Unsupported file format: {ext}")
                return False
        return True

    except Exception as e:
        logger.error(f"Cover image writing failed: {e}")
        return False


def _extract_file_extension(download_url: str) -> str:
    """Extract file extension from download URL."""
    file_extension = ".mp3"  # Default extension

    parsed_url = urllib.parse.urlparse(download_url)
    path_parts = parsed_url.path.split('/')

    if path_parts:
        last_part = path_parts[-1]
        if '.' in last_part:
            file_extension = Path(last_part).suffix.lower()

    # Try to extract from query parameters
    if file_extension == ".mp3":
        query_params = urllib.parse.parse_qs(parsed_url.query)
        v_param = query_params.get('v', [''])[0]
        if v_param and '.' in v_param:
            ext_from_v = Path(v_param).suffix.lower()
            if ext_from_v in {'.flac', '.wav', '.aac', '.m4a'}:
                file_extension = ext_from_v

    return file_extension


def _build_filename(song_name: str, artist: str, idx: int | None) -> str:
    """Build filename with optional index."""
    safe_song_name = clean_filename(song_name)
    safe_artist = clean_filename(artist)

    add_index = config.should_add_index()
    index_format = config.get_index_format()

    if idx is not None and add_index:
        formatted_index = f"{idx:{index_format}}"
        filename = f"{formatted_index} - {safe_artist} - {safe_song_name}"
    else:
        filename = f"{safe_artist} - {safe_song_name}"

    # Truncate if too long
    max_filename_length = 200
    if len(filename) > max_filename_length:
        logger.warning(f"Filename too long ({len(filename)} chars), truncating")
        if idx is not None and add_index:
            formatted_index = f"{idx:{index_format}}"
            available_length = max_filename_length - len(formatted_index) - 4
            total_original = len(safe_artist) + len(safe_song_name)
            if total_original > 0:
                artist_ratio = len(safe_artist) / total_original
                max_artist_len = int(available_length * artist_ratio * 0.5)
                max_song_len = available_length - max_artist_len - 3
                safe_artist = safe_artist[:max_artist_len]
                safe_song_name = safe_song_name[:max_song_len]
            filename = f"{formatted_index} - {safe_artist} - {safe_song_name}"
        else:
            filename = filename[:max_filename_length]

    return filename


def download_song_and_resources(
    song_metadata: dict,
    download_dir: str | None = None,
    idx: int | None = None
) -> bool:
    """
    Download song file and related resources (lyrics, cover).

    Args:
        song_metadata: Song metadata dictionary
        download_dir: Download directory path
        idx: Track index for filename

    Returns:
        bool: Whether download was successful
    """
    if not song_metadata or not song_metadata.get('success', True):
        logger.error("Invalid song metadata")
        return False

    data = song_metadata['data']
    download_url = data['url']

    if not download_url:
        logger.error("No download URL in metadata")
        return False

    # Setup paths
    download_dir = download_dir or config.get_download_dir()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # Build filename
    filename = _build_filename(data['name'], data['ar_name'], idx)
    file_extension = _extract_file_extension(download_url)

    music_file_path = Path(download_dir) / f"{filename}{file_extension}"
    lyric_file_path = Path(download_dir) / f"{filename}.lrc"
    cover_file_path = Path(download_dir) / f"{filename}.jpg"

    logger.info(f"Detected file format: {file_extension}")

    # Skip if already exists
    if music_file_path.exists():
        logger.info(f"File already exists, skipping: {music_file_path.name}")
        return True

    logger.info(f"Starting download: {filename}")
    logger.info(f"File size: {data.get('size', 'Unknown')}")
    logger.info(f"Quality: {song_metadata.get('used_quality', data.get('level', 'unknown'))}")
    logger.info("-" * 60)

    # Download music file
    logger.info("Downloading music file...")
    random_sleep()
    try:
        response = requests.get(download_url, stream=True, timeout=config.get_timeout())
        response.raise_for_status()
        with open(music_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Music file downloaded: {music_file_path.name}")
    except requests.RequestException as e:
        logger.error(f"Music file download failed: {e}")
        return False

    # Prepare metadata for tagging
    metadata_for_tagging = data.copy()
    metadata_for_tagging['cover_path'] = str(cover_file_path) if cover_file_path.exists() else ''
    if idx is not None:
        metadata_for_tagging['track_number'] = str(idx)

    # Write metadata
    logger.info("\nWriting metadata...")
    if config.should_write_metadata():
        if write_metadata_to_file(music_file_path, metadata_for_tagging):
            logger.info(f"Metadata attached: {music_file_path.name}")
        else:
            logger.warning("Metadata writing failed, retrying...")
            for retry_count in range(3):
                logger.info(f"Retry {retry_count + 1}/3...")
                if write_metadata_to_file(music_file_path, metadata_for_tagging):
                    break

    # Download lyrics
    lyric = data.get('lyric', '')
    if lyric and config.should_write_lyrics():
        logger.info("Saving lyrics...")
        try:
            with open(lyric_file_path, 'w', encoding='utf-8') as f:
                f.write(lyric)
            logger.info(f"Lyrics saved: {lyric_file_path.name}")
        except IOError as e:
            logger.warning(f"Lyrics saving failed: {e}")
    else:
        logger.warning("No lyrics found")

    # Download cover
    cover_url = data.get('pic', '')
    if cover_url and config.should_write_cover():
        logger.info("Downloading cover...")
        random_sleep()
        try:
            cover_response = requests.get(f"{cover_url}?param=320x320", timeout=10)
            cover_response.raise_for_status()
            with open(cover_file_path, 'wb') as f:
                f.write(cover_response.content)
            logger.info(f"Cover downloaded: {cover_file_path.name}")
        except requests.RequestException as e:
            logger.warning(f"Cover download failed: {e}")
    else:
        logger.warning("No cover found")

    # Embed cover
    if config.should_write_cover():
        logger.info("Adding cover to song file...")
        write_picture_to_file(music_file_path)

    logger.info(f"\nDownload completed! Files saved in: {download_dir}")
    return True


def download_song(song_id: str, level: str = "lossless"):
    if level is None:
        level = config.get_default_quality()
    metadata = get_song_metadata_by_song_id(song_id, level)
    download_song_and_resources(metadata, idx=None)


def prepare_album_folder(album_metadata: dict, download_dir: str | None = None) -> str | None:
    """
    Create album folder with description file and cover image

    Args:
        album_metadata: Dictionary containing album information
        download_dir: Base download directory path

    Returns:
        Path to the created album folder
    """
    try:
        # Use default download directory from config if not specified
        if download_dir is None:
            download_dir = config.get_download_dir()

        # Get album information
        album_name = album_metadata.get('album_name', 'Unknown Album')
        album_artist = album_metadata.get('album_artist', 'Unknown Artist')
        album_id = album_metadata.get('album_id', '')
        album_publish_time = album_metadata.get('album_publish_time')
        song_count = album_metadata.get('song_count', 0)
        raw_data = album_metadata.get('raw_data', {})

        # Convert publish timestamp to formatted date
        publish_date_str = ''
        if album_publish_time:
            try:
                publish_date_str = time.strftime('%Y-%m-%d', time.localtime(album_publish_time / 1000))
            except (ValueError, OSError):
                logger.warning(f"Could not convert publish time: {album_publish_time}")

        # Get album description from raw data
        album_description = ''
        try:
            album_description = raw_data.get('data', {}).get('album', {}).get('description', '')
        except (AttributeError, KeyError):
            logger.warning(f"Could not extract album description")

        # Get album cover URL from raw data
        album_cover_url = ''
        try:
            album_cover_url = raw_data.get('data', {}).get('album', {}).get('coverImgUrl', '')
            album_cover_url = album_cover_url.split('?')[0]
            logger.info(f"Album cover URL: {album_cover_url}")
        except (AttributeError, KeyError):
            logger.warning(f"Could not extract album cover URL")

        # Clean illegal characters from folder name
        safe_album_name = clean_filename(album_name)
        safe_artist = clean_filename(album_artist)

        # Create album folder name: Artist - Album Name (yyyy-MM-dd)
        if publish_date_str:
            album_folder_name = f"{safe_artist} - {safe_album_name} ({publish_date_str})"
        else:
            album_folder_name = f"{safe_artist} - {safe_album_name}"
        album_folder_path = os.path.join(download_dir, album_folder_name)

        # Create album folder
        os.makedirs(album_folder_path, exist_ok=True)
        logger.info(f"Created album folder: {album_folder_path}")

        # Create description file
        description_file_path = os.path.join(album_folder_path, 'album_info.txt')
        try:
            with open(description_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Album: {album_name}\n")
                f.write(f"Artist: {album_artist}\n")
                f.write(f"Album ID: {album_id}\n")
                if publish_date_str:
                    f.write(f"Publish Date: {publish_date_str}\n")
                f.write(f"Song Count: {song_count}\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("Description:\n\n")
                f.write(album_description if album_description else "No description available")
            logger.info(f"Created album description file: {os.path.basename(description_file_path)}")
        except Exception as e:
            logger.error(f"Failed to create description file: {str(e)}")

        # Download cover image
        if album_cover_url and config.should_write_cover():
            cover_file_path = os.path.join(album_folder_path, 'cover.jpg')
            try:
                logger.info("Downloading album cover...")
                random_sleep()
                cover_response = requests.get(album_cover_url, timeout=10)
                cover_response.raise_for_status()

                with open(cover_file_path, 'wb') as f:
                    f.write(cover_response.content)
                logger.info(f"Album cover downloaded: {os.path.basename(cover_file_path)}")
            except Exception as e:
                logger.warning(f"Album cover download failed: {str(e)}")
        else:
            logger.warning("No album cover found or cover download disabled")

        logger.info(f"Album folder prepared successfully: {album_folder_path}")
        return album_folder_path

    except Exception as e:
        logger.error(f"Failed to prepare album folder: {str(e)}")
        return None


def download_album(album_id: str, index_ids: list, level: str = "lossless"):
    if level is None:
        level = config.get_default_quality()
    album_metadata = get_song_ids_by_album_id(album_id)

    # Create album folder, description file, and cover picture
    prepare_album_folder(album_metadata)

    index = 0
    for song_id in album_metadata['song_ids']:
        song_detail = album_metadata['song_details'][index]
        song_index = song_detail['index']
        logger.info(f"{index + 1}. {song_detail}")

        if len(index_ids) > 0:
            if song_index in index_ids:
                logger.info(f"{song_index} is in the {index_ids}, continue downloading...")
                metadata = get_song_metadata_by_song_id(song_id, level)
                download_song_and_resources(metadata, idx=song_index)
            else:
                logger.info(f"{song_index} is not in the {index_ids}, skipping downloading...")
        else:
            metadata = get_song_metadata_by_song_id(song_id, level)
            download_song_and_resources(metadata, idx=song_index)
        index += 1

    album_artist = album_metadata['album_artist']
    album_name = album_metadata['album_name']
    logger.info(f"Completed downloading album: {album_artist} - {album_name}")


def download_playlist(playlist_id: str, index_ids: list, level: str = "lossless"):
    if level is None:
        level = config.get_default_quality()
    playlist_metadata = get_song_ids_by_playlist_id(playlist_id)
    index = 0
    for song_id in playlist_metadata['song_ids']:
        song_detail = playlist_metadata['song_details'][index]
        song_index = song_detail['index']
        logger.info(f"{index + 1}. {song_detail}")

        if len(index_ids) > 0:
            if song_index in index_ids:
                logger.info(f"{song_index} is in the {index_ids}, continue downloading...")
                metadata = get_song_metadata_by_song_id(song_id, level)
                download_song_and_resources(metadata, idx=None)
            else:
                logger.info(f"{song_index} is not in the {index_ids}, skipping downloading...")
        else:
            metadata = get_song_metadata_by_song_id(song_id, level)
            download_song_and_resources(metadata, idx=None)
        index += 1

NEXT_MUSIC_TOKEN = "59e2b0fa43bb7733b4ae62487f108144"

if __name__ == "__main__":
    # Part-1 Download Song by Song ID
    # https://music.163.com/song?id=2052368104
    # download_song("2014307526")

    indexes = []
    # indexes = [4, 6, 15, 18, 19]
    # indexes = list(range(5, 9))

    # Part-2 Download Songs by Album ID
    download_album("3085025", indexes)

    # Part-3 Download Playlist
    # download_playlist("5453912201", indexes)

    pass