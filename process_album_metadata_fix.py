import json
import os
from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, TYER, TRCK
from mutagen.mp4 import MP4, MP4Cover

from logging_config import setup_logger
from config_manager import config
from utils import (
    get_audio_extension, get_image_mime_type, get_mp4_image_format,
    parse_music_filename, find_cover_image
)

# Create logger
logger = setup_logger(__name__)


class AlbumMetadataFixer:
    """
    Album Metadata Fixer
    
    Scans album folders and fixes missing metadata in music files
    by parsing filenames and album_info.txt
    """
    
    def __init__(self, album_folder: str):
        """
        Initialize the metadata fixer
        
        Args:
            album_folder: Path to the album folder to scan
        """
        self.album_folder = Path(album_folder)
        self.album_info = {}
        self.cover_path = None
        
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
            return True
            
        except Exception as e:
            logger.error(f"Failed to load album_info.txt: {str(e)}")
            return False
    
    def find_cover_image(self) -> Optional[Path]:
        """
        Find cover image in the album folder.

        Returns:
            Path to cover image or None
        """
        cover_path = find_cover_image(self.album_folder)
        if cover_path:
            logger.info(f"Found cover image: {cover_path.name}")
            self.cover_path = cover_path
        else:
            logger.warning("No cover image found")
        return cover_path
    
    def parse_filename(self, filename: str) -> dict:
        """
        Parse music file filename to extract metadata.

        Expected format: {index} - {artist} - {title} or {artist} - {title}

        Args:
            filename: Filename without extension

        Returns:
            Dictionary with parsed metadata
        """
        result = parse_music_filename(filename)
        if not result['artist']:
            logger.warning(f"Could not parse filename, using as title: {filename}")
        else:
            logger.debug(f"Parsed filename: {result}")
        return result
    
    def check_metadata_status(self, file_path: Path) -> dict:
        """
        Check current metadata status of a music file.

        Args:
            file_path: Path to music file

        Returns:
            Dictionary with metadata status
        """
        ext = get_audio_extension(file_path)
        status = {
            'has_title': False,
            'has_artist': False,
            'has_album': False,
            'has_track_number': False,
            'has_cover': False,
            'needs_fix': False
        }
        
        try:
            if ext in ['.mp3', '.mp2', '.mp1']:
                audio = ID3(file_path)
                status['has_title'] = 'TIT2' in audio
                status['has_artist'] = 'TPE1' in audio
                status['has_album'] = 'TALB' in audio
                status['has_track_number'] = 'TRCK' in audio
                status['has_cover'] = any(key.startswith('APIC') for key in audio.keys())
                
            elif ext == '.flac':
                audio = FLAC(file_path)
                status['has_title'] = 'TITLE' in audio
                status['has_artist'] = 'ARTIST' in audio
                status['has_album'] = 'ALBUM' in audio
                status['has_track_number'] = 'TRACKNUMBER' in audio
                status['has_cover'] = len(audio.pictures) > 0
                
            elif ext in ['.m4a', '.mp4', '.aac']:
                audio = MP4(file_path)
                if audio.tags:
                    status['has_title'] = '\xa9nam' in audio.tags
                    status['has_artist'] = '\xa9ART' in audio.tags
                    status['has_album'] = '\xa9alb' in audio.tags
                    status['has_track_number'] = 'trkn' in audio.tags
                    status['has_cover'] = 'covr' in audio.tags
            
            # Determine if file needs fixing
            status['needs_fix'] = not (status['has_title'] and status['has_artist'] and status['has_album'])
            
        except Exception as e:
            logger.error(f"Error checking metadata for {file_path.name}: {str(e)}")
            status['needs_fix'] = True
        
        return status
    
    def fix_metadata(self, file_path: Path, parsed_info: dict,
                    track_number: Optional[str] = None) -> bool:
        """
        Fix metadata for a music file.

        Args:
            file_path: Path to music file
            parsed_info: Parsed information from filename
            track_number: Track number (optional, overrides parsed_info)

        Returns:
            bool: Whether metadata was fixed successfully
        """
        ext = get_audio_extension(file_path)
        
        # Use provided track number or parsed one
        final_track_number = track_number or parsed_info.get('track_number', '')
        
        # Prepare metadata
        title = parsed_info.get('title', file_path.stem)
        artist = parsed_info.get('artist', 'Unknown').split(',')
        album = self.album_info.get('album_name', '')
        
        logger.info(f"Fixing metadata for: {file_path.name}")
        logger.info(f"  Title: {title}")
        logger.info(f"  Artist: {artist}")
        logger.info(f"  Album: {album}")
        logger.info(f"  Track: {final_track_number}")
        
        try:
            if ext in ['.mp3', '.mp2', '.mp1']:
                return self._fix_mp3_metadata(file_path, title, artist, album, final_track_number)
            elif ext == '.flac':
                return self._fix_flac_metadata(file_path, title, artist, album, final_track_number)
            elif ext in ['.m4a', '.mp4', '.aac']:
                return self._fix_mp4_metadata(file_path, title, artist, album, final_track_number)
            else:
                logger.warning(f"Unsupported format: {ext}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to fix metadata: {str(e)}")
            return False
    
    def _fix_mp3_metadata(self, file_path: Path, title: str, artist: str,
                         album: str, track_number: str) -> bool:
        """Fix MP3 file metadata."""
        try:
            audio = ID3(file_path)

            # Add or update tags
            if title:
                audio.add(TIT2(encoding=3, text=title))
            if artist:
                audio.add(TPE1(encoding=3, text=artist))
            if album:
                audio.add(TALB(encoding=3, text=album))
            if track_number:
                audio.add(TRCK(encoding=3, text=track_number))

            # Add year
            publish_date = self.album_info.get('publish_date', '')
            year = publish_date[:4] if publish_date else '2024'
            audio.add(TYER(encoding=3, text=year))

            # Add cover if available
            if self.cover_path and self.cover_path.exists():
                try:
                    with open(self.cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        # Remove existing cover
                        apic_tags = [key for key in audio.keys() if key.startswith('APIC')]
                        for tag in apic_tags:
                            del audio[tag]

                        audio.add(APIC(
                            encoding=3,
                            mime=get_image_mime_type(self.cover_path),
                            type=3,
                            desc='Cover',
                            data=img_data
                        ))
                except Exception as e:
                    logger.warning(f"Failed to add cover: {e}")

            audio.save()
            logger.info("MP3 metadata fixed successfully")
            return True

        except Exception as e:
            logger.error(f"MP3 metadata fix failed: {e}")
            return False
    
    def _fix_flac_metadata(self, file_path: Path, title: str, artist: str,
                          album: str, track_number: str) -> bool:
        """Fix FLAC file metadata."""
        try:
            audio = FLAC(file_path)

            # Add or update tags
            if title:
                audio['TITLE'] = title
            if artist:
                audio['ARTIST'] = artist
            if album:
                audio['ALBUM'] = album
            if track_number:
                audio['TRACKNUMBER'] = track_number

            # Add publish date
            publish_date = self.album_info.get('publish_date', '')
            if publish_date:
                audio['DATE'] = publish_date[:4]

            # Add cover if available
            if self.cover_path and self.cover_path.exists():
                try:
                    with open(self.cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        picture = Picture()
                        picture.type = 3  # Cover (front)
                        picture.mime = get_image_mime_type(self.cover_path)
                        picture.data = img_data

                        # Remove existing pictures
                        audio.clear_pictures()
                        audio.add_picture(picture)
                except Exception as e:
                    logger.warning(f"Failed to add cover: {e}")

            audio.save()
            logger.info("FLAC metadata fixed successfully")
            return True

        except Exception as e:
            logger.error(f"FLAC metadata fix failed: {e}")
            return False
    
    def _fix_mp4_metadata(self, file_path: Path, title: str, artist: str,
                         album: str, track_number: str) -> bool:
        """Fix MP4/AAC file metadata."""
        try:
            audio = MP4(file_path)

            # Create metadata dictionary
            mp4_tags = {}

            if title:
                mp4_tags['\xa9nam'] = title
            if artist:
                mp4_tags['\xa9ART'] = artist
            if album:
                mp4_tags['\xa9alb'] = album
            if track_number:
                try:
                    mp4_tags['trkn'] = [(int(track_number), 0)]
                except ValueError:
                    pass

            # Add cover if available
            if self.cover_path and self.cover_path.exists():
                try:
                    with open(self.cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        mp4_tags['covr'] = [MP4Cover(img_data, imageformat=get_mp4_image_format(self.cover_path))]
                except Exception as e:
                    logger.warning(f"Failed to add cover: {e}")

            if audio.tags is None:
                audio.add_tags()

            audio.tags.update(mp4_tags)
            audio.save()
            logger.info("MP4/AAC metadata fixed successfully")
            return True

        except Exception as e:
            logger.error(f"MP4/AAC metadata fix failed: {e}")
            return False
    
    def scan_and_fix(self, fix_only_missing: bool = True) -> dict:
        """
        Scan album folder and fix metadata for all music files.

        Args:
            fix_only_missing: If True, only fix files with missing metadata.
                            If False, fix all files.

        Returns:
            Dictionary with scan results
        """
        logger.info("=" * 60)
        logger.info(f"Scanning album folder: {self.album_folder}")
        logger.info("=" * 60)
        
        # Load album info
        self.load_album_info()
        
        # Find cover image
        self.find_cover_image()
        
        # Supported audio formats
        audio_extensions = ['*.mp3', '*.flac', '*.m4a', '*.mp4', '*.aac']
        
        # Find all music files
        music_files = []
        for ext in audio_extensions:
            music_files.extend(self.album_folder.glob(ext))
        
        if not music_files:
            logger.warning("No music files found in album folder")
            return {
                'success': False,
                'message': 'No music files found',
                'files_scanned': 0,
                'files_fixed': 0
            }
        
        logger.info(f"Found {len(music_files)} music files")
        
        # Sort files by name
        music_files.sort(key=lambda x: x.name)
        
        # Process each file
        results = {
            'success': True,
            'album_folder': str(self.album_folder),
            'album_name': self.album_info.get('album_name', 'Unknown'),
            'files_scanned': len(music_files),
            'files_fixed': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'details': []
        }
        
        for idx, file_path in enumerate(music_files, 1):
            logger.info("-" * 60)
            logger.info(f"[{idx}/{len(music_files)}] Processing: {file_path.name}")
            
            # Check current metadata status
            status = self.check_metadata_status(file_path)
            
            # Parse filename
            parsed_info = self.parse_filename(file_path.stem)
            
            # Determine if we should fix this file
            should_fix = False
            
            if fix_only_missing:
                if status['needs_fix']:
                    should_fix = True
                    logger.info("Metadata is incomplete, will fix")
                else:
                    logger.info("Metadata is complete, skipping")
                    results['files_skipped'] += 1
            else:
                should_fix = True
                logger.info("Will fix metadata (force mode)")
            
            # Fix metadata if needed
            if should_fix:
                # Use file index as track number if not parsed from filename
                track_num = parsed_info.get('track_number', str(idx))
                
                if self.fix_metadata(file_path, parsed_info, track_num):
                    results['files_fixed'] += 1
                    
                    # Verify the fix
                    new_status = self.check_metadata_status(file_path)
                    if new_status['needs_fix']:
                        logger.warning("Metadata still incomplete after fix")
                        results['details'].append({
                            'file': file_path.name,
                            'action': 'fixed_but_incomplete',
                            'status': new_status
                        })
                    else:
                        logger.info("Metadata fixed and verified successfully")
                        results['details'].append({
                            'file': file_path.name,
                            'action': 'fixed',
                            'status': new_status
                        })
                else:
                    results['files_failed'] += 1
                    results['details'].append({
                        'file': file_path.name,
                        'action': 'failed',
                        'reason': 'Metadata fix failed'
                    })
            else:
                results['details'].append({
                    'file': file_path.name,
                    'action': 'skipped',
                    'status': status
                })
        
        # Summary
        logger.info("=" * 60)
        logger.info("Metadata Fix Summary")
        logger.info("=" * 60)
        logger.info(f"Album: {self.album_info.get('album_name', 'Unknown')}")
        logger.info(f"Artist: {self.album_info.get('album_artist', 'Unknown')}")
        logger.info(f"Total files scanned: {results['files_scanned']}")
        logger.info(f"Files fixed: {results['files_fixed']}")
        logger.info(f"Files skipped: {results['files_skipped']}")
        logger.info(f"Files failed: {results['files_failed']}")
        logger.info("=" * 60)
        
        return results


def fix_album_metadata(album_folder: str, fix_only_missing: bool = True) -> dict:
    """
    Convenience function to fix album metadata.

    Args:
        album_folder: Path to album folder
        fix_only_missing: If True, only fix files with missing metadata

    Returns:
        Dictionary with fix results
    """
    fixer = AlbumMetadataFixer(album_folder)
    return fixer.scan_and_fix(fix_only_missing)


def scan_multiple_albums(album_folders: list[str], fix_only_missing: bool = True) -> list[dict]:
    """
    Scan and fix multiple album folders.

    Args:
        album_folders: List of album folder paths
        fix_only_missing: If True, only fix files with missing metadata

    Returns:
        List of results for each album
    """
    results = []
    
    for folder in album_folders:
        if os.path.isdir(folder):
            logger.info(f"\nProcessing album: {folder}")
            result = fix_album_metadata(folder, fix_only_missing)
            results.append(result)
        else:
            logger.warning(f"Skipping non-directory: {folder}")
    
    return results


if __name__ == "__main__":
    # Example usage
    
    # Example 1: Fix single album folder
    fix_album_metadata(r"F:\Workspaces\JetBrains\PyCharm\python_uv_cloud_music\downloads\许茹芸 - 好歌茹芸 (2011-05-13)")
    
    # Example 2: Fix multiple album folders
    # download_dir = config.get_download_dir()
    # album_folders = [
    #     os.path.join(download_dir, folder) 
    #     for folder in os.listdir(download_dir) 
    #     if os.path.isdir(os.path.join(download_dir, folder))
    # ]
    # scan_multiple_albums(album_folders)
    
    # Example 3: Force fix all files (even if metadata exists)
    # fix_album_metadata(r"path\to\album", fix_only_missing=False)
    
    pass
