"""
Extra models package for additional data not covered by core models.
"""

from src.model.extra.song_metadata import SongMetadata
from src.model.extra.album_metadata import AlbumMetadata
from src.model.extra.playlist_metadata import PlaylistMetadata

__all__ = ['SongMetadata', 'AlbumMetadata', 'PlaylistMetadata']
