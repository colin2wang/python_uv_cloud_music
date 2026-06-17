"""
Download management functions for music files
"""

import os
import time
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, COMM, TYER, TRCK, TXXX
from mutagen.mp4 import MP4, MP4Cover
from tqdm import tqdm

from src.util.util_commons import get_audio_extension, get_image_mime_type, get_mp4_image_format, clean_filename, random_sleep, \
    HTTP_OK, HTTP_TOO_MANY_REQUESTS, IMAGE_EXTENSIONS, AUDIO_EXTENSIONS
from src.util.util_config import config
from src.util.util_logging import setup_logger

logger = setup_logger(__name__)


def _write_audio_metadata(audio_file: Any, metadata: dict, format_type: str) -> None:
    """Write audio metadata based on format"""
    song_name = metadata.get('name', '')
    artist_str = metadata.get('ar_name', '') or ''
    artist = [a.strip() for a in artist_str.split(',') if a.strip()]
    album = metadata.get('al_name', '') or ''
    lyric = metadata.get('lyric', '') or ''
    cover_path = metadata.get('cover_path', '') or ''
    track_number = metadata.get('track_number', '') or ''
    song_id = metadata.get('id', '') or ''

    format_handlers = {
        'mp3': _write_mp3_metadata,
        'flac': _write_flac_metadata,
        'mp4': _write_mp4_metadata
    }
    
    handler = format_handlers.get(format_type)
    if handler:
        handler(audio_file, song_name, artist, album, lyric, cover_path, track_number, song_id)


def _write_mp3_metadata(audio_file: ID3, song_name: str, artist: list, album: str, lyric: str,
                        cover_path: str, track_number: str, song_id: str) -> None:
    """Write MP3 metadata"""
    if not song_name and not artist and not album:
        logger.warning("No metadata to write for MP3 file")
        return
        
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
    """Write FLAC metadata"""
    if not song_name and not artist and not album:
        logger.warning("No metadata to write for FLAC file")
        return
        
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
    """Write MP4/M4A metadata"""
    if not song_name and not artist and not album:
        logger.warning("No metadata to write for MP4 file")
        return
        
    mp4_tags = {}
    if song_name:
        mp4_tags['\xa9nam'] = song_name
    if artist:
        mp4_tags['\xa9ART'] = artist
    if album:
        mp4_tags['\xa9alb'] = album
    if lyric:
        max_lyric_len = config.get_max_lyric_length()
        mp4_tags['\xa9lyr'] = lyric[:max_lyric_len]
    if track_number and track_number.isdigit():
        try:
            track_num = int(track_number)
            mp4_tags['trkn'] = [(track_num, 0)]
        except ValueError:
            logger.warning(f"Invalid track number: {track_number}")
    
    if song_id:
        mp4_tags['----:CMUSIC_ID'] = str(song_id).encode('utf-8')
        
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, 'rb') as img_file:
                img_data = img_file.read()
                mp4_tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path))]
        except (IOError, OSError) as e:
            logger.warning(f"Failed to read cover image: {e}")

    if audio_file.tags is None:
        audio_file.add_tags()
    audio_file.tags.update(mp4_tags)


def _embed_cover_to_mp3(audio_file: ID3, cover_path: str) -> None:
    """Embed cover image into MP3 file"""
    try:
        if not os.path.exists(cover_path):
            logger.warning(f"Cover file not found: {cover_path}")
            return
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            audio_file.add(APIC(
                encoding=3,
                mime=get_image_mime_type(cover_path),
                type=3,
                desc='Cover',
                data=img_data
            ))
    except (IOError, OSError) as e:
        logger.warning(f"Failed to embed cover image: {e}")


def _embed_cover_to_flac(audio_file: FLAC, cover_path: str) -> None:
    """Embed cover image into FLAC file"""
    try:
        if not os.path.exists(cover_path):
            logger.warning(f"Cover file not found: {cover_path}")
            return
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            picture = Picture()
            picture.type = 3
            picture.mime = get_image_mime_type(cover_path)
            picture.data = img_data
            audio_file.add_picture(picture)
    except (IOError, OSError) as e:
        logger.warning(f"Failed to embed cover image: {e}")


def write_metadata_to_file(file_path: Union[str, Path], metadata: dict) -> bool:
    """Write metadata to audio file"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    ext = get_audio_extension(file_path)
    logger.info(f"Writing metadata to {file_path.name}...")

    try:
        format_map = {
            '.mp3': (ID3, 'mp3'),
            '.mp2': (ID3, 'mp3'),
            '.mp1': (ID3, 'mp3'),
            '.flac': (FLAC, 'flac'),
            '.m4a': (MP4, 'mp4'),
            '.mp4': (MP4, 'mp4'),
            '.aac': (MP4, 'mp4')
        }
        
        handler_info = format_map.get(ext)
        if not handler_info:
            logger.warning(f"Unsupported file format: {ext}")
            return False
            
        AudioClass, format_type = handler_info
        audio_file = AudioClass(file_path)
        _write_audio_metadata(audio_file, metadata, format_type)
        audio_file.save()
        
        logger.info("Metadata written successfully!")
        return True

    except Exception as e:
        logger.error(f"Metadata writing failed: {e}")
        return False


def _embed_cover_to_file(audio_file: Any, cover_path: Union[str, Path], ext: str) -> None:
    """Embed cover image into audio file"""
    cover_path_str = str(cover_path)
    if not os.path.exists(cover_path_str):
        logger.warning(f"Cover file not found: {cover_path}")
        return
        
    if ext in ('.mp3', '.mp2', '.mp1'):
        _embed_cover_to_mp3(audio_file, cover_path_str)
    elif ext == '.flac':
        _embed_cover_to_flac(audio_file, cover_path_str)
    elif ext in ('.m4a', '.mp4', '.aac'):
        try:
            with open(cover_path_str, 'rb') as img_file:
                img_data = img_file.read()
                if audio_file.tags is None:
                    audio_file.add_tags()
                audio_file.tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(cover_path_str))]
        except (IOError, OSError) as e:
            logger.warning(f"Failed to embed cover: {e}")


def write_picture_to_file(file_path: Union[str, Path]) -> bool:
    """Embed image file with same name into audio file"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    file_dir = file_path.parent
    file_base_name = file_path.stem

    # Find image file with same name
    cover_path = next(
        (file_dir / f"{file_base_name}{ext}" for ext in IMAGE_EXTENSIONS 
         if (file_dir / f"{file_base_name}{ext}").exists()),
        None
    )

    if not cover_path or not cover_path.exists():
        logger.warning("No image file found with the same name")
        return False

    ext = get_audio_extension(file_path)
    logger.info(f"Writing image to {file_path.name}...")

    try:
        format_map = {
            '.mp3': (ID3, 'mp3'),
            '.mp2': (ID3, 'mp3'),
            '.mp1': (ID3, 'mp3'),
            '.flac': (FLAC, 'flac'),
            '.m4a': (MP4, 'mp4'),
            '.mp4': (MP4, 'mp4'),
            '.aac': (MP4, 'mp4')
        }
        
        handler_info = format_map.get(ext)
        if not handler_info:
            logger.warning(f"Unsupported file format: {ext}")
            return False
            
        AudioClass, _ = handler_info
        audio_file = AudioClass(file_path)
        _embed_cover_to_file(audio_file, cover_path, ext)
        audio_file.save()
        
        logger.info(f"{ext.upper()} cover image written successfully!")
        return True

    except Exception as e:
        logger.error(f"Cover image writing failed: {e}")
        return False


def _extract_file_extension(download_url: str) -> str:
    """Extract file extension from download URL"""
    try:
        parsed_url = urllib.parse.urlparse(download_url)
        path_parts = parsed_url.path.split('/')
        
        # Prioritize getting extension from end of path
        if path_parts:
            last_part = path_parts[-1]
            if '.' in last_part:
                ext = Path(last_part).suffix.lower()
                if ext in AUDIO_EXTENSIONS:
                    return ext

        # Extract from query parameters (some CDN specify format via v parameter)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        v_param = query_params.get('v', [''])[0]
        if v_param and '.' in v_param:
            ext_from_v = Path(v_param).suffix.lower()
            if ext_from_v in AUDIO_EXTENSIONS:
                return ext_from_v
        
        # Default to common format
        logger.debug(f"Could not determine extension from URL: {download_url}")
        return ".mp3"
    except Exception as e:
        logger.warning(f"Failed to extract file extension: {e}")
        return ".mp3"


def _build_filename(song_name: str, artist: str, idx: Optional[int] = None) -> str:
    """Build safe filename"""
    safe_song_name = clean_filename(song_name)
    
    if not safe_song_name:
        return "Unknown_Song"
        
    add_index = config.should_add_index()
    index_format = config.get_index_format()

    # Check if filename will be too long, and truncate artist name if needed
    MAX_FILENAME_LENGTH = 200
    
    def build_with_artist(artists: list) -> str:
        """Build filename with given artist list"""
        safe_artists = [clean_filename(a.strip()) for a in artists if a.strip()]
        artist_str = ', '.join(safe_artists)
        
        if idx is not None and add_index:
            formatted_index = f"{idx:{index_format}}"
            return f"{formatted_index} - {artist_str} - {safe_song_name}"
        else:
            return f"{artist_str} - {safe_song_name}"

    # Parse original artist list
    artist_parts = [a.strip() for a in artist.split(',') if a.strip()]
    
    # Try with all artists first
    filename = build_with_artist(artist_parts)
    
    # If too long, truncate artist names by keeping fewer artists
    if len(filename) > MAX_FILENAME_LENGTH:
        logger.warning(f"Filename too long ({len(filename)} chars), truncating artist list")
        
        # Keep only first N artists until filename fits
        for i in range(len(artist_parts)):
            truncated_filename = build_with_artist(artist_parts[:i+1])
            if len(truncated_filename) <= MAX_FILENAME_LENGTH:
                filename = truncated_filename
                break
        
        # If still too long, fall back to simple truncation
        if len(filename) > MAX_FILENAME_LENGTH:
            formatted_index = f"{idx:{index_format}}" if idx is not None and add_index else ""
            available_length = MAX_FILENAME_LENGTH - len(formatted_index) - 4 - len(safe_song_name) - 4
            if artist_parts:
                safe_artist = clean_filename(artist_parts[0])
                if len(safe_artist) > available_length:
                    safe_artist = safe_artist[:available_length]
                filename = build_with_artist([safe_artist])

    return filename


def _download_with_retry(url: str, timeout: int, reason: str) -> Optional[requests.Response]:
    """Download function with retry mechanism"""
    max_retries = 2  # Initial request + 1 retry
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            if response.status_code == HTTP_TOO_MANY_REQUESTS:
                random_sleep(min_delay=10.0, max_delay=15.0, 
                           reason=f"429 Too Many Requests - {reason} rate limit")
                continue  # Retry
            
            response.raise_for_status()
            return response
            
        except requests.Timeout:
            logger.warning(f"Download timeout ({reason}), attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                continue
            break
            
        except requests.RequestException as e:
            logger.error(f"Download failed ({reason}, attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                continue
            break
    
    return None


def download_song_and_resources(
    song_metadata: dict,
    download_dir: Optional[str] = None,
    idx: Optional[int] = None,
    current_index: Optional[int] = None,
    total_count: Optional[int] = None
) -> bool:
    """Download song and resources (lyrics, cover)"""
    # Validate metadata
    if not song_metadata:
        logger.error("Invalid song metadata: None")
        return False
        
    status = song_metadata.get('status', -1)
    if status != HTTP_OK and not song_metadata.get('success'):
        return False

    data = song_metadata.get('data', {})
    download_url = data.get('url')

    if not download_url:
        logger.error("No download URL in metadata")
        return False

    # Determine download directory
    download_dir = Path(download_dir or config.get_download_dir())
    try:
        download_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create download directory: {e}")
        return False

    # Build file path
    filename = _build_filename(data.get('name', 'Unknown'), data.get('ar_name', 'Unknown'), idx)
    file_extension = _extract_file_extension(download_url)
    
    music_file_path = download_dir / f"{filename}{file_extension}"
    lyric_file_path = download_dir / f"{filename}.lrc"
    cover_file_path = download_dir / f"{filename}.jpg"

    # Skip existing files
    if music_file_path.exists():
        logger.info(f"File already exists, skipping: {music_file_path.name}")
        return True

    progress_info = f"[{current_index} / {total_count}] " if current_index and total_count else ""
    logger.info(f"{progress_info}Starting download: {filename}")
    logger.info(f"File size: {data.get('size', 'Unknown')}")
    logger.info(f"Quality: {song_metadata.get('used_quality', data.get('level', 'unknown'))}")
    logger.info("-" * 60)

    # Download music file
    random_sleep(reason="Before downloading music file")
    response = _download_with_retry(download_url, config.get_timeout(), "music")
    if not response:
        return False

    try:
        total_size = int(response.headers.get('content-length', 0))
        
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

    # Prepare metadata for tagging
    metadata_for_tagging = dict(data)
    metadata_for_tagging['cover_path'] = str(cover_file_path) if cover_file_path.exists() else ''
    if idx is not None:
        metadata_for_tagging['track_number'] = str(idx)

    # Write metadata to file if configured
    if config.should_write_metadata():
        logger.info("\nWriting metadata...")
        if not write_metadata_to_file(music_file_path, metadata_for_tagging):
            for retry_count in range(config.get_max_retries()):
                logger.warning(f"Metadata writing failed, retrying ({retry_count + 1}/{config.get_max_retries()})...")
                if write_metadata_to_file(music_file_path, metadata_for_tagging):
                    break

    # Save lyrics to file if configured
    lyric = data.get('lyric', '')
    if lyric and config.should_write_lyrics():
        logger.info("Saving lyrics...")
        try:
            with open(lyric_file_path, 'w', encoding='utf-8') as f:
                f.write(lyric)
            logger.info(f"Lyrics saved: {lyric_file_path.name}")
        except (IOError, OSError) as e:
            logger.warning(f"Lyrics saving failed: {e}")

    # Download cover image if configured and available
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
            except (IOError, OSError) as e:
                logger.warning(f"Cover saving failed: {e}")

    # Add music cover to song file if configured
    if config.should_write_cover():
        logger.info("Adding cover to song file...")
        write_picture_to_file(music_file_path)

    return True


def download_song(song_id: str, level: Optional[str] = None) -> bool:
    """Download single song"""

    try:
        quality = level if level is not None else config.get_default_quality()
        from src.util.util_music_metadata import get_song_metadata_by_song_id
        metadata = get_song_metadata_by_song_id(song_id, quality)
        
        success = download_song_and_resources(metadata, idx=None)
        return success
    except Exception as e:
        logger.error(f"Failed to download song {song_id}: {e}")
        return False


def prepare_album_folder(album_metadata: dict, download_dir: Optional[str] = None) -> Optional[Path]:
    """Prepare album download folder"""
    try:
        download_dir = Path(download_dir or config.get_download_dir())
        
        album_name = album_metadata.get('album_name', 'Unknown Album')
        album_artist = album_metadata.get('album_artist', 'Unknown Artist')
        album_id = album_metadata.get('album_id', '')
        album_publish_time = album_metadata.get('album_publish_time')
        song_count = album_metadata.get('song_count', 0)
        raw_data = album_metadata.get('raw_data', {})

        # Format publish date
        publish_date_str = ''
        if album_publish_time:
            try:
                publish_date_str = time.strftime('%Y-%m-%d', time.localtime(album_publish_time / 1000))
            except (ValueError, OSError) as e:
                logger.warning(f"Could not convert publish time {album_publish_time}: {e}")

        # Get album description and cover
        album_description = raw_data.get('data', {}).get('album', {}).get('description', '')
        album_cover_url = raw_data.get('data', {}).get('album', {}).get('coverImgUrl', '').split('?')[0]
        logger.info(f"Album cover URL: {album_cover_url}")

        safe_album_name = clean_filename(album_name)
        safe_artist = clean_filename(album_artist)

        if publish_date_str:
            album_folder_name = f"{safe_artist} - {safe_album_name} ({publish_date_str})"
        else:
            album_folder_name = f"{safe_artist} - {safe_album_name}"
            
        album_folder_path = download_dir / album_folder_name
        album_folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created album folder: {album_folder_path}")

        # Create subdirectory for song files (e.g., TBD)
        sub_dir_name = config.get_sub_dir()
        song_folder_path = album_folder_path / sub_dir_name if sub_dir_name else album_folder_path
        song_folder_path.mkdir(parents=True, exist_ok=True)
        if sub_dir_name:
            logger.info(f"Created song subdirectory: {song_folder_path}")

        # Create album info file
        _create_album_description_file(
            str(album_folder_path), 
            album_name, 
            album_artist, 
            album_id,
            publish_date_str, 
            song_count, 
            album_description
        )

        # Create album ID file
        if album_id:
            _create_album_id_file(
                str(album_folder_path),
                album_id, 
                album_name, 
                album_artist,
                album_metadata.get('song_details', [])
            )

        # Download cover
        if album_cover_url and config.should_write_cover():
            _download_album_cover(str(album_folder_path), album_cover_url)

        logger.info(f"Album folder prepared successfully: {song_folder_path}")
        return song_folder_path

    except Exception as e:
        logger.error(f"Failed to prepare album folder: {e}")
        return None


def _create_album_description_file(folder_path: str, album_name: str, album_artist: str, album_id: str,
                                   publish_date_str: str, song_count: int, description: str) -> None:
    """Create album description file"""
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    description_file_path = folder_path / 'album_info.txt'
    try:
        lines = [
            f"Album: {album_name}",
            f"Artist: {album_artist}",
            f"Album ID: {album_id}",
            f"Publish Date: {publish_date_str}" if publish_date_str else "",
            f"Song Count: {song_count}",
            "=" * 60,
            "Description:",
            description if description else "No description available",
            ""
        ]
        
        with open(description_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(line for line in lines if line))
        logger.info(f"Created album description file: {description_file_path.name}")
    except (IOError, OSError) as e:
        logger.error(f"Failed to create description file: {e}")


def _create_album_id_file(folder_path: str, album_id: str, album_name: str, album_artist: str,
                          song_details: List[dict]) -> None:
    """Create album ID file"""
    folder_path = Path(folder_path)
    
    album_id_file_path = folder_path / f"{album_id}.txt"
    try:
        lines = [
            f"Album ID: {album_id}",
            f"Album: {album_name}",
            f"Artist: {album_artist}",
            "=" * 60,
            "Songs:"
        ]
        
        if song_details:
            for song_detail in song_details:
                idx = song_detail.get('index', 0)
                song_name = song_detail.get('name', 'Unknown')
                song_id = song_detail.get('id', '')
                song_artists = song_detail.get('artists', 'Unknown Artist')
                lines.append(f"{idx}. {song_name} - {song_artists} (ID: {song_id})")
        else:
            lines.append("No song information available")

        with open(album_id_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
            
        logger.info(f"Created album ID file: {album_id_file_path.name}")
    except (IOError, OSError) as e:
        logger.error(f"Failed to create album ID file: {e}")


def _download_album_cover(folder_path: str, cover_url: str) -> None:
    """Download album cover"""
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    cover_file_path = folder_path / 'cover.jpg'
    try:
        logger.info("Downloading album cover...")
        random_sleep(reason="Before downloading album cover")
        
        response = requests.get(cover_url, timeout=10)

        if response.status_code == HTTP_TOO_MANY_REQUESTS:
            logger.warning("Received 429 Too Many Requests while downloading album cover.")
            random_sleep(min_delay=10.0, max_delay=15.0, 
                        reason="429 Too Many Requests - album cover download rate limit")
            response = requests.get(cover_url, timeout=10)

        response.raise_for_status()

        with open(cover_file_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Album cover downloaded: {cover_file_path.name}")
    except (IOError, OSError, requests.RequestException) as e:
        logger.warning(f"Album cover download failed: {e}")


def _count_downloaded_songs(download_dir: str) -> Dict[str, int]:
    """Count files in download directory"""
    download_path = Path(download_dir)
    if not download_path.exists():
        return {}

    ext_counter = Counter()
    
    try:
        for file_path in download_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
                ext_counter[file_path.suffix.lower()] += 1
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to scan download directory: {e}")
        return {}

    return dict(ext_counter)


def prepare_playlist_folder(playlist_metadata: dict, download_dir: Optional[str] = None) -> Optional[Path]:
    """Prepare playlist download folder with info files"""
    try:
        download_dir = Path(download_dir or config.get_download_dir())
        
        playlist_name = playlist_metadata.get('playlist_name', 'Unknown Playlist')
        playlist_creator = playlist_metadata.get('playlist_creator', 'Unknown Creator')
        playlist_id = playlist_metadata.get('playlist_id', '')
        song_count = playlist_metadata.get('song_count', 0)

        safe_playlist_name = clean_filename(playlist_name)
        safe_creator = clean_filename(playlist_creator)
        playlist_folder_name = f"{safe_creator} - {safe_playlist_name}"
            
        playlist_folder_path = download_dir / playlist_folder_name
        playlist_folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created playlist folder: {playlist_folder_path}")

        # Create subdirectory for song files (e.g., TBD)
        sub_dir_name = config.get_sub_dir()
        song_folder_path = playlist_folder_path / sub_dir_name if sub_dir_name else playlist_folder_path
        song_folder_path.mkdir(parents=True, exist_ok=True)
        if sub_dir_name:
            logger.info(f"Created song subdirectory: {song_folder_path}")

        # Create playlist info file
        info_file_path = playlist_folder_path / 'playlist_info.txt'
        try:
            lines = [
                f"Playlist: {playlist_name}",
                f"Creator: {playlist_creator}",
                f"Playlist ID: {playlist_id}",
                f"Song Count: {song_count}",
                "=" * 60,
                ""
            ]
            with open(info_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(line for line in lines if line))
            logger.info(f"Created playlist info file: {info_file_path.name}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to create playlist info file: {e}")

        # Create playlist ID file with song list
        id_file_path = playlist_folder_path / f"{playlist_id}.txt"
        try:
            song_details = playlist_metadata.get('song_details', [])
            lines = [
                f"Playlist ID: {playlist_id}",
                f"Playlist: {playlist_name}",
                f"Creator: {playlist_creator}",
                "=" * 60,
                "Songs:"
            ]
            if song_details:
                for song_detail in song_details:
                    idx = song_detail.get('index', 0)
                    song_name = song_detail.get('name', 'Unknown')
                    sid = song_detail.get('id', '')
                    song_artists = song_detail.get('artists', 'Unknown Artist')
                    lines.append(f"{idx}. {song_name} - {song_artists} (ID: {sid})")
            else:
                lines.append("No song information available")

            with open(id_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
            logger.info(f"Created playlist ID file: {id_file_path.name}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to create playlist ID file: {e}")

        logger.info(f"Playlist folder prepared successfully: {song_folder_path}")
        return song_folder_path

    except Exception as e:
        logger.error(f"Failed to prepare playlist folder: {e}")
        return None


def _download_songs_from_metadata(metadata: Any,
                                  index_ids: List[int], level: str, is_album: bool = True,
                                  download_dir: Optional[str] = None) -> None:
    """Download songs from metadata"""
    failed_indexes = []

    # Ensure index_ids is a list
    if not isinstance(index_ids, list):
        index_ids = []

    for index, song_detail in enumerate(metadata.song_details):
        song_id = song_detail.get('id')
        song_index = song_detail.get('index', 0)

        if not song_id:
            logger.warning(f"Song at index {index} has no ID, skipping...")
            continue

        logger.info(f"{index + 1}. {song_detail}")

        # Check if in download list
        if index_ids and song_index not in index_ids:
            logger.info(f"Skipping: {song_index} is not in download list")
            continue

         # Fetch and download song
        from src.util.util_music_metadata import get_song_metadata_by_song_id
        song_metadata = get_song_metadata_by_song_id(song_id, level)
        success = download_song_and_resources(
            song_metadata,
            download_dir=download_dir,
            idx=song_index if is_album else None,
            current_index=index + 1,
            total_count=len(metadata.song_details)
        )
        
        if not success:
            failed_indexes.append(song_index)

     # Summary
    name_info = f"{metadata.album_artist} - {metadata.album_name}" if is_album else f"playlist {metadata.playlist_id}"
    logger.info(f"\nCompleted downloading {name_info}")
    logger.info(f"Total songs in list: {len(metadata.song_details)}")
    
     # Output failed songs
    if failed_indexes:
        logger.warning(f"Failed to download {len(failed_indexes)} song(s)")
        for idx in sorted(failed_indexes):
            logger.warning(f"  - Index {idx}")

     # Count downloaded files
    stats = _count_downloaded_songs(config.get_download_dir())
    if stats:
        total_count = sum(stats.values())
        logger.info(f"\nDownload Statistics by File Extension:")
        for ext, count in sorted(stats.items()):
            logger.info(f"  {ext.upper()}: {count} files")
        logger.info(f"  Total: {total_count} files")


def download_album(album_id: str, index_ids: List[int] = None, level: Optional[str] = None) -> bool:
    """Download album"""
    try:
        if not album_id:
            logger.error("Album ID cannot be empty")
            return False
            
        quality = level if level is not None else config.get_default_quality()
        
         # Ensure index_ids is a list
        index_list = index_ids if isinstance(index_ids, list) else []

        from src.util.util_music_metadata import get_song_ids_by_album_id
        album_metadata = get_song_ids_by_album_id(album_id)
        if album_metadata is None:
            logger.error("Failed to get album metadata")
            return False

     # Prepare album folder
        album_folder = prepare_album_folder(album_metadata.to_dict())
        if not album_folder:
            logger.error("Failed to create album folder")
            return False
            
        _download_songs_from_metadata(album_metadata, index_list, quality, is_album=True,
                                      download_dir=str(album_folder))
        return True
        
    except Exception as e:
        logger.error(f"Failed to download album {album_id}: {e}")
        return False


def download_playlist(playlist_id: str, index_ids: List[int] = None, level: Optional[str] = None) -> bool:
    """Download playlist"""
    try:
        if not playlist_id:
            logger.error("Playlist ID cannot be empty")
            return False
            
        quality = level if level is not None else config.get_default_quality()
        
         # Ensure index_ids is a list
        index_list = index_ids if isinstance(index_ids, list) else []

        from src.util.util_music_metadata import get_song_ids_by_playlist_id
        playlist_metadata = get_song_ids_by_playlist_id(playlist_id)
        if playlist_metadata is None:
            logger.error("Failed to get playlist metadata")
            return False

     # Prepare playlist folder
        playlist_folder = prepare_playlist_folder(playlist_metadata.to_dict())
        if not playlist_folder:
            logger.error("Failed to create playlist folder")
            return False

        _download_songs_from_metadata(playlist_metadata, index_list, quality, is_album=False,
                                      download_dir=str(playlist_folder))
        return True
        
    except Exception as e:
        logger.error(f"Failed to download playlist {playlist_id}: {e}")
        return False