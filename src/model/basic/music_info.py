"""
MusicInfo model for music_info table.
"""
from typing import Optional, Dict


class MusicInfo:
    """
    Music information model corresponding to music_info table.
    
    Attributes:
        music_id: Unique music identifier (primary key)
        artist: Artist name
        title: Song title
        album: Album name
        cover_url: Cover image URL
        lyrics: Song lyrics text
        duration: Song duration in milliseconds
    """
    
    def __init__(self, music_id: int, artist: str = None, title: str = None, 
                 album: str = None, cover_url: str = None, lyrics: str = None,
                 duration: int = None):
        """
        Initialize MusicInfo instance.
        
        Args:
            music_id: Unique music identifier
            artist: Artist name
            title: Song title
            album: Album name
            cover_url: Cover image URL
            lyrics: Song lyrics text
            duration: Song duration in milliseconds
        """
        self.music_id = music_id
        self.artist = artist
        self.title = title
        self.album = album
        self.cover_url = cover_url
        self.lyrics = lyrics
        self.duration = duration
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database operations."""
        return {
            'music_id': self.music_id,
            'artist': self.artist,
            'title': self.title,
            'album': self.album,
            'cover_url': self.cover_url,
            'lyrics': self.lyrics,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MusicInfo':
        """Create instance from dictionary."""
        return cls(
            music_id=data['music_id'],
            artist=data.get('artist'),
            title=data.get('title'),
            album=data.get('album'),
            cover_url=data.get('cover_url'),
            lyrics=data.get('lyrics'),
            duration=data.get('duration')
        )
    
    @classmethod
    def from_db_row(cls, row: Dict) -> 'MusicInfo':
        """Create instance from database row."""
        return cls(
            music_id=row['music_id'],
            artist=row.get('artists'),  # Database uses 'artists' (plural)
            title=row.get('title'),
            album=row.get('album_name'),  # Database uses 'album_name'
            cover_url=row.get('cover_url'),
            lyrics=row.get('lyrics'),
            duration=row.get('duration')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.artist} - {self.title}" if self.artist and self.title else f"Music ID: {self.music_id}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"MusicInfo(music_id={self.music_id}, artist='{self.artist}', title='{self.title}')"
