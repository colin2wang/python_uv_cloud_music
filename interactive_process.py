"""
Interactive download script for cloud music.
Provides a user-friendly interface to select download method and input parameters.
"""

import sys

from logging_config import setup_logger
from process_cloud_music import download_song, download_album, download_playlist

# Create logger
logger = setup_logger(__name__)


def parse_indexes(input_str: str) -> list:
    """
    Parse index string to list of integers.
    
    Args:
        input_str: String containing indexes separated by spaces or commas
        
    Returns:
        List of integers
    """
    if not input_str or not input_str.strip():
        return []
    
    # Replace commas with spaces, then split
    normalized = input_str.replace(',', ' ').replace('，', ' ')
    parts = normalized.split()
    
    indexes = []
    for part in parts:
        try:
            idx = int(part.strip())
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


def select_download_method() -> int:
    """
    Display menu and let user select download method.
    
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
        choice = input("Enter your choice (0-3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return int(choice)
        else:
            print("Invalid choice. Please enter 0, 1, 2, or 3.")


def main():
    """Main interactive download function."""
    print("\nWelcome to Cloud Music Interactive Download Tool!")
    
    while True:
        # Step 1: Select download method
        method = select_download_method()
        
        if method == 0:
            print("\nThank you for using Cloud Music Download Tool. Goodbye!")
            break
        
        # Step 2: Get ID based on selected method
        if method == 1:
            resource_id = get_user_input("Enter Song ID (e.g., 2163629816)")
            quality = get_user_input("Enter quality level", "lossless")
            
            print(f"\nStarting download...")
            print(f"Song ID: {resource_id}")
            print(f"Quality: {quality}")
            print("-" * 60)
            
            try:
                download_song(resource_id, quality)
                print("\n✓ Download completed successfully!")
            except Exception as e:
                logger.error(f"Download failed: {str(e)}")
                print(f"\n✗ Download failed: {str(e)}")
        
        elif method == 2:
            resource_id = get_user_input("Enter Album ID (e.g., 172259)")
            quality = get_user_input("Enter quality level", "lossless")
            
            # Ask if user wants to specify indexes
            want_indexes = input("\nDo you want to download specific tracks only? (yes/no) [no]: ").strip().lower()
            
            indexes = []
            if want_indexes in ['yes', 'y']:
                print("\nEnter track numbers to download (separated by spaces or commas)")
                print("Example: 1 3 5  or  1,3,5  or  1 3,5")
                
                while True:
                    index_input = get_user_input("Enter track numbers")
                    indexes = parse_indexes(index_input)
                    
                    if confirm_indexes(indexes):
                        break
                    else:
                        print("Please re-enter the track numbers.")
            else:
                print("Downloading all tracks in the album.")
            
            print(f"\nStarting download...")
            print(f"Album ID: {resource_id}")
            print(f"Quality: {quality}")
            if indexes:
                print(f"Selected tracks: {indexes}")
            else:
                print("All tracks will be downloaded")
            print("-" * 60)
            
            try:
                download_album(resource_id, indexes, quality)
                print("\n✓ Album download completed successfully!")
            except Exception as e:
                logger.error(f"Download failed: {str(e)}")
                print(f"\n✗ Download failed: {str(e)}")
        
        elif method == 3:
            resource_id = get_user_input("Enter Playlist ID (e.g., 5453912201)")
            quality = get_user_input("Enter quality level", "lossless")
            
            # Ask if user wants to specify indexes
            want_indexes = input("\nDo you want to download specific tracks only? (yes/no) [no]: ").strip().lower()
            
            indexes = []
            if want_indexes in ['yes', 'y']:
                print("\nEnter track numbers to download (separated by spaces or commas)")
                print("Example: 1 3 5  or  1,3,5  or  1 3,5")
                
                while True:
                    index_input = get_user_input("Enter track numbers")
                    indexes = parse_indexes(index_input)
                    
                    if confirm_indexes(indexes):
                        break
                    else:
                        print("Please re-enter the track numbers.")
            else:
                print("Downloading all tracks in the playlist.")
            
            print(f"\nStarting download...")
            print(f"Playlist ID: {resource_id}")
            print(f"Quality: {quality}")
            if indexes:
                print(f"Selected tracks: {indexes}")
            else:
                print("All tracks will be downloaded")
            print("-" * 60)
            
            try:
                download_playlist(resource_id, indexes, quality)
                print("\n✓ Playlist download completed successfully!")
            except Exception as e:
                logger.error(f"Download failed: {str(e)}")
                print(f"\n✗ Download failed: {str(e)}")
        
        # Ask if user wants to continue
        print("\n" + "=" * 60)
        again = input("Do you want to download more? (yes/no) [no]: ").strip().lower()
        if again not in ['yes', 'y']:
            print("\nThank you for using Cloud Music Download Tool. Goodbye!")
            break


if __name__ == "__main__":
    main()
