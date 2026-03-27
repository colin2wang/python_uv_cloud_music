import os
import re
import time
from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC
from mutagen.id3 import ID3, COMM
from mutagen.mp4 import MP4

from logging_config import setup_logger
from config_manager import config
from process_cloud_music import get_song_ids_by_album_id, get_song_metadata_by_song_id
from utils import get_audio_extension, clean_filename, safe_get

# Create logger
logger = setup_logger(__name__)


class AlbumLyricFixer:
    """
    Album Lyric Fixer
    
    Scans album folders and fixes truncated lyrics in music files
    by re-downloading complete lyrics from NetEase Cloud Music API
    """
    
    def __init__(self, album_folder: str):
        """
        Initialize the lyric fixer

        Args:
            album_folder: Path to the album folder to scan
        """
        self.album_folder = Path(album_folder)
        self.album_info = {}
        self.songs_metadata = []
        
    def load_album_info(self) -> bool:
        """
        Load album information from album_info.txt
        
        Returns:
            bool: Whether album info was loaded successfully
        """
        album_info_file = self.album_folder / 'album_info.txt'
        
        if not album_info_file.exists():
            logger.warning(f"album_info.txt not found in {self.album_folder}")
            return False
        
        try:
            with open(album_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse album info file
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'album':
                        self.album_info['album_name'] = value
                    elif key == 'artist':
                        self.album_info['album_artist'] = value
                    elif key == 'album id':
                        self.album_info['album_id'] = value
                    elif key == 'publish date':
                        self.album_info['publish_date'] = value
                    elif key == 'song count':
                        self.album_info['song_count'] = value
            
            logger.info(f"Album info loaded: {self.album_info.get('album_name', 'Unknown')} - "
                       f"{self.album_info.get('album_artist', 'Unknown Artist')}")
            logger.info(f"Album ID: {self.album_info.get('album_id', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load album_info.txt: {str(e)}")
            return False
    
    def fetch_album_songs(self) -> bool:
        """
        Fetch all songs from the album using NetEase API
        
        Returns:
            bool: Whether songs were fetched successfully
        """
        album_id = self.album_info.get('album_id')
        
        if not album_id:
            logger.error("Album ID not found in album_info.txt")
            return False
        
        try:
            logger.info("=" * 60)
            logger.info(f"Fetching songs from album ID: {album_id}")
            logger.info("=" * 60)
            
            # Get album songs
            album_metadata = get_song_ids_by_album_id(album_id)
            
            if not album_metadata.get('success'):
                logger.error(f"Failed to fetch album songs: {album_metadata.get('message', 'Unknown error')}")
                return False
            
            self.songs_metadata = album_metadata.get('song_details', [])
            
            logger.info(f"Successfully fetched {len(self.songs_metadata)} songs from album")
            for i, song in enumerate(self.songs_metadata, 1):
                logger.info(f"  {i}. {song['name']} - {song['artists']} (ID: {song['id']})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fetching album songs: {str(e)}")
            return False
    
    def find_music_file(self, song_name: str, artist: str) -> Optional[Path]:
        """
        Find music file in album folder by matching song name and artist
        
        Args:
            song_name: Song title
            artist: Artist name
        
        Returns:
            Path to music file or None
        """
        # Clean illegal characters from song name and artist
        safe_song_name = clean_filename(song_name)
        safe_artist = clean_filename(artist.replace('/', config.get_artist_delimiter_replacement()))
        
        # Keep original artist name for generating variations (before cleaning illegal chars)
        original_artist = artist
        
        # Supported audio formats
        audio_extensions = ['.mp3', '.flac', '.m4a', '.mp4', '.aac']
        
        logger.info(f"Searching for file with song_name: {safe_song_name}, artist: {safe_artist}")
        logger.info(f"Original artist: {original_artist}")
        logger.debug(f"Album folder: {self.album_folder}")
        
        # Try to match file with pattern: {index} - {artist} - {title}
        for ext in audio_extensions:
            # Pattern with index
            pattern_with_index = f"* - {safe_artist} - {safe_song_name}{ext}"
            matches = list(self.album_folder.glob(pattern_with_index))
            if matches:
                logger.info(f"Found music file (with index): {matches[0].name}")
                return matches[0]
            
            # Pattern without index
            pattern_without_index = f"{safe_artist} - {safe_song_name}{ext}"
            matches = list(self.album_folder.glob(pattern_without_index))
            if matches:
                logger.info(f"Found music file (without index): {matches[0].name}")
                return matches[0]
        
        # Try fuzzy matching (partial match) - more flexible
        logger.debug("Starting fuzzy matching...")

        # List all music files for debugging
        all_music_files = []
        for ext in audio_extensions:
            all_music_files.extend(self.album_folder.glob(f"*{ext}"))
        logger.debug(f"Total music files found: {len(all_music_files)}")
        for mf in all_music_files[:10]:  # Log first 10 files
            logger.debug(f"  {mf.name}")

        for file_path in all_music_files:
                filename_lower = file_path.name.lower()
                song_name_lower = safe_song_name.lower()
                artist_lower = safe_artist.lower()
                original_artist_lower = original_artist.lower()
                
                logger.debug(f"Checking file: {file_path.name}")
                
                # Generate variations of artist name with different separators and orders
                artist_variations = [artist_lower, original_artist_lower]
                
                # Try different separator variations for safe_artist (with _)
                separators_safe = ['_', ', ', ',', ' & ', '&']
                for sep1 in separators_safe:
                    if sep1 in artist_lower:
                        # Replace with all other separators
                        for sep2 in separators_safe:
                            if sep1 != sep2:
                                # Forward order
                                variation = artist_lower.replace(sep1, sep2)
                                if variation not in artist_variations:
                                    artist_variations.append(variation)
                                
                                # Reversed order
                                parts = [p.strip() for p in artist_lower.split(sep1) if p.strip()]
                                if len(parts) >= 2:
                                    reversed_variation = sep2.join(reversed(parts))
                                    if reversed_variation not in artist_variations:
                                        artist_variations.append(reversed_variation)
                
                # Try different separator variations for original_artist (with /)
                separators_original = ['/', ', ', ',', ' & ', '&']
                for sep1 in separators_original:
                    if sep1 in original_artist_lower:
                        # Replace with all other separators
                        for sep2 in separators_original:
                            if sep1 != sep2:
                                # Forward order
                                variation = original_artist_lower.replace(sep1, sep2)
                                if variation not in artist_variations:
                                    artist_variations.append(variation)
                                
                                # Reversed order
                                parts = [p.strip() for p in original_artist_lower.split(sep1) if p.strip()]
                                if len(parts) >= 2:
                                    reversed_variation = sep2.join(reversed(parts))
                                    if reversed_variation not in artist_variations:
                                        artist_variations.append(reversed_variation)
                
                # Debug: Log variations for first file if debug level
                if logger.level <= 10:  # DEBUG level
                    logger.debug(f"Artist variations for '{artist_lower}': {artist_variations}")
                else:
                    # Log variations for the song we're looking for
                    if song_name_lower in filename_lower:
                        logger.info(f"  Song name matched in: {file_path.name}")
                        logger.info(f"  Checking artist variations: {artist_variations}")
                
                # Try each artist variation
                for artist_variant in artist_variations:
                    # Check if both song name and artist are in filename
                    if song_name_lower in filename_lower and artist_variant in filename_lower:
                        logger.info(f"Found music file (fuzzy match): {file_path.name}")
                        logger.info(f"  Matched artist variation: '{artist_variant}'")
                        return file_path
                
                # Try matching with song name only (for instrumental tracks)
                if song_name_lower in filename_lower and len(song_name_lower) > 3:
                    # Extract just the song name part (remove special chars for comparison)
                    clean_song = re.sub(r'[!？。、，\s]+', '', song_name_lower)
                    clean_filename_text = re.sub(r'[!？。、，\s]+', '', filename_lower)
                    if clean_song in clean_filename_text:
                        logger.info(f"Found music file (song name match): {file_path.name}")
                        return file_path

        logger.warning(f"Music file not found for: {song_name} - {artist}")
        return None
    
    def download_complete_lyric(self, song_id: str) -> Optional[str]:
        """
        Download complete lyric for a song
        
        Args:
            song_id: NetEase song ID
        
        Returns:
            Complete lyric text or None
        """
        try:
            logger.info(f"Downloading lyric for song ID: {song_id}")
            
            # Get song metadata with complete lyric
            metadata = get_song_metadata_by_song_id(song_id)
            
            if not metadata or not metadata.get('success'):
                logger.error(f"Failed to get song metadata: {song_id}")
                return None
            
            lyric = metadata.get('data', {}).get('lyric', '')
            
            if not lyric:
                logger.warning(f"No lyric found for song ID: {song_id}")
                return None
            
            logger.info(f"Lyric downloaded successfully, length: {len(lyric)} characters")
            return lyric
            
        except Exception as e:
            logger.error(f"Error downloading lyric: {str(e)}")
            return None
    
    def fix_lyric_in_file(self, file_path: Path, lyric: str, song_id: str = None) -> bool:
        """
        Fix lyric tag in music file
        
        Args:
            file_path: Path to music file
            lyric: Complete lyric text
            song_id: Song ID for CMUSIC_ID tag
        
        Returns:
            bool: Whether lyric was fixed successfully
        """
        ext = file_path.suffix.lower()
        
        logger.info(f"Fixing lyric in: {file_path.name}")
        logger.info(f"  Lyric length: {len(lyric)} characters")
        
        try:
            if ext in ['.mp3', '.mp2', '.mp1']:
                # Process MP3 files
                audio = ID3(file_path)
                
                # Remove existing lyric
                comm_tags_to_remove = []
                for key in audio.keys():
                    if key.startswith('COMM'):
                        comm_tag = audio[key]
                        # Check if it's a lyric (empty description or eng language)
                        if hasattr(comm_tag, 'desc') and (comm_tag.desc == '' or comm_tag.lang == 'eng'):
                            comm_tags_to_remove.append(key)
                
                for tag_key in comm_tags_to_remove:
                    del audio[tag_key]
                
                # Add complete lyric (no length limit!)
                if lyric:
                    # Split long lyrics into multiple COMM tags if needed
                    # ID3v2 has a recommended limit but most players support longer
                    max_chunk_size = 5000  # Conservative chunk size
                    lyric_chunks = []
                    
                    if len(lyric) <= max_chunk_size:
                        lyric_chunks.append(lyric)
                    else:
                        # Split into chunks while trying to break at line boundaries
                        current_pos = 0
                        chunk_num = 0
                        while current_pos < len(lyric):
                            end_pos = min(current_pos + max_chunk_size, len(lyric))
                            
                            # Try to break at a newline
                            if end_pos < len(lyric):
                                last_newline = lyric.rfind('\n', current_pos, end_pos)
                                if last_newline > current_pos:
                                    end_pos = last_newline + 1
                            
                            lyric_chunks.append(lyric[current_pos:end_pos])
                            current_pos = end_pos
                            chunk_num += 1
                        
                        if chunk_num > 1:
                            logger.info(f"  Split lyric into {chunk_num} chunks")
                    
                    # Add first chunk as main lyric
                    # Note: Use encoding=1 (UTF-16 with BOM) to properly preserve newlines
                    audio.add(COMM(
                        encoding=1,
                        lang='eng',
                        desc='',
                        text=lyric_chunks[0]
                    ))

                    # Add additional chunks with numbered descriptions
                    for i, chunk in enumerate(lyric_chunks[1:], 2):
                        audio.add(COMM(
                            encoding=1,
                            lang='eng',
                            desc=f'Lyric Part {i}',
                            text=chunk
                        ))
                
                # Add Cloud Music Song ID
                if song_id:
                    from mutagen.id3 import TXXX
                    audio.add(TXXX(encoding=3, desc='CMUSIC_ID', text=song_id))
                
                audio.save()
                logger.info("MP3 lyric fixed successfully")
                return True
                
            elif ext == '.flac':
                # Process FLAC files
                audio = FLAC(file_path)
                
                # Add complete lyric (no length limit!)
                if lyric:
                    audio['LYRICS'] = lyric
                
                # Add Cloud Music Song ID
                if song_id:
                    audio['CMUSIC_ID'] = song_id
                
                audio.save()
                logger.info("FLAC lyric fixed successfully")
                return True
                
            elif ext in ['.m4a', '.mp4', '.aac']:
                # Process MP4/AAC files
                audio = MP4(file_path)

                if audio.tags is None:
                    audio.add_tags()

                # Add complete lyric (no 1000 character limit!)
                if lyric:
                    audio.tags['\xa9lyr'] = lyric

                audio.save()
                logger.info("MP4/AAC lyric fixed successfully")
                return True
                
            else:
                logger.warning(f"Unsupported format: {ext}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to fix lyric: {str(e)}")
            return False
    
    def also_save_as_lrc_file(self, file_path: Path, lyric: str) -> bool:
        """
        Also save lyric as .lrc file alongside the music file
        
        Args:
            file_path: Path to music file
            lyric: Complete lyric text
        
        Returns:
            bool: Whether lrc file was saved successfully
        """
        try:
            # Get directory and base filename
            file_dir = file_path.parent
            file_base_name = file_path.stem
            
            # Create .lrc file path
            lrc_file_path = file_dir / f"{file_base_name}.lrc"
            
            # Save lyric
            with open(lrc_file_path, 'w', encoding='utf-8') as f:
                f.write(lyric)
            
            logger.info(f"LRC file saved: {lrc_file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save LRC file: {str(e)}")
            return False
    
    def check_all_music_files_have_cmusic_id(self) -> tuple[bool, list[Path], set]:
        """
        Check if all music files in the album folder have CMUSIC_ID tag.

        Returns:
            tuple: (bool indicating if all files have CMUSIC_ID, list of music files found, set of filenames with CMUSIC_ID)
        """
        from utils import AUDIO_EXTENSIONS

        # Find all music files in album folder
        music_files = []
        for ext in AUDIO_EXTENSIONS:
            music_files.extend(self.album_folder.glob(f"*{ext}"))

        if not music_files:
            logger.warning("No music files found in album folder")
            return True, [], set()

        logger.info(f"Found {len(music_files)} music files to check for CMUSIC_ID tag")

        all_have_cmusic_id = True
        files_with_cmusic_id = set()

        for file_path in music_files:
            ext = file_path.suffix.lower()
            has_cmusic_id = False
            cmusic_id_value = None

            try:
                if ext in ['.mp3', '.mp2', '.mp1']:
                    audio = ID3(file_path)
                    # Check for TXXX frame with desc='CMUSIC_ID'
                    from mutagen.id3 import TXXX
                    for key in audio.keys():
                        if key.startswith('TXXX'):
                            frame = audio[key]
                            if hasattr(frame, 'desc') and frame.desc == 'CMUSIC_ID':
                                has_cmusic_id = True
                                # Extract the value (frame.text is a list)
                                if frame.text:
                                    cmusic_id_value = str(frame.text[0])
                                break

                elif ext == '.flac':
                    audio = FLAC(file_path)
                    has_cmusic_id = 'CMUSIC_ID' in audio
                    if has_cmusic_id:
                        # Extract the value (audio['CMUSIC_ID'] is a list)
                        cmusic_id_value = str(audio['CMUSIC_ID'][0])

                elif ext in ['.m4a', '.mp4', '.aac']:
                    audio = MP4(file_path)
                    # MP4 uses a special format for custom tags
                    has_cmusic_id = '----:com.apple.iTunes:CMUSIC_ID' in audio.tags if audio.tags else False
                    if has_cmusic_id:
                        # Extract the value (tag value is a list of bytes)
                        tag_value = audio.tags['----:com.apple.iTunes:CMUSIC_ID'][0]
                        if isinstance(tag_value, bytes):
                            cmusic_id_value = tag_value.decode('utf-8')
                        else:
                            cmusic_id_value = str(tag_value)

            except Exception as e:
                logger.warning(f"Error checking CMUSIC_ID in {file_path.name}: {str(e)}")
                has_cmusic_id = False

            if not has_cmusic_id:
                all_have_cmusic_id = False
                logger.info(f"  Missing CMUSIC_ID: {file_path.name}")
            else:
                files_with_cmusic_id.add(file_path.name)
                if cmusic_id_value:
                    logger.info(f"  Has CMUSIC_ID: {file_path.name} = {cmusic_id_value}")
                else:
                    logger.info(f"  Has CMUSIC_ID: {file_path.name}")

        return all_have_cmusic_id, music_files, files_with_cmusic_id

    def check_file_has_cmusic_id(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Check if a music file has CMUSIC_ID tag
        
        Args:
            file_path: Path to music file
        
        Returns:
            tuple: (bool indicating if file has CMUSIC_ID, the CMUSIC_ID value if exists)
        """
        ext = file_path.suffix.lower()
        has_cmusic_id = False
        cmusic_id_value = None
        
        try:
            if ext in ['.mp3', '.mp2', '.mp1']:
                audio = ID3(file_path)
                from mutagen.id3 import TXXX
                for key in audio.keys():
                    if key.startswith('TXXX'):
                        frame = audio[key]
                        if hasattr(frame, 'desc') and frame.desc == 'CMUSIC_ID':
                            has_cmusic_id = True
                            if frame.text:
                                cmusic_id_value = str(frame.text[0])
                            break
                            
            elif ext == '.flac':
                audio = FLAC(file_path)
                has_cmusic_id = 'CMUSIC_ID' in audio
                if has_cmusic_id:
                    cmusic_id_value = str(audio['CMUSIC_ID'][0])
            
            elif ext in ['.m4a', '.mp4', '.aac']:
                audio = MP4(file_path)
                has_cmusic_id = '----:com.apple.iTunes:CMUSIC_ID' in audio.tags if audio.tags else False
                if has_cmusic_id:
                    tag_value = audio.tags['----:com.apple.iTunes:CMUSIC_ID'][0]
                    if isinstance(tag_value, bytes):
                        cmusic_id_value = tag_value.decode('utf-8')
                    else:
                        cmusic_id_value = str(tag_value)
        
        except Exception as e:
            logger.warning(f"Error checking CMUSIC_ID in {file_path.name}: {str(e)}")
            has_cmusic_id = False
        
        return has_cmusic_id, cmusic_id_value

    def move_lrc_files_to_delete_subfolder(self) -> int:
        """
        Move all .lrc files in album folder to .delete subfolder
        
        Returns:
            int: Number of files moved
        """
        delete_folder = self.album_folder / '.delete'
        
        # Create .delete folder if it doesn't exist
        delete_folder.mkdir(exist_ok=True)
        logger.info(f"Created/verified .delete folder: {delete_folder}")
        
        # Find all .lrc files in album folder (not in subdirectories)
        lrc_files = list(self.album_folder.glob('*.lrc'))
        
        moved_count = 0
        for lrc_file in lrc_files:
            try:
                # Move file to .delete folder
                dest_file = delete_folder / lrc_file.name
                lrc_file.rename(dest_file)
                logger.info(f"Moved LRC file: {lrc_file.name} -> .delete/{lrc_file.name}")
                moved_count += 1
            except Exception as e:
                logger.error(f"Failed to move {lrc_file.name}: {str(e)}")
        
        logger.info(f"Total LRC files moved to .delete: {moved_count}")
        return moved_count
    
    def scan_and_fix_lyrics(self) -> dict:
        """
        Scan album folder and fix lyrics for all music files.

        Returns:
            Dictionary with scan and fix results
        """
        logger.info("=" * 60)
        logger.info(f"Starting lyric fix for album: {self.album_folder}")
        logger.info("=" * 60)

        # Step 1: Check if all music files already have CMUSIC_ID tag
        logger.info("-" * 60)
        logger.info("Checking if all music files already have CMUSIC_ID tag...")
        logger.info("-" * 60)

        all_have_cmusic_id, music_files, files_with_cmusic_id = self.check_all_music_files_have_cmusic_id()

        if all_have_cmusic_id:
            logger.info("=" * 60)
            logger.info("All music files already have CMUSIC_ID tag - Task completed")
            logger.info("=" * 60)
            return {
                'success': True,
                'message': 'All music files already have CMUSIC_ID tag',
                'album_folder': str(self.album_folder),
                'action': 'skipped',
                'reason': 'All files already have CMUSIC_ID',
                'total_files': len(music_files)
            }

        if not music_files:
            logger.error("No music files found in album folder")
            return {
                'success': False,
                'message': 'No music files found in album folder',
                'album_folder': str(self.album_folder)
            }

        logger.info(f"Found {len(music_files)} music files, some without CMUSIC_ID tag")
        logger.info(f"  Files with CMUSIC_ID: {len(files_with_cmusic_id)}")
        logger.info("Proceeding with lyric fix process...")

        # Step 2: Load album info
        if not self.load_album_info():
            return {
                'success': False,
                'message': 'Failed to load album info',
                'album_folder': str(self.album_folder)
            }

        # Step 3: Fetch album songs
        if not self.fetch_album_songs():
            return {
                'success': False,
                'message': 'Failed to fetch album songs',
                'album_folder': str(self.album_folder)
            }

        # Step 4: Process each song from API
        results = {
            'success': True,
            'album_folder': str(self.album_folder),
            'album_name': self.album_info.get('album_name', 'Unknown'),
            'album_id': self.album_info.get('album_id', ''),
            'total_songs': len(self.songs_metadata),
            'songs_fixed': 0,
            'songs_skipped': 0,
            'songs_failed': 0,
            'songs_not_found': 0,
            'lrc_files_moved': 0,
            'details': []
        }
        for idx, song in enumerate(self.songs_metadata, 1):
            song_id = song['id']
            song_name = song['name']
            song_artists = song['artists']
            
            logger.info("-" * 60)
            logger.info(f"[{idx}/{len(self.songs_metadata)}] Processing: {song_name} - {song_artists}")
            logger.info(f"  Song ID: {song_id}")
            
            # Find music file
            music_file = self.find_music_file(song_name, song_artists)
            
            if not music_file:
                logger.warning("Music file not found in album folder")
                results['songs_not_found'] += 1
                results['details'].append({
                    'song_name': song_name,
                    'artist': song_artists,
                    'song_id': song_id,
                    'action': 'not_found',
                    'reason': 'Music file not found'
                })
                continue

            # Check if file already has CMUSIC_ID (using Step 1 records)
            if music_file.name in files_with_cmusic_id:
                # File has CMUSIC_ID, read the value from file
                _, existing_cmusic_id = self.check_file_has_cmusic_id(music_file)
                logger.info(f"File already has CMUSIC_ID: {existing_cmusic_id}, skipping download and fix")
                results['songs_skipped'] += 1
                results['details'].append({
                    'song_name': song_name,
                    'artist': song_artists,
                    'song_id': song_id,
                    'file': music_file.name,
                    'action': 'skipped',
                    'reason': 'File already has CMUSIC_ID',
                    'cmusic_id': existing_cmusic_id
                })
                continue

            # Download complete lyric
            lyric = self.download_complete_lyric(song_id)

            if not lyric:
                logger.warning("Failed to download complete lyric")
                results['songs_failed'] += 1
                results['details'].append({
                    'song_name': song_name,
                    'artist': song_artists,
                    'song_id': song_id,
                    'action': 'failed',
                    'reason': 'Failed to download lyric'
                })
                continue

            # Fix lyric in music file
            if self.fix_lyric_in_file(music_file, lyric, song_id):
                results['songs_fixed'] += 1

                # Also save as .lrc file
                self.also_save_as_lrc_file(music_file, lyric)

                results['details'].append({
                    'song_name': song_name,
                    'artist': song_artists,
                    'song_id': song_id,
                    'file': music_file.name,
                    'action': 'fixed',
                    'lyric_length': len(lyric)
                })
            else:
                results['songs_failed'] += 1
                results['details'].append({
                    'song_name': song_name,
                    'artist': song_artists,
                    'song_id': song_id,
                    'file': music_file.name,
                    'action': 'failed',
                    'reason': 'Failed to write lyric'
                })

            # Add delay between requests to avoid rate limiting
            if idx < len(self.songs_metadata):
                delay = 2.0  # seconds
                logger.info(f"Waiting {delay} seconds before next song...")
                time.sleep(delay)
        
        # Step 5: Process music files without CMUSIC_ID that weren't matched above
        logger.info("-" * 60)
        logger.info("Checking for music files without CMUSIC_ID...")
        logger.info("-" * 60)

        # Track files that were already processed (matched with API songs)
        processed_files = set()
        for detail in results['details']:
            if 'file' in detail:
                processed_files.add(detail['file'])

        # Find files without CMUSIC_ID that haven't been processed
        for file_path in music_files:
            if file_path.name in processed_files:
                continue

            # Skip files that already have CMUSIC_ID (using Step 1 records)
            if file_path.name in files_with_cmusic_id:
                continue
            
            # File doesn't have CMUSIC_ID, try to find matching song
            logger.info("-" * 40)
            logger.info(f"Found file without CMUSIC_ID: {file_path.name}")
            
            # Extract song name and artist from filename
            # Try to match with pattern: {index} - {artist} - {title} or {artist} - {title}
            filename = file_path.stem  # filename without extension
            
            # Try to parse filename
            song_name = None
            artist_name = None
            
            # Pattern with index: "001 - 许茹芸 - 泪海"
            if ' - ' in filename:
                parts = filename.split(' - ')
                if len(parts) >= 3:
                    # Try to determine if first part is a number/index
                    try:
                        int(parts[0])
                        artist_name = parts[1].strip()
                        song_name = parts[2].strip()
                    except ValueError:
                        # First part is not a number, so it's {artist} - {song} format
                        artist_name = parts[0].strip()
                        song_name = parts[1].strip()
                elif len(parts) == 2:
                    artist_name = parts[0].strip()
                    song_name = parts[1].strip()
            
            if song_name and artist_name:
                logger.info(f"  Extracted from filename: Song='{song_name}', Artist='{artist_name}'")
                
                # Try to find matching song in API results
                matched_song = None
                for song in self.songs_metadata:
                    api_song_name = song['name']
                    api_artists = song['artists']
                    
                    # Normalize separators for comparison
                    normalized_artist = artist_name.replace(',', '/').replace(' ', '/')
                    normalized_api_artist = api_artists.replace(', ', '/')
                    
                    if song_name == api_song_name and normalized_artist in normalized_api_artist or normalized_api_artist in normalized_artist:
                        matched_song = song
                        break
                
                if matched_song:
                    song_id = matched_song['id']
                    logger.info(f"  Matched with song ID: {song_id}")
                    
                    # Download lyric
                    lyric = self.download_complete_lyric(song_id)
                    
                    if lyric:
                        if self.fix_lyric_in_file(file_path, lyric, song_id):
                            logger.info(f"  ✓ Fixed lyric and added CMUSIC_ID for: {file_path.name}")
                            results['songs_fixed'] += 1
                            self.also_save_as_lrc_file(file_path, lyric)
                            
                            results['details'].append({
                                'song_name': song_name,
                                'artist': artist_name,
                                'song_id': song_id,
                                'file': file_path.name,
                                'action': 'fixed',
                                'lyric_length': len(lyric)
                            })
                            
                            # Add delay
                            delay = 2.0
                            logger.info(f"Waiting {delay} seconds before next file...")
                            time.sleep(delay)
                        else:
                            logger.error(f"  ✗ Failed to write lyric to: {file_path.name}")
                            results['songs_failed'] += 1
                    else:
                        logger.warning(f"  ✗ Failed to download lyric for song ID: {song_id}")
                        results['songs_failed'] += 1
                else:
                    logger.warning(f"  ✗ No matching song found in API results")
                    results['songs_not_found'] += 1
            else:
                logger.warning(f"  ✗ Could not parse filename: {file_path.name}")
                results['songs_not_found'] += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("Lyric Fix Summary")
        logger.info("=" * 60)
        logger.info(f"Album: {self.album_info.get('album_name', 'Unknown')}")
        logger.info(f"Artist: {self.album_info.get('album_artist', 'Unknown')}")
        logger.info(f"Total songs in album: {results['total_songs']}")
        logger.info(f"Songs fixed: {results['songs_fixed']}")
        logger.info(f"Songs skipped (already fixed): {results['songs_skipped']}")
        logger.info(f"Songs not found: {results['songs_not_found']}")
        logger.info(f"Songs failed: {results['songs_failed']}")
        
        # Move all .lrc files to .delete subfolder
        logger.info("-" * 60)
        logger.info("Moving LRC files to .delete subfolder...")
        lrc_files_moved = self.move_lrc_files_to_delete_subfolder()
        logger.info(f"Moved {lrc_files_moved} LRC files to .delete folder")
        
        logger.info("=" * 60)
        
        return results


def fix_album_lyrics(album_folder: str) -> dict:
    """
    Convenience function to fix album lyrics.

    Args:
        album_folder: Path to album folder

    Returns:
        Dictionary with fix results
    """
    fixer = AlbumLyricFixer(album_folder)
    return fixer.scan_and_fix_lyrics()


def scan_multiple_albums_for_lyrics(album_folders: list[str]) -> list[dict]:
    """
    Scan and fix lyrics for multiple album folders.

    Args:
        album_folders: List of album folder paths

    Returns:
        List of results for each album
    """
    results = []

    for folder in album_folders:
        if os.path.isdir(folder):
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing album: {folder}")
            logger.info(f"{'='*80}\n")
            result = fix_album_lyrics(folder)
            results.append(result)
        else:
            logger.warning(f"Skipping non-directory: {folder}")

    return results


if __name__ == "__main__":
    # Example usage

    # Example 1: Fix single album folder
    # Provide your album folder path here
    album_folder_path = r"F:\Workspaces\JetBrains\PyCharm\python_uv_cloud_music\downloads\许茹芸 - 好歌茹芸 (2011-05-13)"
    fix_album_lyrics(album_folder_path)

    # Example 2: Fix multiple album folders
    # download_dir = config.get_download_dir()
    # album_folders = [
    #     os.path.join(download_dir, folder)
    #     for folder in os.listdir(download_dir)
    #     if os.path.isdir(os.path.join(download_dir, folder))
    # ]
    # scan_multiple_albums_for_lyrics(album_folders)
