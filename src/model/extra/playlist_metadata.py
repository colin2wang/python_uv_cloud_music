"""
PlaylistMetadata model for playlist-related data.
"""
from typing import Optional, Dict, List


class PlaylistMetadata:
    """
    Playlist metadata model for playlist management.
    
    This model contains playlist information including song lists.
    
    Attributes:
        playlist_id: Playlist identifier
        playlist_name: Playlist name
        playlist_creator: Playlist creator
        song_count: Number of songs in playlist
        song_ids: List of song IDs
        song_details: List of song details with id, name, artists, index
    """
    
    def __init__(self, playlist_id: str = None, playlist_name: str = None,
                 playlist_creator: str = None, song_count: int = 0,
                 song_ids: List[str] = None, song_details: List[Dict] = None):
        """
        Initialize PlaylistMetadata instance.
        
        Args:
            playlist_id: Playlist identifier
            playlist_name: Playlist name
            playlist_creator: Playlist creator
            song_count: Number of songs in playlist
            song_ids: List of song IDs
            song_details: List of song details
        """
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.playlist_creator = playlist_creator
        self.song_count = song_count
        self.song_ids = song_ids or []
        self.song_details = song_details or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'playlist_id': self.playlist_id,
            'playlist_name': self.playlist_name,
            'playlist_creator': self.playlist_creator,
            'song_count': self.song_count,
            'song_ids': self.song_ids,
            'song_details': self.song_details
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlaylistMetadata':
        """Create instance from dictionary."""
        return cls(
            playlist_id=data.get('playlist_id'),
            playlist_name=data.get('playlist_name'),
            playlist_creator=data.get('playlist_creator'),
            song_count=data.get('song_count', 0),
            song_ids=data.get('song_ids', []),
            song_details=data.get('song_details', [])
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.playlist_name} by {self.playlist_creator}" if self.playlist_name else f"Playlist ID: {self.playlist_id}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"PlaylistMetadata(playlist_id='{self.playlist_id}', name='{self.playlist_name}')"
