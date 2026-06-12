"""
Main entry point for cloud music download tool
"""
from src.util.util_music_downloader import download_song, download_album, download_playlist
from src.util.util_logging import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point"""
    # Example usage:
    download_song("3383993462")
    
    indexes = []
    # indexes = [4, 6, 15, 18, 19]
    indexes = list(range(11, 13))
    
    # download_album("1505850", indexes)
    # download_playlist("5453912201", indexes)


if __name__ == "__main__":
    main()