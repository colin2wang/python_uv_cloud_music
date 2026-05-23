"""
AlbumMetadata model for album-related data needed for folder creation.
"""
from typing import Optional, Dict, List


class AlbumMetadata:
    """
    Album metadata model for album folder creation and management.
    
    This model contains album information needed for creating album folders
    and description files.
    
    Attributes:
        album_id: Album identifier
        album_name: Album name
        album_artist: Album artist
        album_publish_time: Publish timestamp
        song_count: Number of songs in album
        song_details: List of song details with id, name, artists, index
        raw_data: Raw API response data (for description and cover URL)
    """
    
    def __init__(self, album_id: str = None, album_name: str = None,
                 album_artist: str = None, album_publish_time: int = None,
                 song_count: int = 0, song_details: List[Dict] = None,
                 raw_data: Dict = None):
        """
        Initialize AlbumMetadata instance.
        
        Args:
            album_id: Album identifier
            album_name: Album name
            album_artist: Album artist
            album_publish_time: Publish timestamp
            song_count: Number of songs in album
            song_details: List of song details
            raw_data: Raw API response data
        """
        self.album_id = album_id
        self.album_name = album_name
        self.album_artist = album_artist
        self.album_publish_time = album_publish_time
        self.song_count = song_count
        self.song_details = song_details or []
        self.raw_data = raw_data or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for file operations."""
        return {
            'album_id': self.album_id,
            'album_name': self.album_name,
            'album_artist': self.album_artist,
            'album_publish_time': self.album_publish_time,
            'song_count': self.song_count,
            'song_details': self.song_details,
            'raw_data': self.raw_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AlbumMetadata':
        """Create instance from dictionary."""
        return cls(
            album_id=data.get('album_id'),
            album_name=data.get('album_name'),
            album_artist=data.get('album_artist'),
            album_publish_time=data.get('album_publish_time'),
            song_count=data.get('song_count', 0),
            song_details=data.get('song_details', []),
            raw_data=data.get('raw_data', {})
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.album_artist} - {self.album_name}" if self.album_artist and self.album_name else f"Album ID: {self.album_id}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"AlbumMetadata(album_id='{self.album_id}', name='{self.album_name}', artist='{self.album_artist}')"
