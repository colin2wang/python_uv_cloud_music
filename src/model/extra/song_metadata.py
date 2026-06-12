"""
SongMetadata model for additional song metadata needed for file operations.
"""
from typing import Optional, Dict


class SongMetadata:
    """
    Additional song metadata model for file operations.
    
    This model contains extra fields needed for downloading and tagging files,
    but not stored in the core MusicInfo/MusicURL models.
    
    Attributes:
        size: File size information
        pic: Cover image URL
        duration: Song duration in seconds
        cover_path: Local path to cover image file
        track_number: Track number in album
        used_quality: Actually used quality level
    """
    
    def __init__(self, size: str = None, pic: str = None, duration: int = None,
                 cover_path: str = None, track_number: str = None, 
                 used_quality: str = None):
        """
        Initialize SongMetadata instance.
        
        Args:
            size: File size information
            pic: Cover image URL
            duration: Song duration in seconds
            cover_path: Local path to cover image file
            track_number: Track number in album
            used_quality: Actually used quality level
        """
        self.size = size
        self.pic = pic
        self.duration = duration
        self.cover_path = cover_path
        self.track_number = track_number
        self.used_quality = used_quality
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for file operations."""
        return {
            'size': self.size,
            'pic': self.pic,
            'duration': self.duration,
            'cover_path': self.cover_path,
            'track_number': self.track_number,
            'used_quality': self.used_quality
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SongMetadata':
        """Create instance from dictionary."""
        return cls(
            size=data.get('size'),
            pic=data.get('pic'),
            duration=data.get('duration'),
            cover_path=data.get('cover_path'),
            track_number=data.get('track_number'),
            used_quality=data.get('used_quality')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"SongMetadata(size={self.size}, quality={self.used_quality})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SongMetadata(size='{self.size}', pic='{self.pic}', duration={self.duration})"
