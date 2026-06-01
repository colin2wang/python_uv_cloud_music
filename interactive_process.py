"""
Interactive download script for cloud music.
Provides a user-friendly interface to select download method and input parameters.
"""

import json
import sys

from util_database import MusicDB
from util_music_downloader import download_song, download_album, download_playlist
from util_logging import setup_logger

# Create logger
logger = setup_logger(__name__)

# Database instance
db = MusicDB()


def load_last_config() -> dict:
    """
    Load last used configuration from database.
    
    Returns:
        Dictionary containing last configuration values
    """
    try:
        config_json = db.get_config('last_download_config')
        if config_json:
            config = json.loads(config_json)
            logger.info("Loaded last configuration from database")
            return config
    except Exception as e:
        logger.warning(f"Failed to load last config from database: {e}")
    
    # Return default config if not found or error occurred
    return {
        'method': 1,
        'quality': 'lossless'
    }


def save_last_config(config: dict):
    """
    Save current configuration to database.
    
    Args:
        config: Dictionary containing configuration values to save
    """
    try:
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        db.upsert_config('last_download_config', config_json)
        logger.info("Saved configuration to database")
    except Exception as e:
        logger.warning(f"Failed to save last config to database: {e}")


def parse_indexes(input_str: str) -> list:
    """
    Parse index string to list of integers.
    Supports various formats including ranges (e.g., "1 2 3-6 9-11").
    
    Args:
        input_str: String containing indexes separated by spaces or commas,
                   can include ranges with hyphen (e.g., "1-5")
        
    Returns:
        List of integers
    """
    if not input_str or not input_str.strip():
        return []
    
    # Replace commas and Chinese commas with spaces, then split
    normalized = input_str.replace(',', ' ').replace('，', ' ')
    parts = normalized.split()
    
    indexes = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check if the part is a range (contains hyphen)
        if '-' in part and not part.startswith('-'):
            try:
                range_parts = part.split('-')
                if len(range_parts) == 2:
                    start_idx = int(range_parts[0].strip())
                    end_idx = int(range_parts[1].strip())
                    
                    # Validate range
                    if start_idx <= 0 or end_idx <= 0:
                        logger.warning(f"Skipping invalid range: {part} (must be positive)")
                        continue
                    
                    if start_idx > end_idx:
                        logger.warning(f"Skipping invalid range: {part} (start > end)")
                        continue
                    
                    # Add all numbers in the range
                    for idx in range(start_idx, end_idx + 1):
                        indexes.append(idx)
                else:
                    logger.warning(f"Skipping malformed range: {part}")
            except ValueError:
                logger.warning(f"Skipping invalid range: {part}")
        else:
            # Single number
            try:
                idx = int(part)
                if idx > 0:
                    indexes.append(idx)
                else:
                    logger.warning(f"Skipping invalid index: {idx} (must be positive)")
            except ValueError:
                logger.warning(f"Skipping invalid index: {part}")
    
    return sorted(set(indexes))  # Remove duplicates and sort


def get_user_input(prompt: str, default: str = "") -> str:
    """
    Get user input with optional default value.
    
    Args:
        prompt: Prompt message to display
        default: Default value if user presses Enter
        
    Returns:
        User input string or default value
    """
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    try:
        user_input = input(full_prompt).strip()
        return user_input if user_input else default
    except (EOFError, KeyboardInterrupt):
        print("\n\nOperation cancelled by user.")
        sys.exit(0)


def confirm_indexes(indexes: list) -> bool:
    """
    Ask user to confirm the parsed indexes.
    
    Args:
        indexes: List of parsed indexes
        
    Returns:
        True if user confirms, False otherwise
    """
    if not indexes:
        print("No indexes specified.")
        return True
    
    print(f"\nParsed indexes: {indexes}")
    print(f"Total count: {len(indexes)}")
    
    while True:
        confirm = input("Are these indexes correct? (yes/no) [yes]: ").strip().lower()
        if confirm in ['', 'yes', 'y']:
            return True
        elif confirm in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def select_download_method(default_method: int = 1) -> int:
    """
    Display menu and let user select download method.
    
    Args:
        default_method: Default method to suggest (1, 2, or 3)
    
    Returns:
        Selected method number (1, 2, or 3)
    """
    print("\n" + "=" * 60)
    print("Cloud Music Download Tool")
    print("=" * 60)
    print("\nPlease select download method:")
    print("1. Download single song by Song ID")
    print("2. Download album by Album ID")
    print("3. Download playlist by Playlist ID")
    print("0. Exit")
    print("-" * 60)
    
    while True:
        choice = input(f"Enter your choice (0-3) [{default_method}]: ").strip()
        if choice == '':
            logger.info(f"User selected download method: {default_method} (default)")
            return default_method
        elif choice in ['0', '1', '2', '3']:
            method_num = int(choice)
            method_names = {0: 'Exit', 1: 'Single Song', 2: 'Album', 3: 'Playlist'}
            logger.info(f"User selected download method: {method_num} ({method_names[method_num]})")
            return method_num
        else:
            print("Invalid choice. Please enter 0, 1, 2, or 3.")


def get_resource_id_and_quality(config_key: str, default_id: str = "", prompt_text: str = "") -> tuple:
    """
    Get resource ID and quality from user input.
    
    Args:
        config_key: Key to look up last used value in config
        default_id: Default ID value if available
        prompt_text: Custom prompt text for resource ID
        
    Returns:
        Tuple of (resource_id, quality)
    """
    last_config = load_last_config()
    resource_id = get_user_input(prompt_text or f"Enter {config_key.replace('_', ' ').title()} (e.g., 12345)", 
                                  last_config.get(config_key, default_id))
    quality = get_user_input("Enter quality level", last_config.get('quality', 'lossless'))
    return resource_id, quality


def should_download_specific_tracks() -> bool:
    """
    Ask user if they want to download specific tracks only.
    
    Returns:
        True if user wants specific tracks, False otherwise
    """
    answer = input("\nDo you want to download specific tracks only? (yes/no) [no]: ").strip().lower()
    return answer in ['yes', 'y']


def get_track_indexes_from_user(last_indexes: list = None) -> list:
    """
    Get track indexes from user input.
    
    Args:
        last_indexes: Previously used indexes to show as default
        
    Returns:
        List of parsed and validated track indexes
    """
    print("\nEnter track numbers to download")
    print("Supported formats:")
    print("  - Single: 1 2 3")
    print("  - Comma-separated: 1,2,3")
    print("  - Ranges: 3-6 (includes 3, 4, 5, 6)")
    print("  - Mixed: 1 2 3-6 9-11")
    
    last_indexes_str = ' '.join(map(str, last_indexes)) if last_indexes else ''
    if last_indexes:
        print(f"Last used indexes: {last_indexes}")
    
    while True:
        index_input = get_user_input("Enter track numbers", last_indexes_str)
        indexes = parse_indexes(index_input)
        
        logger.info(f"User entered track indexes: '{index_input}' -> Parsed: {indexes}")
        
        if confirm_indexes(indexes):
            return indexes
        else:
            print("Please re-enter the track numbers.")


def download_single_song(last_config: dict) -> bool:
    """
    Handle single song download flow.
    
    Args:
        last_config: Last saved configuration dictionary
        
    Returns:
        True if download succeeded, False otherwise
    """
    resource_id, quality = get_resource_id_and_quality('song_id', '', "Enter Song ID (e.g., 2163629816)")
    
    logger.info(f"User input - Method: Single Song, Song ID: {resource_id}, Quality: {quality}")
    
    print(f"\nStarting download...")
    print(f"Song ID: {resource_id}")
    print(f"Quality: {quality}")
    print("-" * 60)
    
    try:
        download_song(resource_id, quality)
        print("\n✓ Download completed successfully!")
        
        # Save configuration for next use
        save_last_config({
            'method': 1,
            'song_id': resource_id,
            'quality': quality
        })
        return True
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        print(f"\n✗ Download failed: {str(e)}")
        return False


def download_album_or_playlist(method: int, last_config: dict) -> bool:
    """
    Handle album or playlist download flow (shared logic).
    
    Args:
        method: Download method (2 for album, 3 for playlist)
        last_config: Last saved configuration dictionary
        
    Returns:
        True if download succeeded, False otherwise
    """
    config_key = 'album_id' if method == 2 else 'playlist_id'
    resource_type = "Album" if method == 2 else "Playlist"
    
    resource_id, quality = get_resource_id_and_quality(config_key, '', 
                                                        f"Enter {resource_type} ID (e.g., 172259)")
    
    # Ask if user wants to specify indexes
    want_indexes = should_download_specific_tracks()
    
    logger.info(f"User input - Method: {resource_type}, {resource_type} ID: {resource_id}, "
                f"Quality: {quality}, Want specific tracks: {want_indexes}")
    
    indexes = []
    if want_indexes:
        last_indexes = last_config.get('indexes', [])
        indexes = get_track_indexes_from_user(last_indexes)
    else:
        print(f"Downloading all tracks in the {resource_type}.")
        logger.info(f"User chose to download all tracks in {resource_type.lower()}")
    
    print(f"\nStarting download...")
    print(f"{resource_type} ID: {resource_id}")
    print(f"Quality: {quality}")
    if indexes:
        print(f"Selected tracks: {indexes}")
    else:
        print("All tracks will be downloaded")
    print("-" * 60)
    
    try:
        # Call appropriate download function based on method
        if method == 2:
            download_album(resource_id, indexes, quality)
        else:
            download_playlist(resource_id, indexes, quality)
        
        print(f"\n✓ {resource_type} download completed successfully!")
        
        # Save configuration for next use
        save_last_config({
            'method': method,
            config_key: resource_id,
            'quality': quality,
            'indexes': indexes
        })
        return True
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        print(f"\n✗ Download failed: {str(e)}")
        return False


def run_download_session():
    """
    Main interactive download loop.
    
    Runs the complete download flow in a loop until user chooses to exit.
    """
    print("\nWelcome to Cloud Music Interactive Download Tool!")
    
    while True:
        # Load last configuration at the start of each iteration
        last_config = load_last_config()
        
        # Step 1: Select download method
        method = select_download_method(last_config.get('method', 1))
        
        if method == 0:
            print("\nThank you for using Cloud Music Download Tool. Goodbye!")
            break
        
        # Step 2: Execute download based on selected method
        success = False
        if method == 1:
            success = download_single_song(last_config)
        elif method == 2:
            success = download_album_or_playlist(2, last_config)
        elif method == 3:
            success = download_album_or_playlist(3, last_config)
        
        # Ask if user wants to continue (only if previous download succeeded or user wants to retry)
        print("\n" + "=" * 60)
        again = input("Do you want to download more? (yes/no) [yes]: ").strip().lower()
        logger.info(f"User chose to continue: {again if again else 'yes (default)'}")
        if again in ['no', 'n']:
            print("\nThank you for using Cloud Music Download Tool. Goodbye!")
            break


def main():
    """Main entry point for interactive download tool."""
    run_download_session()


if __name__ == "__main__":
    main()
