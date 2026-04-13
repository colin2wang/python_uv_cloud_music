import os
import time
from pathlib import Path
from typing import Optional

import imagesize
import requests

from logging_config import setup_logger
from process_cloud_music import get_song_ids_by_album_id
from utils import random_sleep

# Create logger
logger = setup_logger(__name__)


class AlbumCoverRedownloader:
    """
    Album Cover Redownloader

    Scans album folders and re-downloads album cover images
    by fetching from the music source API
    """
    
    def __init__(self, album_folder: str):
        """
        Initialize the cover redownloader

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
    
    def fetch_album_cover_url(self) -> Optional[str]:
        """
        Fetch album cover URL from the API using album ID

        Returns:
            str: Album cover URL or None
        """
        album_id = self.album_info.get('album_id')
        
        if not album_id:
            logger.error("Album ID not found in album_info.txt")
            return None
        
        try:
            logger.info("=" * 60)
            logger.info(f"Fetching album cover from album ID: {album_id}")
            logger.info("=" * 60)
            
            # Get album metadata
            album_metadata = get_song_ids_by_album_id(album_id)
            
            if not album_metadata.get('success'):
                logger.error(f"Failed to fetch album metadata: {album_metadata.get('message', 'Unknown error')}")
                return None
            
            # Extract cover URL from raw data
            raw_data = album_metadata.get('raw_data', {})
            album_cover_url = ''
            
            try:
                album_cover_url = raw_data.get('data', {}).get('album', {}).get('coverImgUrl', '')
                album_cover_url = album_cover_url.split('?')[0]
                logger.info(f"Album cover URL fetched: {album_cover_url}")
            except (AttributeError, KeyError):
                logger.warning(f"Could not extract album cover URL from response")
                return None
            
            return album_cover_url
            
        except Exception as e:
            logger.error(f"Error fetching album cover URL: {str(e)}")
            return None
    
    def download_cover_image(self, cover_url: str, cover_file_path: Path) -> bool:
        """
        Download cover image from URL
        
        Args:
            cover_url: URL of the cover image
            cover_file_path: Path to save the cover image
        
        Returns:
            bool: Whether download was successful
        """
        try:
            logger.info("Downloading album cover...")
            random_sleep(reason="Before downloading album cover")
            
            cover_response = requests.get(cover_url, timeout=10)
            cover_response.raise_for_status()
            
            with open(cover_file_path, 'wb') as f:
                f.write(cover_response.content)
            
            logger.info(f"Album cover downloaded: {cover_file_path.name}")
            return True
            
        except Exception as e:
            logger.warning(f"Album cover download failed: {str(e)}")
            return False
    
    def check_existing_cover(self) -> Optional[Path]:
        """
        Check if cover.jpg already exists in album folder
            
        Returns:
            Path to existing cover file or None
        """
        cover_file_path = self.album_folder / 'cover.jpg'
            
        if cover_file_path.exists():
            logger.info(f"Existing cover found：{cover_file_path.name}")
            return cover_file_path
            
        logger.info("No existing cover.jpg found in album folder")
        return None
        
    def check_cover_resolution(self, cover_path: Path) -> tuple[bool, int, int]:
        """
        Check if cover image resolution meets the requirement (>=400x400)
            
        Args:
            cover_path: Path to the cover image
                
        Returns:
            tuple[bool, int, int]: (meets_requirement, width, height)
        """
        if not cover_path.exists():
            return False, 0, 0
            
        try:
            width, height = imagesize.get(str(cover_path))
            
            if width is None or height is None:
                logger.warning("Failed to read image dimensions")
                return False, 0, 0
            
            meets_requirement = width >= 400 and height >= 400
                
            logger.info(f"Cover resolution: {width}x{height}, "
                       f"{'meets' if meets_requirement else 'does not meet'} requirement (>=400x400)")
                
            return meets_requirement, width, height
        except Exception as e:
            logger.warning(f"Failed to check cover resolution: {str(e)}")
            return False, 0, 0
    
    def backup_existing_cover(self) -> Optional[Path]:
        """
        Backup existing cover.jpg to .delete subfolder if it exists
        
        Returns:
            Path to backed up file or None
        """
        existing_cover = self.check_existing_cover()
        
        if not existing_cover:
            return None
        
        # Create .delete folder
        delete_folder = self.album_folder / '.delete'
        delete_folder.mkdir(exist_ok=True)
        logger.info(f"Created/verified .delete folder: {delete_folder}")
        
        try:
            # Move existing cover to .delete folder
            backup_path = delete_folder / f'cover_backup_{int(time.time())}.jpg'
            existing_cover.rename(backup_path)
            logger.info(f"Backed up existing cover: {existing_cover.name} -> .delete/{backup_path.name}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup existing cover: {str(e)}")
            return None
    
    def redownload_cover(self, force: bool = False) -> dict:
        """
        Re-download album cover
        
        Args:
            force: If True, overwrite existing cover without backup
        
        Returns:
            Dictionary with redownload results
        """
        logger.info("=" * 60)
        logger.info(f"Starting cover redownload for album: {self.album_folder}")
        logger.info("=" * 60)
        
        results = {
            'success': False,
            'album_folder': str(self.album_folder),
            'album_name': '',
            'album_id': '',
            'action': '',
            'cover_path': '',
            'message': ''
        }
        
        # Step 1: Load album info
        if not self.load_album_info():
            results['message'] = 'Failed to load album info'
            return results
        
        results['album_name'] = self.album_info.get('album_name', 'Unknown')
        results['album_id'] = self.album_info.get('album_id', '')
        
        # Step 2: Check existing cover resolution
        existing_cover = self.check_existing_cover()
        
        if existing_cover:
            meets_requirement, width, height = self.check_cover_resolution(existing_cover)
            
            if meets_requirement:
                logger.info("-" * 60)
                logger.info("Existing cover resolution meets requirement, skipping download")
                logger.info("-" * 60)
                results['success'] = True
                results['cover_path'] = str(existing_cover)
                results['action'] = 'already_satisfactory'
                results['message'] = 'Existing cover resolution is sufficient'
                
                logger.info("=" * 60)
                logger.info("Cover Check Summary")
                logger.info("=" * 60)
                logger.info(f"Album: {self.album_info.get('album_name', 'Unknown')}")
                logger.info(f"Artist: {self.album_info.get('album_artist', 'Unknown')}")
                logger.info(f"Resolution: {width}x{height}")
                logger.info(f"Action: {results['action']}")
                logger.info(f"Cover path: {existing_cover}")
                logger.info("=" * 60)
                return results
            else:
                logger.info("-" * 60)
                logger.info(f"Existing cover resolution ({width}x{height}) does not meet requirement, will replace...")
                logger.info("-" * 60)
                # Directly overwrite without backup
                try:
                    existing_cover.unlink()
                    logger.info(f"Deleted existing cover: {existing_cover.name}")
                    results['action'] = 'replaced_low_resolution'
                except Exception as e:
                    logger.error(f"Failed to delete existing cover: {str(e)}")
                    results['message'] = f'Failed to delete existing cover: {str(e)}'
                    return results
        else:
            results['action'] = 'downloaded_new'
        
        # Step 3: Fetch cover URL
        logger.info("-" * 60)
        cover_url = self.fetch_album_cover_url()
        
        if not cover_url:
            results['message'] = 'Failed to fetch cover URL'
            return results
        
        # Step 4: Download cover
        logger.info("-" * 60)
        cover_file_path = self.album_folder / 'cover.jpg'
        
        if self.download_cover_image(cover_url, cover_file_path):
            results['success'] = True
            results['cover_path'] = str(cover_file_path)
            results['message'] = 'Cover downloaded successfully'
            
            logger.info("=" * 60)
            logger.info("Cover Redownload Summary")
            logger.info("=" * 60)
            logger.info(f"Album: {self.album_info.get('album_name', 'Unknown')}")
            logger.info(f"Artist: {self.album_info.get('album_artist', 'Unknown')}")
            logger.info(f"Action: {results['action']}")
            logger.info(f"Cover saved: {cover_file_path}")
            logger.info("=" * 60)
        else:
            results['message'] = 'Failed to download cover'
            logger.error("Cover download failed")
        
        return results


def redownload_album_cover(album_folder: str, force: bool = False) -> dict:
    """
    Convenience function to redownload album cover.

    Args:
        album_folder: Path to album folder
        force: If True, overwrite existing cover without backup

    Returns:
        Dictionary with redownload results
    """
    redownloader = AlbumCoverRedownloader(album_folder)
    return redownloader.redownload_cover(force=force)


def redownload_multiple_album_covers(album_folders: list[str], force: bool = False) -> list[dict]:
    """
    Re-download covers for multiple album folders.

    Args:
        album_folders: List of album folder paths
        force: If True, overwrite existing covers without backup

    Returns:
        List of results for each album
    """
    results = []

    for folder in album_folders:
        if os.path.isdir(folder):
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing album: {folder}")
            logger.info(f"{'='*80}\n")
            result = redownload_album_cover(folder, force=force)
            results.append(result)
        else:
            logger.warning(f"Skipping non-directory: {folder}")

    return results


if __name__ == "__main__":
    # Example usage

    # Example 1: Re-download single album cover
    # Provide your album folder path here
    album_folder_path = r"F:\Workspaces\JetBrains\PyCharm\python_uv_cloud_music\downloads\许茹芸 - 好歌茹芸 (2011-05-13)"
    redownload_album_cover(album_folder_path)

    # Example 2: Re-download multiple album covers
    # download_dir = config.get_download_dir()
    # album_folders = [
    #     os.path.join(download_dir, folder)
    #     for folder in os.listdir(download_dir)
    #     if os.path.isdir(os.path.join(download_dir, folder))
    # ]
    # redownload_multiple_album_covers(album_folders)

    # Example 3: Force overwrite existing covers without backup
    # redownload_album_cover(album_folder_path, force=True)
