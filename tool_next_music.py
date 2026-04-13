"""
NextMusic Tool - A class-based wrapper for NextMusic API
"""
import hashlib
import json
import time

import requests

from logging_config import setup_logger
from utils import random_sleep

# Create logger
logger = setup_logger(__name__)

MAX_RETRY = 3

class NextMusicTool:
    """NextMusic API tool for getting song URLs"""
    
    API_URL = "https://nextmusic.toubiec.cn/api/getSongUrl"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Origin": "https://wyapi.toubiec.cn",
        "Referer": "https://wyapi.toubiec.cn/",
    }

    @staticmethod
    def next_token():
        # 1. Generate c: identical to JS (current timestamp rounded down to minutes)
        c = int(time.time() // 60)  # Equivalent to JS: Math.floor(Date.now() / 6e4)

        # 2. Concatenate string
        raw_str = f"suxiaoqings:{c}"

        # 3. MD5 encryption (32-bit lowercase hexadecimal)
        d = hashlib.md5(raw_str.encode('utf-8')).hexdigest()

        return d

    def get_song_url(self, song_id: str | int, level: str = "lossless") -> dict:
        """
        Get song URL from NextMusic API
        
        Args:
            song_id: Song ID
            level: Audio quality level (default: lossless)
        
        Returns:
            API response as dictionary
        """
        data = {
            "id": str(song_id),
            "level": level,
            "token": self.next_token()
        }

        retry = 0
        while True:
            try:
                random_sleep(3.0, reason="Before NextMusic API request")
                response = requests.post(self.API_URL, json=data, headers=self.HEADERS)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if retry >= MAX_RETRY:
                    logger.error(f"Max retry reached, giving up: {e}")
                    break
                logger.error(f"Error making request to NextMusic API: {e}, retry in {++retry}")


if __name__ == "__main__":
    # Initialize the tool
    tool = NextMusicTool()
    
    # Get song URL
    song_id = 74674741
    result = tool.get_song_url(song_id)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("code") == 200:
        print("Download URL:", result["data"]["url"])