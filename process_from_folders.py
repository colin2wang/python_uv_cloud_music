"""
Folder List Utility

Functionality:
- List all subdirectories in a specified directory

Usage:
    from list_folders import list_folders, iterate_folders, process_folders
    
    # List all folders
    folders = list_folders("J:\\Music")
    
    # Iterate and process one by one
    for folder in iterate_folders("J:\\Music"):
        process_album(folder)
    
    # Batch processing
    def my_process_func(folder_path):
        return do_something(folder_path)
    
    results = process_folders("J:\\Music", my_process_func)
"""

from pathlib import Path
from typing import List, Optional

from logging_config import setup_logger
from process_album_cover_redownload import redownload_album_cover
from process_album_lyrics_fix import fix_album_lyrics

# Create logger
logger = setup_logger(__name__)


def list_folders(directory: str) -> List[str]:
    """
    List all folders in a directory

    Args:
        directory: Directory path

    Returns:
        List of folder absolute paths (sorted)

    Example:
        # List all folders
        folders = list_folders("J:\\Music")
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    # Get all subdirectories (non-recursive)
    folders = []
    for item in dir_path.iterdir():
        if item.is_dir():
            # Skip hidden folders (starting with .)
            if not item.name.startswith('.'):
                folders.append(item)

    # Sort by name (default: Unicode encoding order)
    folders.sort(key=lambda x: x.name.lower())

    # Return list of absolute paths
    return [str(folder.resolve()) for folder in folders]


def iterate_folders(directory: str):
    """
    Iterator: Yield folder paths one by one for easy processing in loops

    Args:
        directory: Directory path

    Yields:
        Folder absolute path

    Example:
        from list_folders import iterate_folders
        for folder in iterate_folders("J:\\Music"):
            process_album(folder)
    """
    folders = list_folders(directory)
    for folder in folders:
        yield folder


def process_folders(directory: str, process_func, show_progress: bool = True,
                   stop_on_error: bool = False):
    """
    Batch process folders

    Args:
        directory: Directory path
        process_func: Processing function, receives folder absolute path as parameter
        show_progress: Whether to show progress information
        stop_on_error: Stop when encountering error (False means skip and continue)

    Returns:
        List of processing results, each element contains folder, success, result, error

    Example:
        from list_folders import process_folders
        from process_album_lyrics_fix import fix_album_lyrics

        results = process_folders(
            "J:\\Music",
            fix_album_lyrics,
            show_progress=True
        )

        for r in results:
            logger.info(f"{r['folder']}: {'Success' if r['success'] else 'Failed'}")
    """
    from datetime import datetime

    folders = list_folders(directory)
    results = []
    total = len(folders)
    start_time = datetime.now()

    if show_progress:
        logger.info("=" * 60)
        logger.info(f"Starting to process {total} folders")
        logger.info("=" * 60)
    
    for idx, folder in enumerate(folders, 1):
        result = {
            'folder': folder,
            'success': False,
            'result': None,
            'error': None,
            'index': idx
        }
        
        if show_progress:
            folder_name = Path(folder).name
            logger.info(f"[{idx}/{total}] Processing: {folder_name}")
            logger.info(f"Path: {folder}")
        
        try:
            # Call the processing function
            process_result = process_func(folder)
            result['success'] = True
            result['result'] = process_result
            
            if show_progress:
                logger.info("✓ Processing successful")
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
            if show_progress:
                logger.error(f"✗ Processing failed: {e}")
            
            if stop_on_error:
                logger.warning("\nEncountered error, stopping processing")
                break
        
        results.append(result)
        
        if show_progress:
            # Show current progress
            elapsed = (datetime.now() - start_time).total_seconds()
            if idx > 1:
                avg_time = elapsed / idx
                remaining = avg_time * (total - idx)
                logger.info(f"Progress: {idx}/{total} | Elapsed: {elapsed:.1f}s | Estimated remaining: {remaining:.1f}s")
    
    if show_progress:
        # Show summary
        success_count = sum(1 for r in results if r['success'])
        failed_count = total - success_count
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("Processing completed")
        logger.info(f"Total: {total} folders")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Duration: {elapsed:.1f}s")
        logger.info("=" * 60)
    
    return results


def print_folders(folders: List[str], show_index: bool = False):
    """
    Print folder list
    
    Args:
        folders: Folder path list
        show_index: Whether to show index numbers
    """
    if not folders:
        logger.info("No folders found")
        return
    
    logger.info(f"Found {len(folders)} folders:")
    logger.info("-" * 60)
    
    for i, folder in enumerate(folders):
        if show_index:
            logger.info(f"{i+1:3d}. {folder}")
        else:
            logger.info(folder)
    
    logger.info("-" * 60)
    logger.info(f"Total: {len(folders)} folders")


def main():
    # Configuration: Set directory
    target_directory = r"F:\我的音乐\我的专辑\华语流行"

    # Output options
    show_index = True  # Whether to show index numbers
    quiet_mode = True  # Quiet mode, only output paths (one per line)

    try:
        # List folders
        folders = list_folders(target_directory)

        if quiet_mode:
            # Quiet mode: Only output paths, one per line
            for folder in folders:
                logger.info(folder)

                # Fix album lyrics issues.
                # fix_album_lyrics(folder)

                # Redownload album cover.
                redownload_album_cover(folder)
        else:
            # Normal mode: Show formatted output
            logger.info("Sort order: Default (Unicode)")
            logger.info("")
            print_folders(folders, show_index=show_index)

    
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except NotADirectoryError as e:
        logger.error(f"Error: {e}")
    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unknown error: {e}")


if __name__ == "__main__":
    main()
