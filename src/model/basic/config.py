"""
Config model for config table.
"""
from typing import Optional, Dict


class Config:
    """
    Configuration model corresponding to config table.
    
    Attributes:
        name: Configuration key name (primary key)
        value: Configuration value
    """
    
    def __init__(self, name: str, value: str = None):
        """
        Initialize Config instance.
        
        Args:
            name: Configuration key name
            value: Configuration value
        """
        self.name = name
        self.value = value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database operations."""
        return {
            'name': self.name,
            'value': self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Config':
        """Create instance from dictionary."""
        return cls(
            name=data['name'],
            value=data.get('value')
        )
    
    @classmethod
    def from_db_row(cls, row: Dict) -> 'Config':
        """Create instance from database row."""
        return cls(
            name=row['name'],
            value=row.get('value')
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}={self.value}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Config(name='{self.name}', value='{self.value}')"
