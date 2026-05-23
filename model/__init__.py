"""
Music Library Models Package

Provides both basic and extra models for the music library.
"""

from model.basic import MusicInfo, MusicURL, Config
from model.extra import SongMetadata, AlbumMetadata, PlaylistMetadata

__all__ = [
    'MusicInfo', 'MusicURL', 'Config',
    'SongMetadata', 'AlbumMetadata', 'PlaylistMetadata'
]
