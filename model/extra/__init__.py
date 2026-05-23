"""
Extra models package for additional data not covered by core models.
"""

from model.extra.song_metadata import SongMetadata
from model.extra.album_metadata import AlbumMetadata
from model.extra.playlist_metadata import PlaylistMetadata

__all__ = ['SongMetadata', 'AlbumMetadata', 'PlaylistMetadata']
