"""
Music Library Database Models Package (Basic)

Provides object-oriented interfaces for database tables.
"""

from src.model.basic.config import Config
from src.model.basic.music_info import MusicInfo
from src.model.basic.music_url import MusicURL

__all__ = ['MusicInfo', 'MusicURL', 'Config']
