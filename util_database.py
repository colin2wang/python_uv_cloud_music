"""
SQLite Database Manager for Music Library

Provides database operations for music_info table and in-memory URL caching.
Supports query by id/quality and upsert operations.
"""
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict

from util_logging import setup_logger

logger = setup_logger(__name__)


class MusicDB:
    """
    Simple SQLite database manager for music information with in-memory URL caching.
    
    Tables:
        - music_info: Stores music metadata (music_id, artist, title, album, lyrics)
        - config: Stores configuration key-value pairs (name, value)
    
    In-memory cache:
        - _url_cache: Dictionary mapping (music_id, quality) to URL
    """
    
    def __init__(self, db_path: str | Path = None):
        """
        Initialize database connection and in-memory URL cache.
        
        Args:
            db_path: Path to SQLite database file. Defaults to 'music_library.db'
        """
        self.db_path = Path(db_path) if db_path else Path.cwd() / 'cloud-music.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize tables only if database file doesn't exist
        if not self.db_path.exists():
            self._initialize_tables()
        
        # In-memory URL cache: {(music_id, quality): url}
        self._url_cache = {}
        self._url_cache_lock = threading.Lock()
        logger.info(f"Database initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_tables(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS music_info (
                    music_id INTEGER NOT NULL PRIMARY KEY,
                    artists TEXT,
                    title TEXT,
                    album_name TEXT,
                    cover_url TEXT,
                    lyrics TEXT,
                    duration INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    name TEXT NOT NULL PRIMARY KEY,
                    value TEXT
                )
            """)
        logger.debug("Tables initialized")
    
    # ==================== Upsert Operations ====================
    
    def upsert_music_info(self, music_id: int, artists: str = None, 
                         title: str = None, album_name: str = None,
                         cover_url: str = None, lyrics: str = None,
                         duration: int = None) -> bool:
        """
        Insert or update music information.
        
        Args:
            music_id: Unique music identifier
            artists: Artist name(s)
            title: Song title
            album_name: Album name
            cover_url: Cover image URL
            lyrics: Song lyrics
            duration: Song duration in milliseconds
            
        Returns:
            True if successful
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO music_info (music_id, artists, title, album_name, cover_url, lyrics, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(music_id) DO UPDATE SET
                    artists = COALESCE(excluded.artists, artists),
                    title = COALESCE(excluded.title, title),
                    album_name = COALESCE(excluded.album_name, album_name),
                    cover_url = COALESCE(excluded.cover_url, cover_url),
                    lyrics = COALESCE(excluded.lyrics, lyrics),
                    duration = COALESCE(excluded.duration, duration)
            """, (music_id, artists, title, album_name, cover_url, lyrics, duration))
        
        logger.info(f"Upserted music_info: id={music_id}")
        return True
    
    def upsert_music_url(self, music_id: int, quality: str, url: str) -> bool:
        """
        Insert or update music URL for specific quality using in-memory cache.
        
        Args:
            music_id: Unique music identifier
            quality: Quality level (e.g., 'standard', 'lossless', 'hires')
            url: Download URL
            
        Returns:
            True if successful
        """
        with self._url_cache_lock:
            self._url_cache[(music_id, quality)] = url
        
        logger.info(f"Upserted music_url to cache: id={music_id}, quality={quality}")
        return True
    
    def upsert_batch_urls(self, music_id: int, urls: Dict[str, str]) -> int:
        """
        Batch upsert multiple URLs for different qualities.
        
        Args:
            music_id: Unique music identifier
            urls: Dictionary mapping quality to URL
            
        Returns:
            Number of URLs inserted/updated
        """
        count = 0
        with self._get_connection() as conn:
            for quality, url in urls.items():
                conn.execute("""
                    INSERT INTO music_url (music_id, quality, url)
                    VALUES (?, ?, ?)
                    ON CONFLICT(music_id, quality) DO UPDATE SET
                        url = excluded.url
                """, (music_id, quality, url))
                count += 1
        
        logger.info(f"Batch upserted {count} URLs for music_id={music_id}")
        return count
    
    # ==================== Query Operations ====================
    
    def get_music_info(self, music_id: int) -> Optional[Dict]:
        """
        Query music information by ID.
        
        Args:
            music_id: Unique music identifier
            
        Returns:
            Dictionary with music info or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM music_info WHERE music_id = ?", 
                (music_id,)
            )
            row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_music_url(self, music_id: int, quality: str) -> Optional[str]:
        """
        Query music URL by ID and quality from in-memory cache.
        
        Args:
            music_id: Unique music identifier
            quality: Quality level
            
        Returns:
            URL string or None if not found
        """
        with self._url_cache_lock:
            return self._url_cache.get((music_id, quality))
    
    def get_all_music_urls(self, music_id: int) -> Dict[str, str]:
        """
        Query all URLs for a music ID.
        
        Args:
            music_id: Unique music identifier
            
        Returns:
            Dictionary mapping quality to URL
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT quality, url FROM music_url WHERE music_id = ?",
                (music_id,)
            )
            rows = cursor.fetchall()
        
        return {row['quality']: row['url'] for row in rows}
    
    def get_music_with_urls(self, music_id: int) -> Optional[Dict]:
        """
        Query music info with all associated URLs.
        
        Args:
            music_id: Unique music identifier
            
        Returns:
            Dictionary with music info and 'urls' field, or None
        """
        info = self.get_music_info(music_id)
        if info:
            info['urls'] = self.get_all_music_urls(music_id)
        return info
    
    # ==================== Config Operations ====================
    
    def upsert_config(self, name: str, value: str) -> bool:
        """
        Insert or update configuration value.
        
        Args:
            name: Configuration key name
            value: Configuration value
            
        Returns:
            True if successful
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO config (name, value)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    value = excluded.value
            """, (name, value))
        
        logger.info(f"Upserted config: {name}")
        return True
    
    def get_config(self, name: str, default: str = None) -> Optional[str]:
        """
        Query configuration value by name.
        
        Args:
            name: Configuration key name
            default: Default value if not found
            
        Returns:
            Configuration value or default if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
        
        if row:
            return row['value']
        return default
    
    def delete_config(self, name: str) -> bool:
        """
        Delete configuration entry.
        
        Args:
            name: Configuration key name
            
        Returns:
            True if deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM config WHERE name = ?",
                (name,)
            )
            deleted = cursor.rowcount > 0
        
        if deleted:
            logger.info(f"Deleted config: {name}")
        return deleted
    
    def get_all_configs(self) -> Dict[str, str]:
        """
        Get all configuration entries.
        
        Returns:
            Dictionary mapping config names to values
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT name, value FROM config")
            rows = cursor.fetchall()
        
        return {row['name']: row['value'] for row in rows}
    
    # ==================== Utility Operations ====================
    
    def delete_music(self, music_id: int) -> bool:
        """
        Delete music info and all associated URLs.
        
        Args:
            music_id: Unique music identifier
            
        Returns:
            True if deleted
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM music_url WHERE music_id = ?", (music_id,))
            cursor = conn.execute("DELETE FROM music_info WHERE music_id = ?", (music_id,))
            deleted = cursor.rowcount > 0
        
        if deleted:
            logger.info(f"Deleted music: id={music_id}")
        return deleted
    
    def exists(self, music_id: int) -> bool:
        """
        Check if music exists in database.
        
        Args:
            music_id: Unique music identifier
            
        Returns:
            True if exists
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM music_info WHERE music_id = ?",
                (music_id,)
            )
            return cursor.fetchone()[0] > 0
    
    def count(self) -> int:
        """
        Get total number of music records.
        
        Returns:
            Count of records
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM music_info")
            return cursor.fetchone()[0]


def main():
    """Demonstrate database operations."""
    db = MusicDB()
    
    print("\n=== Upsert Music Info ===")
    db.upsert_music_info(
        music_id=12345678,
        artist="Artist Name",
        title="Song Title",
        album="Album Name",
        cover_url="http://example.com/cover.jpg",
        lyrics="[00:00.00] Lyrics here...",
        duration=240000
    )
    
    print("\n=== Upsert URLs ===")
    db.upsert_music_url(12345678, "standard", "http://example.com/standard.mp3")
    db.upsert_music_url(12345678, "lossless", "http://example.com/lossless.flac")
    
    # Batch upsert
    db.upsert_batch_urls(12345678, {
        "hires": "http://example.com/hires.flac",
        "jymaster": "http://example.com/master.flac"
    })
    
    print("\n=== Query by ID ===")
    info = db.get_music_info(12345678)
    if info:
        print(f"Title: {info['title']}")
        print(f"Artist: {info['artist']}")
        print(f"Album: {info['album']}")
    
    print("\n=== Query by ID + Quality ===")
    url = db.get_music_url(12345678, "lossless")
    print(f"Lossless URL: {url}")
    
    print("\n=== Get All URLs ===")
    all_urls = db.get_all_music_urls(12345678)
    for quality, url in all_urls.items():
        print(f"{quality}: {url}")
    
    print("\n=== Get Music with URLs ===")
    full_info = db.get_music_with_urls(12345678)
    if full_info:
        print(f"Music: {full_info['title']}")
        print(f"URLs: {list(full_info['urls'].keys())}")
    
    print("\n=== Config Operations ===")
    # Upsert config
    db.upsert_config("download_dir", "./downloads")
    db.upsert_config("default_quality", "lossless")
    db.upsert_config("max_retries", "3")
    
    # Query config
    download_dir = db.get_config("download_dir")
    print(f"Download dir: {download_dir}")
    
    quality = db.get_config("default_quality", "standard")
    print(f"Default quality: {quality}")
    
    # Query non-existent config with default
    timeout = db.get_config("timeout", "30")
    print(f"Timeout (with default): {timeout}")
    
    # Get all configs
    all_configs = db.get_all_configs()
    print(f"All configs: {all_configs}")
    
    # Delete config
    db.delete_config("max_retries")
    print(f"After delete - max_retries: {db.get_config('max_retries', 'N/A')}")
    
    print("\n=== Check Exists ===")
    print(f"Exists: {db.exists(12345678)}")
    print(f"Total count: {db.count()}")


if __name__ == "__main__":
    main()