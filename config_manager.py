"""
Configuration Manager for Music Library Organizer

This module handles loading and accessing configuration settings from config.yml
"""

import os
from pathlib import Path
from typing import Any

import yaml

from logging_config import setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """
    Configuration Manager Singleton
    
    Provides centralized access to application configuration
    loaded from config.yml file.
    """
    
    _instance = None
    _config = None
    _config_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: str | None = None) -> dict:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file (default: config.yml in project root)

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Try to find config.yml in the project root
            possible_paths = [
                Path.cwd() / 'config.yml',
                Path(__file__).parent / 'config.yml',
            ]

            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break

            if config_path is None:
                logger.warning("config.yml not found, using default configuration")
                self._config = self._get_default_config()
                self._config_path = None
                return self._config

        try:
            config_path_obj = Path(config_path)
            logger.info(f"Loading configuration from: {config_path_obj}")

            with open(config_path_obj, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)

            self._config_path = str(config_path_obj)
            logger.info("Configuration loaded successfully")

            # Merge with default config to ensure all keys exist
            default_config = self._get_default_config()
            self._config = self._merge_configs(default_config, self._config)

            return self._config

        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self._config = self._get_default_config()
            return self._config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}, using defaults")
            self._config = self._get_default_config()
            return self._config
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}, using defaults")
            self._config = self._get_default_config()
            return self._config
    
    def _get_default_config(self) -> dict:
        """
        Get default configuration values
        
        Returns:
            Dictionary with default configuration
        """
        return {
            'api': {
                'base_url': 'https://musicapi.lxchen.cn'
            },
            'download': {
                'default_dir': 'downloads',
                'default_quality': 'lossless',
                'add_index_to_filename': True,
                'index_format': '03d'
            },
            'filename': {
                'pattern': '{index} - {artist} - {title}',
                'illegal_char_replacement': '_'
            },
            'metadata': {
                'write_metadata': True,
                'write_cover': True,
                'write_lyrics': True,
                'max_lyric_length': 1000
            },
            'network': {
                'timeout': 30,
                'random_delay_max': 2.5,
                'api_delay_min': 1.0
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'console_output': True,
                'file_output': True,
                'log_file': 'logs/app.log'
            }
        }
    
    def _merge_configs(self, default: dict, override: dict) -> dict:
        """
        Merge two configuration dictionaries recursively
        
        Args:
            default: Default configuration
            override: Override configuration
            
        Returns:
            Merged configuration dictionary
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key path.

        Args:
            key_path: Dot-separated path (e.g., 'download.default_dir')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if self._config is None:
            return default

        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
    
    def get_api_base_url(self) -> str:
        """Get API base URL"""
        return self.get('api.base_url', 'https://musicapi.lxchen.cn')
    
    def get_download_dir(self) -> str:
        """Get default download directory"""
        return self.get('download.default_dir', 'downloads')
    
    def get_default_quality(self) -> str:
        """Get default audio quality level"""
        return self.get('download.default_quality', 'lossless')
    
    def should_add_index(self) -> bool:
        """Check if index should be added to filename"""
        return self.get('download.add_index_to_filename', True)
    
    def get_index_format(self) -> str:
        """Get index format string"""
        return self.get('download.index_format', '03d')
    
    def get_filename_pattern(self) -> str:
        """Get filename pattern"""
        return self.get('filename.pattern', '{index} - {artist} - {title}')
    
    def get_illegal_char_replacement(self) -> str:
        """Get replacement character for illegal filename characters"""
        return self.get('filename.illegal_char_replacement', '_')

    def get_artist_delimiter_replacement(self) -> str:
        """Get replacement character for artist delimiters"""
        return self.get('filename.artist_delimiter_replacement', ', ')
    
    def should_write_metadata(self) -> bool:
        """Check if metadata should be written to files"""
        return self.get('metadata.write_metadata', True)
    
    def should_write_cover(self) -> bool:
        """Check if cover images should be written"""
        return self.get('metadata.write_cover', True)
    
    def should_write_lyrics(self) -> bool:
        """Check if lyrics should be written"""
        return self.get('metadata.write_lyrics', True)
    
    def get_max_lyric_length(self) -> int:
        """Get maximum lyric length"""
        return self.get('metadata.max_lyric_length', 1000)
    
    def get_timeout(self) -> int:
        """Get network timeout in seconds"""
        return self.get('network.timeout', 30)
    
    def get_random_delay_max(self) -> float:
        """Get maximum random delay for requests"""
        return self.get('network.random_delay_max', 2.5)
    
    def get_api_delay_min(self) -> float:
        """Get minimum delay between API calls"""
        return self.get('network.api_delay_min', 1.0)
    
    def reload(self) -> dict:
        """
        Reload configuration from file
        
        Returns:
            Reloaded configuration dictionary
        """
        return self.load_config(self._config_path)


# Create singleton instance
config = ConfigManager()
