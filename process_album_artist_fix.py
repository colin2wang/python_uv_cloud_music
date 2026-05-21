import os
from pathlib import Path
from typing import Optional, List

from mutagen.flac import FLAC
from mutagen.id3 import ID3, TPE1
from mutagen.mp4 import MP4

from config_manager import config
from logging_config import setup_logger
from utils import AUDIO_EXTENSIONS, clean_filename

# Create logger
logger = setup_logger(__name__)


class AlbumArtistFixer:
    """
    Album Artist Fixer

    Scans album folders and fixes artist tags in music files
    by replacing '/' separator with ', ' and using array format for multiple artists
    """
    
    def __init__(self, album_folder: str):
        """
        Initialize the artist fixer

        Args:
            album_folder: Path to the album folder to scan
        """
        self.album_folder = Path(album_folder)
        self.album_info = {}
        
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
            
            logger.info(f"Album info loaded: {self.album_info.get('album_name', 'Unknown')} - "
                       f"{self.album_info.get('album_artist', 'Unknown Artist')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load album_info.txt: {str(e)}")
            return False
    
    def split_artists(self, artist_string: str) -> List[str]:
        """
        Split artist string into list of artists
        
        Args:
            artist_string: Artist string that may contain '/', ',', or other separators
        
        Returns:
            List of individual artist names
        """
        if not artist_string:
            return []
        
        # Replace common separators with comma + space
        normalized = artist_string.replace('/', ', ').replace('&', ', ').replace('、', ', ')
        
        # Split by comma and strip whitespace
        artists = [artist.strip() for artist in normalized.split(',')]
        
        # Filter out empty strings
        artists = [artist for artist in artists if artist]
        
        return artists
    
    def check_and_fix_artist_in_file(self, file_path: Path) -> tuple[bool, bool, Optional[str], Optional[List[str]]]:
        """
        Check and fix artist tag in music file
        
        Args:
            file_path: Path to music file
        
        Returns:
            tuple: (has_slash, is_fixed, old_artist_string, new_artist_list)
        """
        ext = file_path.suffix.lower()
        has_slash = False
        is_fixed = False
        old_artist_string = None
        new_artist_list = None
        
        logger.info(f"Checking artist tag in: {file_path.name}")
        
        try:
            if ext in ['.mp3', '.mp2', '.mp1']:
                # Process MP3 files
                audio = ID3(file_path)
                
                # Get artist tag (TPE1)
                if 'TPE1' in audio:
                    artist_frame = audio['TPE1']
                    if hasattr(artist_frame, 'text') and artist_frame.text:
                        # text can be a list of artists or a single string
                        if len(artist_frame.text) == 1:
                            current_artist = str(artist_frame.text[0])
                        else:
                            current_artist = ', '.join([str(t) for t in artist_frame.text])
                        
                        old_artist_string = current_artist
                        
                        # Check if contains '/'
                        if '/' in current_artist:
                            has_slash = True
                            logger.info(f"  Found '/' in artist tag: {current_artist}")
                            
                            # Split into array of artists
                            artist_list = self.split_artists(current_artist)
                            new_artist_list = artist_list
                            
                            # Update the tag with array format
                            audio['TPE1'] = TPE1(encoding=3, text=artist_list)
                            audio.save()
                            is_fixed = True
                            logger.info(f"  Fixed artist tag to array: {artist_list}")
                        else:
                            logger.info(f"  No '/' found in artist tag: {current_artist}")
                    else:
                        logger.debug(f"  No artist text found")
                else:
                    logger.debug(f"  No TPE1 tag found")
                    
            elif ext == '.flac':
                # Process FLAC files
                audio = FLAC(file_path)
                
                # Get artist tag
                if 'ARTIST' in audio:
                    # ARTIST can be a list of artists or a single string
                    current_artists = audio['ARTIST']
                    
                    # Check each artist in the list
                    needs_fix = False
                    all_artists_str = ', '.join(current_artists) if isinstance(current_artists, list) else str(current_artists)
                    old_artist_string = all_artists_str
                    
                    # Check if any artist contains '/'
                    for artist in current_artists:
                        if '/' in str(artist):
                            needs_fix = True
                            has_slash = True
                            break
                    
                    if needs_fix:
                        logger.info(f"  Found '/' in artist tag: {all_artists_str}")
                        
                        # Split into array of artists
                        artist_list = self.split_artists(all_artists_str)
                        new_artist_list = artist_list
                        
                        # Update the tag with array format
                        audio['ARTIST'] = artist_list
                        audio.save()
                        is_fixed = True
                        logger.info(f"  Fixed artist tag to array: {artist_list}")
                    else:
                        logger.info(f"  No '/' found in artist tag: {all_artists_str}")
                else:
                    logger.debug(f"  No ARTIST tag found")
            
            elif ext in ['.m4a', '.mp4', '.aac']:
                # Process MP4/AAC files
                audio = MP4(file_path)
                
                if audio.tags and '\xa9ART' in audio.tags:
                    current_artists = audio.tags['\xa9ART']
                    
                    # MP4 stores artists as a list
                    all_artists_str = ', '.join(current_artists) if isinstance(current_artists, list) else str(current_artists)
                    old_artist_string = all_artists_str
                    
                    # Check if any artist contains '/'
                    needs_fix = False
                    for artist in current_artists:
                        if '/' in str(artist):
                            needs_fix = True
                            has_slash = True
                            break
                    
                    if needs_fix:
                        logger.info(f"  Found '/' in artist tag: {all_artists_str}")
                        
                        # Split into array of artists
                        artist_list = self.split_artists(all_artists_str)
                        new_artist_list = artist_list
                        
                        # Update the tag with array format
                        audio.tags['\xa9ART'] = artist_list
                        audio.save()
                        is_fixed = True
                        logger.info(f"  Fixed artist tag to array: {artist_list}")
                    else:
                        logger.info(f"  No '/' found in artist tag: {all_artists_str}")
                else:
                    logger.debug(f"  No \\xa9ART tag found")
            
            else:
                logger.warning(f"Unsupported format: {ext}")
                return False, False, None, None
                
        except Exception as e:
            logger.error(f"Failed to check/fix artist tag: {str(e)}")
            return False, False, None, None
        
        return has_slash, is_fixed, old_artist_string, new_artist_list
    
    def rebuild_filename_from_tag(self, file_path: Path, old_artist_string: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Rebuild filename based on artist tag fix. Parse the original filename to extract
        song name and index, then rebuild with corrected artist names.
        
        Args:
            file_path: Path to music file
            old_artist_string: Original artist string from tag (contains '/')
        
        Returns:
            tuple: (is_renamed, old_filename, new_filename)
        """
        filename = file_path.name
        stem = file_path.stem
        suffix = file_path.suffix
        
        # Extract artist names from the old artist string
        # Split by '/' to get individual artists
        artists_with_slash = [a.strip() for a in old_artist_string.split('/') if a.strip()]
        
        if len(artists_with_slash) < 2:
            logger.debug(f"  Artist string doesn't contain multiple artists: {old_artist_string}")
            return False, None, None
        
        # Build correct artist part with ', ' separator
        correct_artist_part = ', '.join(artists_with_slash)
        clean_correct_artist = clean_filename(correct_artist_part)
        
        logger.info(f"  Rebuilding filename based on artist fix: {filename}")
        logger.info(f"  Artists from tag: {artists_with_slash}")
        logger.info(f"  Correct artist part: {correct_artist_part}")
        
        # Parse original filename to extract components
        # Pattern 1: "{index} - {artist} - {song_name}"
        # Pattern 2: "{artist} - {song_name}"
        
        idx = None
        song_name = None
        original_artist_in_filename = None
        
        # Try pattern with index first
        if ' - ' in stem:
            parts = stem.split(' - ', 2)
            if len(parts) == 3:
                # Check if first part is an index (number)
                try:
                    idx = int(parts[0].strip())
                    original_artist_in_filename = parts[1].strip()
                    song_name = parts[2].strip()
                    logger.info(f"  Parsed filename: idx={idx}, artist='{original_artist_in_filename}', song='{song_name}'")
                except ValueError:
                    # First part is not a number, use pattern without index
                    original_artist_in_filename = parts[0].strip()
                    song_name = parts[1].strip() if len(parts) > 1 else ''
                    logger.info(f"  Parsed filename (no index): artist='{original_artist_in_filename}', song='{song_name}'")
            elif len(parts) == 2:
                original_artist_in_filename = parts[0].strip()
                song_name = parts[1].strip()
                logger.info(f"  Parsed filename (no index): artist='{original_artist_in_filename}', song='{song_name}'")
        
        if not song_name:
            logger.warning(f"  Could not parse filename: {filename}")
            return False, None, None
        
        # Rebuild filename with correct artist
        clean_song_name = clean_filename(song_name)
        
        if idx is not None:
            # Get index format from config or detect from original filename
            index_format = config.get_index_format()
            formatted_index = f"{idx:{index_format}}"
            new_stem = f"{formatted_index} - {clean_correct_artist} - {clean_song_name}"
        else:
            new_stem = f"{clean_correct_artist} - {clean_song_name}"
        
        new_filename = new_stem + suffix
        
        if new_filename != filename:
            try:
                new_file_path = file_path.parent / new_filename
                file_path.rename(new_file_path)
                logger.info(f"  Renamed file: {filename} -> {new_filename}")
                return True, filename, new_filename
            except Exception as e:
                logger.error(f"  Failed to rename file: {str(e)}")
                return False, filename, None
        
        logger.info(f"  Filename already correct: {filename}")
        return False, None, None
    
    def scan_and_fix_artists(self) -> dict:
        """
        Scan album folder and fix artist tags and filenames for all music files.

        Returns:
            Dictionary with scan and fix results
        """
        logger.info("=" * 60)
        logger.info(f"Starting artist fix for album: {self.album_folder}")
        logger.info("=" * 60)

        # Load album info (optional, just for logging)
        self.load_album_info()

        # Find all music files in album folder
        music_files = []
        for ext in AUDIO_EXTENSIONS:
            music_files.extend(self.album_folder.glob(f"*{ext}"))

        if not music_files:
            logger.warning("No music files found in album folder")
            return {
                'success': False,
                'message': 'No music files found in album folder',
                'album_folder': str(self.album_folder)
            }

        logger.info(f"Found {len(music_files)} music files to check")

        # Process each music file
        results = {
            'success': True,
            'album_folder': str(self.album_folder),
            'album_name': self.album_info.get('album_name', 'Unknown'),
            'total_files': len(music_files),
            'files_with_slash': 0,
            'files_fixed': 0,
            'files_renamed': 0,
            'files_skipped': 0,
            'details': []
        }

        for idx, file_path in enumerate(music_files, 1):
            logger.info("-" * 60)
            logger.info(f"[{idx}/{len(music_files)}] Processing: {file_path.name}")
            
            # Step 1: Check and fix artist tag
            has_slash, is_fixed, old_artist, new_artist = self.check_and_fix_artist_in_file(file_path)
            
            if has_slash:
                results['files_with_slash'] += 1
                
                if is_fixed:
                    results['files_fixed'] += 1
                    logger.info(f"  ✓ Artist tag fixed")
                    
                    detail = {
                        'file': file_path.name,
                        'action': 'artist_fixed',
                        'old_artist': old_artist,
                        'new_artist': new_artist
                    }
                    
                    # Step 2: Rebuild filename based on corrected artist tag
                    is_renamed, old_filename, new_filename = self.rebuild_filename_from_tag(file_path, old_artist)
                    
                    if is_renamed:
                        results['files_renamed'] += 1
                        logger.info(f"  ✓ File renamed")
                        detail['file_rename'] = {
                            'old': old_filename,
                            'new': new_filename
                        }
                    else:
                        logger.info(f"  ℹ Filename already correct or couldn't be rebuilt")
                    
                    results['details'].append(detail)
                else:
                    logger.warning(f"  ✗ Artist tag has '/' but failed to fix")
                    results['details'].append({
                        'file': file_path.name,
                        'action': 'failed',
                        'reason': 'Failed to fix artist tag',
                        'old_artist': old_artist
                    })
            else:
                logger.info(f"  ✓ No '/' found, skipping")
                results['files_skipped'] += 1
                results['details'].append({
                    'file': file_path.name,
                    'action': 'skipped',
                    'reason': 'No slash in artist tag'
                })
        
        # Summary
        logger.info("=" * 60)
        logger.info("Artist Fix Summary")
        logger.info("=" * 60)
        logger.info(f"Album: {self.album_info.get('album_name', 'Unknown')}")
        logger.info(f"Total files: {results['total_files']}")
        logger.info(f"Files with '/': {results['files_with_slash']}")
        logger.info(f"Files fixed: {results['files_fixed']}")
        logger.info(f"Files renamed: {results['files_renamed']}")
        logger.info(f"Files skipped: {results['files_skipped']}")
        logger.info("=" * 60)
        
        return results


def fix_album_artists(album_folder: str) -> dict:
    """
    Convenience function to fix album artists.

    Args:
        album_folder: Path to album folder

    Returns:
        Dictionary with fix results
    """
    fixer = AlbumArtistFixer(album_folder)
    return fixer.scan_and_fix_artists()


def scan_multiple_albums_for_artists(album_folders: list[str]) -> list[dict]:
    """
    Scan and fix artists for multiple album folders.

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
            result = fix_album_artists(folder)
            results.append(result)
        else:
            logger.warning(f"Skipping non-directory: {folder}")

    return results


if __name__ == "__main__":
    # Example usage

    # Example 1: Fix single album folder
    # Provide your album folder path here
    album_folder_path = r"F:\我的音乐\我的专辑\华语流行\揽佬SKAI ISYOURGOD - 八方来财 (2024-08-20)"
    fix_album_artists(album_folder_path)

    # Example 2: Fix multiple album folders
    # download_dir = config.get_download_dir()
    # album_folders = [
    #     os.path.join(download_dir, folder)
    #     for folder in os.listdir(download_dir)
    #     if os.path.isdir(os.path.join(download_dir, folder))
    # ]
    # scan_multiple_albums_for_artists(album_folders)
