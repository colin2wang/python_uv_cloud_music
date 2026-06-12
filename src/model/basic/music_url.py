"""
MusicURL model for music_url table.
"""
from typing import Optional, Dict


class MusicURL:
    """
    Music URL model corresponding to music_url table.
    
    Attributes:
        music_id: Music identifier (foreign key)
        quality: Quality level (e.g., 'standard', 'lossless', 'hires')
        url: Download URL
    """
    
    def __init__(self, music_id: int, quality: str, url: str = None):
        """
        Initialize MusicURL instance.
        
        Args:
            music_id: Music identifier
            quality: Quality level
            url: Download URL
        """
        self.music_id = music_id
        self.quality = quality
        self.url = url
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database operations."""
        return {
            'music_id': self.music_id,
            'quality': self.quality,
            'url': self.url
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MusicURL':
        """Create instance from dictionary."""
        return cls(
            music_id=data['music_id'],
            quality=data['quality'],
            url=data.get('url')
        )
    
    @classmethod
    def from_db_row(cls, row: Dict) -> 'MusicURL':
        """Create instance from database row."""
        return cls(
            music_id=row['music_id'],
            quality=row['quality'],
            url=row.get('url')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.quality}: {self.url}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"MusicURL(music_id={self.music_id}, quality='{self.quality}')"
