"""
Music Library Database Models Package (Basic)

Provides object-oriented interfaces for database tables.
"""

from model.basic.config import Config
from model.basic.music_info import MusicInfo
from model.basic.music_url import MusicURL

__all__ = ['MusicInfo', 'MusicURL', 'Config']
