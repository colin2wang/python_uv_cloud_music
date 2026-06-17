"""
Metadata processing functions for music files
"""

from typing import List, Optional, Tuple, Any
from src.model.basic import MusicInfo, MusicURL
from src.model.extra import AlbumMetadata, PlaylistMetadata
from src.tool.tool_next_music_v2 import NextMusicToolV2
from src.util.util_commons import random_sleep, ensure_get_metadata_interval, finish_get_metadata
from src.util.util_config import config
from src.util.util_logging import setup_logger

logger = setup_logger(__name__)

# Constants
HTTP_OK = 200


def _extract_song_details(song_list: List[dict]) -> Tuple[List[str], List[dict]]:
    """Extract song IDs and details from song list"""
    song_ids = []
    song_details = []

    for i, song in enumerate(song_list, 1):
        song_id = song.get('id')
        if not song_id:
            logger.warning(f"{i:2d}. Invalid song data (no ID): {song}")
            continue
            
        song_name = song.get('name', 'Unknown Song')
        song_artists = song.get('artists', 'Unknown Artist')
        
        song_ids.append(str(song_id))
        song_details.append({
            "id": str(song_id),
            "name": song_name,
            "artists": song_artists,
            "index": i
        })
        logger.info(f"{i:2d}. [{song_id}] {song_name} - {song_artists}")

    return song_ids, song_details


def get_song_ids_by_playlist_id(playlist_id: str) -> Optional[PlaylistMetadata]:
    """Get song list by playlist ID"""
    from src.util.util_music_api import MusicToolAPI
    
    logger.info("=" * 60)
    logger.info("Extract Songs from Playlist ID")
    logger.info("=" * 60)
    logger.info(f"Playlist ID: {playlist_id}")
    logger.info("-" * 60)

    api = MusicToolAPI(config.get_api_base_url())

    playlist_result = api.parse_playlist(playlist_id)
    if not playlist_result:
        logger.error("\nPlaylist parsing failed: No result returned")
        return None

    # Check status code
    status = playlist_result.get('status')
    if status != HTTP_OK:
        error_msg = playlist_result.get('message', 'Unknown error')
        logger.error(f"\nPlaylist parsing failed (Status {status}): {error_msg}")
        return None

    data_section = playlist_result.get('data', {})
    playlist_info = data_section.get('playlist', {})

    if not playlist_info:
        logger.error("\nPlaylist info not found")
        return None

    playlist_name = playlist_info.get('name', 'Unknown Playlist')
    creator_raw = playlist_info.get('creator', 'Unknown Creator')
    if isinstance(creator_raw, dict):
        playlist_creator = creator_raw.get('nickname', 'Unknown Creator')
    else:
        playlist_creator = str(creator_raw) if creator_raw else 'Unknown Creator'
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
    """Get song list by album ID"""
    from src.util.util_music_api import MusicToolAPI
    
    logger.info("=" * 60)
    logger.info("Extract Songs from Album ID")
    logger.info("=" * 60)
    logger.info(f"Album ID: {album_id}")
    logger.info("-" * 60)

    api = MusicToolAPI(config.get_api_base_url())

    album_result = api.parse_album(album_id)
    if not album_result:
        logger.error("\nAlbum parsing failed: No result returned")
        return None

    status = album_result.get('status')
    if status != HTTP_OK:
        error_msg = album_result.get('message', 'Unknown error')
        logger.error(f"\nAlbum parsing failed (Status {status}): {error_msg}")
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
        import time
        try:
            publish_date = time.strftime('%Y-%m-%d', time.localtime(album_publish_time / 1000))
            logger.info(f"Publish Date: {publish_date}")
        except (ValueError, OSError) as e:
            logger.warning(f"Could not format publish time: {album_publish_time}, error: {e}")
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


def _fetch_metadata_from_next_music_tool(song_id: str, quality_level: str) -> Optional[dict]:
    """Get song metadata using NextMusicTool"""
    try:
        next_music_tool = NextMusicToolV2()
        song_info_model = next_music_tool.get_song_info(song_id)
        song_url_model = next_music_tool.get_song_url(song_id, quality_level)
        song_lyric_str = next_music_tool.get_song_lyric(song_id)

        # Validate returned model types
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
            'status': HTTP_OK
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


def _fetch_metadata_from_original_api(api: Any, song_id: str, quality_level: str) -> Optional[dict]:
    """Get song metadata using original API"""
    try:
        result_json = api.parse_song(song_id, quality_level)
        if not result_json:
            return None
            
        # Check if retry is needed (429 error)
        from src.util.util_music_api import _handle_429_error_json
        if _handle_429_error_json(result_json.get('data', {}).get('msg', '')):
            logger.info(f"Retrying after 429 error for song {song_id}...")
            result_json = api.parse_song(song_id, quality_level)
        
        return result_json
    except Exception as e:
        logger.error(f"Error fetching metadata from original API: {str(e)}")
        return None


def get_song_metadata_by_song_id(song_id: str, level: Optional[str] = None) -> dict:
    """Get metadata by song ID"""

    # Ensure minimum interval between get_metadata requests
    ensure_get_metadata_interval()
    
    # Get configuration
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

        # Choose metadata retrieval method based on configuration
        if config.should_use_next_music_tool():
            logger.info("Replacing song URL with NextMusicTool...")
            result_json = _fetch_metadata_from_next_music_tool(song_id, try_quality_level)
        else:
            from src.util.util_music_api import MusicToolAPI
            api = MusicToolAPI(config.get_api_base_url())
            logger.info(f"Fetching song metadata from Original API (quality: {try_quality_level})...")
            result_json = _fetch_metadata_from_original_api(api, song_id, try_quality_level)

        if not result_json:
            continue

        # Validate response
        status = result_json.get('status', -1)
        data = result_json.get('data', {})
        
        if status == HTTP_OK and data.get('url'):
            actual_level = data.get('level', '')
            
            # Check if quality matches
            if actual_level and actual_level != try_quality_level:
                if retry_count == max_retries:
                    logger.info(f"Last result: Quality mismatch: expected: [{try_quality_level}], actual: [{actual_level}]")
                    result = result_json
                    used_level = actual_level
                else:
                    logger.warning(
                        f"Quality mismatch: expected: [{try_quality_level}], actual: [{actual_level}]. Retrying...")
                continue

            result = result_json
            used_level = try_quality_level if not actual_level else actual_level
            logger.info(f"Found available quality: {used_level}")
            break
            
        error_msg = data.get('msg') or data.get('message', 'Unknown reason')
        logger.warning(f"Quality {try_quality_level} not available (attempt {retry_count + 1}/{max_retries}): {error_msg}")

    if not result:
        return {"success": False, "message": "No available quality", "tried_levels": [try_quality_level]}

    # Update last get_metadata timestamp
    finish_get_metadata()

    return _prepare_metadata_result(result, used_level)


def _prepare_metadata_result(result: dict, used_level: str) -> dict:
    """Prepare and log metadata result"""
    data = result.get('data', {})
    
    logger.info(f"\nExtraction successful!\n")
    logger.info(f"Song Name: {data.get('name')}")
    logger.info(f"Artist: {data.get('ar_name')}")
    logger.info(f"Album: {data.get('al_name')}")
    logger.info(f"Actual quality: {used_level or data.get('level')}")
    logger.info(f"File Size: {data.get('size', 'Unknown')}")
    logger.info(f"Download/Play URL: {'***' if data.get('url') else 'Not available'}")
    logger.info(f"Cover Image: {data.get('pic')}")

    result['used_quality'] = used_level or data.get('level')

    if data.get('lyric'):
        lyric_preview = data['lyric']
        if len(lyric_preview) > 500:
            logger.info(f"\nLyrics (first 500 chars):\n{lyric_preview[:500]}...")
        else:
            logger.info(f"\nLyrics:\n{lyric_preview}")

    return result