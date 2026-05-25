import json
import os
import re
import time
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, COMM, TYER, TRCK, TXXX
from mutagen.mp4 import MP4, MP4Cover
from tqdm import tqdm

from model.basic import MusicInfo, MusicURL
from model.extra import AlbumMetadata, PlaylistMetadata
from tool_next_music_v2 import NextMusicToolV2
from util_commons import (
    get_audio_extension, get_image_mime_type,
    get_mp4_image_format, clean_filename, random_sleep, ensure_download_interval, update_last_download_timestamp
)
from util_config import config
from util_logging import setup_logger

logger = setup_logger(__name__)


class MusicToolAPI:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or config.get_api_base_url()).rstrip('/')
        self.session = requests.Session()
        self._setup_request_headers()

    def _setup_request_headers(self) -> None:
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': self.base_url,
            'priority': 'u=1, i',
            'referer': self.base_url,
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        })

    def _extract_id(self, text: str, pattern_type: str = 'song') -> str:
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

    def search(self, keyword: str, limit: int = 10) -> str:
        random_sleep(5.0, reason="Before search API request")
        response = self.session.post(
            f"{self.base_url}/Search",
            data={'keyword': keyword, 'limit': limit}
        )
        return response.text

    def parse_song(self, song_id_or_url: str, level: str = "lossless") -> str:
        song_id = self._extract_id(song_id_or_url, 'song')
        random_sleep(3.0, reason="Before song parsing API request")
        response = self.session.post(
            f"{self.base_url}/Song_V1",
            data={'url': song_id, 'level': level, 'type': 'json'}
        )
        return response.text

    def parse_playlist(self, playlist_id_or_url: str) -> str:
        playlist_id = self._extract_id(playlist_id_or_url, 'playlist')
        random_sleep(3.0, reason="Before playlist parsing API request")
        response = self.session.get(
            f"{self.base_url}/Playlist",
            params={'id': playlist_id}
        )
        logger.info("-" * 60)
        return response.text

    def parse_album(self, album_id_or_url: str) -> str:
        album_id = self._extract_id(album_id_or_url, 'album')
        random_sleep(3.0, reason="Before album parsing API request")
        response = self.session.get(
            f"{self.base_url}/Album",
            params={'id': album_id}
        )
        return response.text


def _parse_json_response(response_str: str, operation: str) -> Optional[dict]:
    try:
        return json.loads(response_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed during {operation}: {str(e)}")
        logger.error(f"Raw response: {response_str}")
        return None


def _extract_song_details(song_list: List[dict]) -> Tuple[List[str], List[dict]]:
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

    return song_ids, song_details


def get_song_ids_by_playlist_id(playlist_id: str) -> Optional[PlaylistMetadata]:
    api = MusicToolAPI(config.get_api_base_url())

    logger.info("=" * 60)
    logger.info("Extract Songs from Playlist ID")
    logger.info("=" * 60)
    logger.info(f"Playlist ID: {playlist_id}")
    logger.info("-" * 60)

    playlist_result_str = api.parse_playlist(playlist_id)
    playlist_result = _parse_json_response(playlist_result_str, "playlist parsing")

    if not playlist_result or playlist_result.get('status') != 200:
        error_msg = playlist_result.get('message', 'Unknown error') if playlist_result else 'Invalid response'
        logger.error(f"\nPlaylist parsing failed: {error_msg}")
        return None

    data_section = playlist_result.get('data', {})
    playlist_info = data_section.get('playlist', {})

    if not playlist_info:
        logger.error("\nPlaylist info not found")
        return None

    playlist_name = playlist_info.get('name', 'Unknown Playlist')
    playlist_creator = playlist_info.get('creator', 'Unknown Creator')
    song_list = playlist_info.get('tracks', [])

    logger.info(f"\nPlaylist parsed successfully!")
    logger.info(f"Playlist Name: {playlist_name}")
    logger.info(f"Creator: {playlist_creator}")
    logger.info(f"Track Count: {len(song_list)}")
    logger.info("-" * 60)

    song_ids, song_details = _extract_song_details(song_list)

    logger.info(f"\nSuccessfully extracted {len(song_ids)} song IDs")
    return PlaylistMetadata(
        playlist_id=playlist_id,
        playlist_name=playlist_name,
        playlist_creator=playlist_creator,
        song_count=len(song_ids),
        song_ids=song_ids,
        song_details=song_details
    )


def get_song_ids_by_album_id(album_id: str) -> Optional[AlbumMetadata]:
    api = MusicToolAPI(config.get_api_base_url())

    logger.info("=" * 60)
    logger.info("Extract Songs from Album ID")
    logger.info("=" * 60)
    logger.info(f"Album ID: {album_id}")
    logger.info("-" * 60)

    album_result_str = api.parse_album(album_id)
    album_result = _parse_json_response(album_result_str, "album parsing")

    if not album_result or album_result.get('status') != 200:
        error_msg = album_result.get('message', 'Unknown error') if album_result else 'Invalid response'
        logger.error(f"\nAlbum parsing failed: {error_msg}")
        return None

    album_data = album_result.get('data', {}).get('album', {})

    if not album_data:
        logger.error("\nAlbum data not found")
        return None

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

    song_ids, song_details = _extract_song_details(song_list)

    logger.info(f"\nSuccessfully extracted {len(song_ids)} song IDs")
    return AlbumMetadata(
        album_id=album_id,
        album_name=album_name,
        album_artist=album_artist,
        album_publish_time=album_publish_time,
        song_count=len(song_ids),
        song_details=song_details,
        raw_data=album_result
    )


def _handle_429_error(response_str: str) -> bool:
    if '429 Too Many Requests' in response_str:
        random_sleep(min_delay=10.0, max_delay=15.0, reason="429 Too Many Requests - API rate limit")
        return True
    return False


def _fetch_metadata_from_next_music_tool(song_id: str, quality_level: str) -> Optional[dict]:
    try:
        next_music_tool = NextMusicToolV2()
        song_info_model = next_music_tool.get_song_info(song_id)
        song_url_model = next_music_tool.get_song_url(song_id, quality_level)
        song_lyric_str = next_music_tool.get_song_lyric(song_id)

        if not isinstance(song_url_model, MusicURL) or not isinstance(song_info_model, MusicInfo):
            logger.error("NextMusicTool returned invalid models")
            return None

        result_json = {
            'data': {
                'url': song_url_model.url,
                'level': song_url_model.quality,
                'size': None,
                'name': song_info_model.title,
                'ar_name': song_info_model.artist.replace('/', ', ') if song_info_model.artist else '',
                'al_name': song_info_model.album,
                'pic': song_info_model.cover_url,
                'id': str(song_info_model.music_id),
                'duration': song_info_model.duration
            },
            'status': 200
        }

        if song_lyric_str:
            result_json['data']['lyric'] = song_lyric_str
            logger.info(f"Lyrics retrieved successfully for song {song_id}")
        else:
            logger.warning(f"No lyrics found for song {song_id}")

        return result_json

    except Exception as e:
        logger.error(f"Error fetching metadata from NextMusicTool: {str(e)}")
        return None


def _fetch_metadata_from_original_api(api: MusicToolAPI, song_id: str, quality_level: str) -> Optional[dict]:
    try:
        result_str = api.parse_song(song_id, quality_level)
        if _handle_429_error(result_str):
            result_str = api.parse_song(song_id, quality_level)
        return json.loads(result_str)
    except json.JSONDecodeError as e:
        logger.error(f"Quality {quality_level} parsing failed: {str(e)}")
        logger.error(f"Raw response: {result_str}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network request failed (Quality {quality_level}): {str(e)}")
        return None


def get_song_metadata_by_song_id(song_id: str, level: str = "lossless") -> dict:
    ensure_download_interval()

    try:
        api = MusicToolAPI(config.get_api_base_url())
        try_quality_level = level if level is not None else config.get_default_quality()
        max_retries = config.get_max_retries()

        logger.info("=" * 60)
        logger.info("Extract Song Metadata by Song ID")
        logger.info("=" * 60)
        logger.info(f"Song ID: {song_id}")
        logger.info(f"Quality Level: {try_quality_level}")
        logger.info(f"Max Retries: {max_retries}")
        logger.info("-" * 60)

        result, used_level = None, None

        for retry_count in range(max_retries + 1):
            if retry_count > 0:
                logger.info(f"Retry {retry_count}/{max_retries} for quality {try_quality_level}...")
                random_sleep(reason="Between retry attempts for song metadata")

            if config.should_use_next_music_tool():
                logger.info("Replacing song URL with NextMusicTool...")
                result_json = _fetch_metadata_from_next_music_tool(song_id, try_quality_level)
            else:
                logger.info(f"Fetching song metadata from Original API (quality: {try_quality_level})...")
                result_json = _fetch_metadata_from_original_api(api, song_id, try_quality_level)

            if not result_json:
                continue

            if result_json.get('status') == 200 and result_json.get('data', {}).get('url'):
                actual_level = result_json.get('data', {}).get('level', '')
                if actual_level and actual_level != try_quality_level:
                    logger.warning(
                        f"Quality mismatch: expected: [{try_quality_level}], actual: [{actual_level}]. Retrying...")
                    continue

                result = result_json
                used_level = try_quality_level
                logger.info(f"Found available quality: {try_quality_level}")
                break
            else:
                error_msg = result_json.get('data', {}).get('msg') or result_json.get('message', 'Unknown reason')
                logger.warning(f"Quality {try_quality_level} not available (attempt {retry_count + 1}/{max_retries}): {error_msg}")

        if not result:
            return {"success": False, "message": "No available quality", "tried_levels": [level]}

        return _prepare_metadata_result(result, used_level)

    except Exception as e:
        logger.error(f"Critical error occurred while getting song metadata: {str(e)}")
        return {"success": False, "message": f"Failed to get metadata: {str(e)}", "song_id": song_id}


def _prepare_metadata_result(result: dict, used_level: str) -> dict:
    data = result['data']
    logger.info(f"\nExtraction successful!\n")
    logger.info(f"Song Name: {data['name']}")
    logger.info(f"Artist: {data['ar_name']}")
    logger.info(f"Album: {data['al_name']}")
    logger.info(f"Actual quality: {used_level or data['level']}")
    logger.info(f"File Size: {data['size']}")
    logger.info(f"Download/Play URL: {data['url']}")
    logger.info(f"Cover Image: {data['pic']}")

    result['used_quality'] = used_level or data['level']

    if data.get('lyric'):
        logger.info(f"\nLyrics:")
        logger.info(data['lyric'][:500] + "..." if len(data['lyric']) > 500 else data['lyric'])

    return result


def _write_audio_metadata(audio_file: Any, metadata: dict, format_type: str) -> None:
    song_name = metadata.get('name', '')
    artist = metadata.get('ar_name', '').split(',')
    album = metadata.get('al_name', '')
    lyric = metadata.get('lyric', '')
    cover_path = metadata.get('cover_path', '')
    track_number = metadata.get('track_number', '')
    song_id = metadata.get('id', '')

    if format_type == 'mp3':
        _write_mp3_metadata(audio_file, song_name, artist, album, lyric, cover_path, track_number, song_id)
    elif format_type == 'flac':
        _write_flac_metadata(audio_file, song_name, artist, album, lyric, cover_path, track_number, song_id)
    elif format_type == 'mp4':
        _write_mp4_metadata(audio_file, song_name, artist, album, lyric, cover_path, track_number, song_id)


def _write_mp3_metadata(audio_file: ID3, song_name: str, artist: list, album: str, lyric: str,
                        cover_path: str, track_number: str, song_id: str) -> None:
    if song_name:
        audio_file.add(TIT2(encoding=3, text=song_name))
    if artist:
        audio_file.add(TPE1(encoding=3, text=artist))
    if album:
        audio_file.add(TALB(encoding=3, text=album))
    audio_file.add(TYER(encoding=3, text=str(time.localtime().tm_year)))
    if track_number:
        audio_file.add(TRCK(encoding=3, text=track_number))
    if song_id:
        audio_file.add(TXXX(encoding=3, desc='CMUSIC_ID', text=str(song_id)))
    if lyric:
        audio_file.add(COMM(encoding=1, lang='eng', desc='', text=lyric))
    if cover_path and os.path.exists(cover_path):
        _embed_cover_to_mp3(audio_file, cover_path)


def _write_flac_metadata(audio_file: FLAC, song_name: str, artist: list, album: str, lyric: str,
                         cover_path: str, track_number: str, song_id: str) -> None:
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
        audio_file['CMUSIC_ID'] = str(song_id)
    if cover_path and os.path.exists(cover_path):
        _embed_cover_to_flac(audio_file, cover_path)


def _write_mp4_metadata(audio_file: MP4, song_name: str, artist: list, album: str, lyric: str,
                        cover_path: str, track_number: str, song_id: str) -> None:
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
        mp4_tags['----:CMUSIC_ID'] = str(song_id).encode('utf-8')
    if cover_path and os.path.exists(cover_path):
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            mp4_tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path))]

    if audio_file.tags is None:
        audio_file.add_tags()
    audio_file.tags.update(mp4_tags)


def _embed_cover_to_mp3(audio_file: ID3, cover_path: str) -> None:
    try:
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            audio_file.add(APIC(
                encoding=3,
                mime=get_image_mime_type(cover_path),
                type=3,
                desc='Cover',
                data=img_data
            ))
    except Exception as e:
        logger.warning(f"Cover image writing failed: {e}")


def _embed_cover_to_flac(audio_file: FLAC, cover_path: str) -> None:
    try:
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            picture = Picture()
            picture.type = 3
            picture.mime = get_image_mime_type(cover_path)
            picture.data = img_data
            audio_file.add_picture(picture)
    except Exception as e:
        logger.warning(f"Cover image writing failed: {e}")


def write_metadata_to_file(file_path: Union[str, Path], metadata: dict) -> bool:
    file_path = Path(file_path)
    ext = get_audio_extension(file_path)

    logger.info(f"Writing metadata to {file_path.name}...")

    try:
        if ext in ('.mp3', '.mp2', '.mp1'):
            audio_file = ID3(file_path)
            _write_audio_metadata(audio_file, metadata, 'mp3')
            audio_file.save()
        elif ext == '.flac':
            audio_file = FLAC(file_path)
            _write_audio_metadata(audio_file, metadata, 'flac')
            audio_file.save()
        elif ext in ('.m4a', '.mp4', '.aac'):
            audio_file = MP4(file_path)
            _write_audio_metadata(audio_file, metadata, 'mp4')
            audio_file.save()
        else:
            logger.warning(f"Unsupported file format: {ext}")
            return False

        logger.info("Metadata written successfully!")
        return True

    except Exception as e:
        logger.error(f"Metadata writing failed: {e}")
        return False


def _embed_cover_to_file(audio_file: Any, cover_path: Union[str, Path], ext: str) -> None:
    cover_path = str(cover_path)
    if ext in ('.mp3', '.mp2', '.mp1'):
        _embed_cover_to_mp3(audio_file, cover_path)
    elif ext == '.flac':
        _embed_cover_to_flac(audio_file, cover_path)
    elif ext in ('.m4a', '.mp4', '.aac'):
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            if audio_file.tags is None:
                audio_file.add_tags()
            audio_file.tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path))]


def write_picture_to_file(file_path: Union[str, Path]) -> bool:
    file_path = Path(file_path)
    file_dir = file_path.parent
    file_base_name = file_path.stem

    cover_path = next((file_dir / f"{file_base_name}{ext}" for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
                       if (file_dir / f"{file_base_name}{ext}").exists()), None)

    if not cover_path:
        logger.warning("No image file found with the same name")
        return False

    ext = get_audio_extension(file_path)
    logger.info(f"Writing image to {file_path.name}...")

    try:
        if ext in ('.mp3', '.mp2', '.mp1'):
            audio_file = ID3(file_path)
            _embed_cover_to_file(audio_file, cover_path, ext)
            audio_file.save()
            logger.info("MP3 cover image written successfully!")
        elif ext == '.flac':
            audio_file = FLAC(file_path)
            _embed_cover_to_file(audio_file, cover_path, ext)
            audio_file.save()
            logger.info("FLAC cover image written successfully!")
        elif ext in ('.m4a', '.mp4', '.aac'):
            audio_file = MP4(file_path)
            _embed_cover_to_file(audio_file, cover_path, ext)
            audio_file.save()
            logger.info("MP4/AAC cover image written successfully!")
        else:
            logger.warning(f"Unsupported file format: {ext}")
            return False
        return True

    except Exception as e:
        logger.error(f"Cover image writing failed: {e}")
        return False


def _extract_file_extension(download_url: str) -> str:
    parsed_url = urllib.parse.urlparse(download_url)
    path_parts = parsed_url.path.split('/')

    if path_parts:
        last_part = path_parts[-1]
        if '.' in last_part:
            return Path(last_part).suffix.lower()

    query_params = urllib.parse.parse_qs(parsed_url.query)
    v_param = query_params.get('v', [''])[0]
    if v_param and '.' in v_param:
        ext_from_v = Path(v_param).suffix.lower()
        if ext_from_v in {'.flac', '.wav', '.aac', '.m4a'}:
            return ext_from_v

    return ".mp3"


def _build_filename(song_name: str, artist: str, idx: Optional[int] = None) -> str:
    safe_song_name = clean_filename(song_name)
    safe_artist = clean_filename(artist)
    add_index = config.should_add_index()
    index_format = config.get_index_format()

    if idx is not None and add_index:
        formatted_index = f"{idx:{index_format}}"
        filename = f"{formatted_index} - {safe_artist} - {safe_song_name}"
    else:
        filename = f"{safe_artist} - {safe_song_name}"

    max_filename_length = 200
    if len(filename) > max_filename_length:
        logger.warning(f"Filename too long ({len(filename)} chars), truncating")
        if idx is not None and add_index:
            formatted_index = f"{idx:{index_format}}"
            available_length = max_filename_length - len(formatted_index) - 4
            total_original = len(safe_artist) + len(safe_song_name)
            if total_original > 0:
                max_artist_len = int(available_length * len(safe_artist) / total_original * 0.5)
                max_song_len = available_length - max_artist_len - 3
                safe_artist = safe_artist[:max_artist_len]
                safe_song_name = safe_song_name[:max_song_len]
            filename = f"{formatted_index} - {safe_artist} - {safe_song_name}"
        else:
            filename = filename[:max_filename_length]

    return filename


def _download_with_retry(url: str, timeout: int, reason: str) -> Optional[requests.Response]:
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 429:
            logger.warning(f"Received 429 Too Many Requests while downloading {reason}.")
            random_sleep(min_delay=10.0, max_delay=15.0, reason=f"429 Too Many Requests - {reason} rate limit")
            response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Download failed ({reason}): {e}")
        return None


def download_song_and_resources(
    song_metadata: dict,
    download_dir: Optional[str] = None,
    idx: Optional[int] = None,
    current_index: Optional[int] = None,
    total_count: Optional[int] = None
) -> bool:
    if not song_metadata or not song_metadata.get('success', True):
        logger.error("Invalid song metadata")
        return False

    data = song_metadata['data']
    download_url = data['url']

    if not download_url:
        logger.error("No download URL in metadata")
        return False

    download_dir = download_dir or config.get_download_dir()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    filename = _build_filename(data['name'], data['ar_name'], idx)
    file_extension = _extract_file_extension(download_url)

    music_file_path = Path(download_dir) / f"{filename}{file_extension}"
    lyric_file_path = Path(download_dir) / f"{filename}.lrc"
    cover_file_path = Path(download_dir) / f"{filename}.jpg"

    if music_file_path.exists():
        logger.info(f"File already exists, skipping: {music_file_path.name}")
        return True

    progress_info = f"[{current_index} / {total_count}] " if current_index is not None and total_count is not None else ""

    logger.info(f"{progress_info}Starting download: {filename}")
    logger.info(f"File size: {data.get('size', 'Unknown')}")
    logger.info(f"Quality: {song_metadata.get('used_quality', data.get('level', 'unknown'))}")
    logger.info("-" * 60)

    random_sleep(reason="Before downloading music file")
    response = _download_with_retry(download_url, config.get_timeout(), "music")
    if not response:
        return False

    total_size = int(response.headers.get('content-length', 0))

    try:
        with open(music_file_path, 'wb') as f:
            if total_size > 0:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"{progress_info}{filename}",
                    ncols=100
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        logger.info(f"Music file downloaded: {music_file_path.name}")
    except Exception as e:
        logger.error(f"Failed to write music file: {e}")
        return False

    metadata_for_tagging = data.copy()
    metadata_for_tagging['cover_path'] = str(cover_file_path) if cover_file_path.exists() else ''
    if idx is not None:
        metadata_for_tagging['track_number'] = str(idx)

    if config.should_write_metadata():
        logger.info("\nWriting metadata...")
        if not write_metadata_to_file(music_file_path, metadata_for_tagging):
            logger.warning("Metadata writing failed, retrying...")
            for retry_count in range(config.get_max_retries()):
                logger.info(f"Retry {retry_count + 1}/{config.get_max_retries()}...")
                if write_metadata_to_file(music_file_path, metadata_for_tagging):
                    break

    lyric = data.get('lyric', '')
    if lyric and config.should_write_lyrics():
        logger.info("Saving lyrics...")
        try:
            with open(lyric_file_path, 'w', encoding='utf-8') as f:
                f.write(lyric)
            logger.info(f"Lyrics saved: {lyric_file_path.name}")
        except IOError as e:
            logger.warning(f"Lyrics saving failed: {e}")

    cover_url = data.get('pic', '')
    if cover_url and config.should_write_cover():
        logger.info("Downloading cover...")
        random_sleep(reason="Before downloading cover image")
        cover_response = _download_with_retry(f"{cover_url}?param=320x320", 10, "cover")
        if cover_response:
            try:
                with open(cover_file_path, 'wb') as f:
                    f.write(cover_response.content)
                logger.info(f"Cover downloaded: {cover_file_path.name}")
            except IOError as e:
                logger.warning(f"Cover saving failed: {e}")

    if config.should_write_cover():
        logger.info("Adding cover to song file...")
        write_picture_to_file(music_file_path)

    logger.info(f"Download completed! Files saved in: {download_dir}")
    update_last_download_timestamp()

    return True


def download_song(song_id: str, level: Optional[str] = None) -> None:
    level = level if level is not None else config.get_default_quality()
    metadata = get_song_metadata_by_song_id(song_id, level)
    download_song_and_resources(metadata, idx=None)


def prepare_album_folder(album_metadata: dict, download_dir: Optional[str] = None) -> Optional[str]:
    try:
        download_dir = download_dir or config.get_download_dir()

        album_name = album_metadata.get('album_name', 'Unknown Album')
        album_artist = album_metadata.get('album_artist', 'Unknown Artist')
        album_id = album_metadata.get('album_id', '')
        album_publish_time = album_metadata.get('album_publish_time')
        song_count = album_metadata.get('song_count', 0)
        raw_data = album_metadata.get('raw_data', {})

        publish_date_str = ''
        if album_publish_time:
            try:
                publish_date_str = time.strftime('%Y-%m-%d', time.localtime(album_publish_time / 1000))
            except (ValueError, OSError):
                logger.warning(f"Could not convert publish time: {album_publish_time}")

        album_description = raw_data.get('data', {}).get('album', {}).get('description', '')
        album_cover_url = raw_data.get('data', {}).get('album', {}).get('coverImgUrl', '').split('?')[0]
        logger.info(f"Album cover URL: {album_cover_url}")

        safe_album_name = clean_filename(album_name)
        safe_artist = clean_filename(album_artist)

        if publish_date_str:
            album_folder_name = f"{safe_artist} - {safe_album_name} ({publish_date_str})"
        else:
            album_folder_name = f"{safe_artist} - {safe_album_name}"
        album_folder_path = os.path.join(download_dir, album_folder_name)

        os.makedirs(album_folder_path, exist_ok=True)
        logger.info(f"Created album folder: {album_folder_path}")

        _create_album_description_file(album_folder_path, album_name, album_artist, album_id,
                                       publish_date_str, song_count, album_description)

        if album_id:
            _create_album_id_file(album_folder_path, album_id, album_name, album_artist,
                                  album_metadata.get('song_details', []))

        if album_cover_url and config.should_write_cover():
            _download_album_cover(album_folder_path, album_cover_url)

        logger.info(f"Album folder prepared successfully: {album_folder_path}")
        return album_folder_path

    except Exception as e:
        logger.error(f"Failed to prepare album folder: {str(e)}")
        return None


def _create_album_description_file(folder_path: str, album_name: str, album_artist: str, album_id: str,
                                   publish_date_str: str, song_count: int, description: str) -> None:
    description_file_path = os.path.join(folder_path, 'album_info.txt')
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
            f.write(description if description else "No description available")
        logger.info(f"Created album description file: {os.path.basename(description_file_path)}")
    except Exception as e:
        logger.error(f"Failed to create description file: {str(e)}")


def _create_album_id_file(folder_path: str, album_id: str, album_name: str, album_artist: str,
                          song_details: List[dict]) -> None:
    album_id_file_path = os.path.join(folder_path, f"{album_id}.txt")
    try:
        with open(album_id_file_path, 'w', encoding='utf-8') as f:
            f.write(f"Album ID: {album_id}\n")
            f.write(f"Album: {album_name}\n")
            f.write(f"Artist: {album_artist}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("Songs:\n\n")

            if song_details:
                for song_detail in song_details:
                    idx = song_detail.get('index', 0)
                    song_name = song_detail.get('name', 'Unknown')
                    song_id = song_detail.get('id', '')
                    song_artists = song_detail.get('artists', 'Unknown Artist')
                    f.write(f"{idx}. {song_name} - {song_artists} (ID: {song_id})\n")
            else:
                f.write("No song information available\n")

        logger.info(f"Created album ID file: {os.path.basename(album_id_file_path)}")
    except Exception as e:
        logger.error(f"Failed to create album ID file: {str(e)}")


def _download_album_cover(folder_path: str, cover_url: str) -> None:
    cover_file_path = os.path.join(folder_path, 'cover.jpg')
    try:
        logger.info("Downloading album cover...")
        random_sleep(reason="Before downloading album cover")
        cover_response = requests.get(cover_url, timeout=10)

        if cover_response.status_code == 429:
            logger.warning("Received 429 Too Many Requests while downloading album cover.")
            random_sleep(min_delay=10.0, max_delay=15.0, reason="429 Too Many Requests - album cover download rate limit")
            cover_response = requests.get(cover_url, timeout=10)

        cover_response.raise_for_status()

        with open(cover_file_path, 'wb') as f:
            f.write(cover_response.content)
        logger.info(f"Album cover downloaded: {os.path.basename(cover_file_path)}")
    except Exception as e:
        logger.warning(f"Album cover download failed: {str(e)}")


def _count_downloaded_songs(download_dir: str) -> Dict[str, int]:
    download_path = Path(download_dir)
    if not download_path.exists():
        return {}

    audio_extensions = {'.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.wma', '.mp2', '.mp1'}
    ext_counter = Counter()

    for file_path in download_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            ext_counter[file_path.suffix.lower()] += 1

    return dict(ext_counter)


def _download_songs_from_metadata(metadata: Union[AlbumMetadata, PlaylistMetadata],
                                  index_ids: List[int], level: str, is_album: bool = True) -> None:
    failed_indexes = []

    for index, song_detail in enumerate(metadata.song_details):
        song_id = song_detail['id']
        song_index = song_detail['index']
        logger.info(f"{index + 1}. {song_detail}")

        if index_ids and song_index not in index_ids:
            logger.info(f"{song_index} is not in the {index_ids}, skipping downloading...")
            continue

        logger.info(f"{song_index} is in the {index_ids}, continue downloading..." if index_ids else "Downloading...")
        song_metadata = get_song_metadata_by_song_id(song_id, level)
        success = download_song_and_resources(
            song_metadata,
            idx=song_index if is_album else None,
            current_index=index + 1,
            total_count=len(metadata.song_details)
        )
        if not success:
            failed_indexes.append(song_index)

    if is_album:
        name_info = f"{metadata.album_artist} - {metadata.album_name}"
    else:
        name_info = f"playlist {metadata.playlist_id}"

    logger.info(f"Completed downloading {name_info}")
    logger.info(f"Total downloaded: {len(metadata.song_details)}")

    if failed_indexes:
        logger.info("=" * 60)
        logger.warning(f"Failed to download {len(failed_indexes)} song(s):")
        logger.warning(f"Failed indexes: {failed_indexes}")
        logger.info("=" * 60)

    stats = _count_downloaded_songs(config.get_download_dir())
    if stats:
        logger.info("=" * 60)
        logger.info("Download Statistics by File Extension:")
        total_count = sum(stats.values())
        for ext, count in sorted(stats.items()):
            logger.info(f"  {ext.upper()}: {count} files")
        logger.info(f"  Total: {total_count} files")
        logger.info("=" * 60)


def download_album(album_id: str, index_ids: List[int], level: Optional[str] = None) -> None:
    level = level if level is not None else config.get_default_quality()
    album_metadata = get_song_ids_by_album_id(album_id)

    if album_metadata is None:
        logger.error("Failed to get album metadata")
        return

    prepare_album_folder(album_metadata.to_dict())
    _download_songs_from_metadata(album_metadata, index_ids, level, is_album=True)


def download_playlist(playlist_id: str, index_ids: List[int], level: Optional[str] = None) -> None:
    level = level if level is not None else config.get_default_quality()
    playlist_metadata = get_song_ids_by_playlist_id(playlist_id)

    if playlist_metadata is None:
        logger.error("Failed to get playlist metadata")
        return

    _download_songs_from_metadata(playlist_metadata, index_ids, level, is_album=False)


if __name__ == "__main__":
    download_song("2618710190")

    indexes = []
    # indexes = [4, 6, 15, 18, 19]
    # indexes = list(range(11, 13))

    # download_album("1505850", indexes)
    # download_playlist("5453912201", indexes)