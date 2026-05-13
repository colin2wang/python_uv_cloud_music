"""
NextMusic Tool - A class-based wrapper for NextMusic API with AES-GCM encryption
"""
import base64
import json
import time
import os

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from logging_config import setup_logger
from utils import random_sleep

# Create logger
logger = setup_logger(__name__)

MAX_RETRY = 3

class NextMusicTool:
    """NextMusic API tool for getting song URLs with AES-GCM encryption"""
    
    API_URL = "https://nextmusic.toubiec.cn/api/getSongUrl"
    KEY_API_URL = "https://nextmusic.toubiec.cn/api/key"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://wyapi.toubiec.cn",
        "Referer": "https://wyapi.toubiec.cn/",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "priority": "u=1, i",
    }

    def __init__(self):
        """Initialize NextMusicTool"""
        self.key_data = None
        self.key_expiry_time = 0

    def _get_encryption_key(self) -> dict:
        """
        Get encryption key from NextMusic API
        
        Returns:
            Dictionary containing keyId, keyToken, and key
        """
        try:
            response = requests.post(
                self.KEY_API_URL,
                headers=self.HEADERS,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != 200 or not result.get('data'):
                raise Exception(f"Failed to get encryption key: {result.get('message', 'Unknown error')}")
            
            return result['data']
        except Exception as e:
            logger.error(f"Error getting encryption key: {e}")
            raise

    def _array_buffer_to_base64(self, data: bytes) -> str:
        """
        Convert bytes to base64 string (equivalent to JS btoa)
        
        Args:
            data: Bytes to encode
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(data).decode('utf-8')

    def _base64_to_array_buffer(self, base64_str: str) -> bytes:
        """
        Convert base64 string to bytes (equivalent to JS atob)
        
        Args:
            base64_str: Base64 encoded string
            
        Returns:
            Decoded bytes
        """
        return base64.b64decode(base64_str)

    def _encrypt_data(self, data: dict, key_b64: str) -> str:
        """
        Encrypt data using AES-GCM (equivalent to hB function in JS)
        
        Args:
            data: Dictionary to encrypt
            key_b64: Base64 encoded encryption key
            
        Returns:
            Encrypted data in format: base64(IV).base64(tag).base64(ciphertext)
        """
        try:
            # Decode the key
            key = self._base64_to_array_buffer(key_b64)
            
            # Add timestamp to data (as in JS code)
            data_with_timestamp = {
                **data,
                "timestamp": int(time.time() * 1000)  # JavaScript Date.now() returns milliseconds
            }
            
            # Convert data to JSON string
            json_str = json.dumps(data_with_timestamp, separators=(',', ':'))
            plaintext = json_str.encode('utf-8')
            
            logger.debug(f"Encrypting: {json_str}")
            logger.debug(f"Key length: {len(key)} bytes")
            
            # Generate random 12-byte IV (initialization vector)
            iv = os.urandom(12)
            
            # Encrypt using AES-GCM
            aesgcm = AESGCM(key)
            # AES-GCM returns ciphertext + tag (16 bytes) concatenated
            ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
            
            logger.debug(f"Ciphertext+tag length: {len(ciphertext_with_tag)}")
            
            # Split ciphertext and tag (last 16 bytes are the tag)
            ciphertext = ciphertext_with_tag[:-16]
            tag = ciphertext_with_tag[-16:]
            
            logger.debug(f"Ciphertext length: {len(ciphertext)}, Tag length: {len(tag)}")
            
            # Format: base64(IV).base64(tag).base64(ciphertext)
            encrypted = f"{self._array_buffer_to_base64(iv)}.{self._array_buffer_to_base64(tag)}.{self._array_buffer_to_base64(ciphertext)}"
            
            logger.debug(f"Encrypted format: {encrypted[:50]}...")
            
            return encrypted
        except Exception as e:
            logger.error(f"Error encrypting data: {e}", exc_info=True)
            raise

    def _decrypt_data(self, encrypted_str: str, key_b64: str) -> dict:
        """
        Decrypt data using AES-GCM (equivalent to gB function in JS)
        
        Args:
            encrypted_str: Encrypted data in format: base64(IV).base64(tag).base64(ciphertext)
            key_b64: Base64 encoded encryption key
            
        Returns:
            Decrypted dictionary
        """
        try:
            logger.debug(f"Decrypting data: {encrypted_str[:50]}...")
            
            # Decode the key
            key = self._base64_to_array_buffer(key_b64)
            logger.debug(f"Key length: {len(key)} bytes")
            
            # Split the encrypted string
            parts = encrypted_str.split('.')
            if len(parts) != 3:
                raise ValueError(f"Invalid encrypted data format: expected 3 parts, got {len(parts)}")
            
            iv_b64, tag_b64, ciphertext_b64 = parts
            logger.debug(f"Parts - IV: {len(iv_b64)}, Tag: {len(tag_b64)}, Ciphertext: {len(ciphertext_b64)}")
            
            # Decode each part
            iv = self._base64_to_array_buffer(iv_b64)
            tag = self._base64_to_array_buffer(tag_b64)
            ciphertext = self._base64_to_array_buffer(ciphertext_b64)
            
            logger.debug(f"Decoded - IV: {len(iv)}, Tag: {len(tag)}, Ciphertext: {len(ciphertext)}")
            
            # Combine tag + ciphertext (as in JS code)
            ciphertext_with_tag = tag + ciphertext
            logger.debug(f"Combined ciphertext+tag length: {len(ciphertext_with_tag)}")
            
            # Decrypt using AES-GCM
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)
            
            # Parse JSON
            result = json.loads(plaintext.decode('utf-8'))
            logger.debug(f"Decryption successful")
            return result
        except Exception as e:
            logger.error(f"Error decrypting data: {e}", exc_info=True)
            return None

    def get_song_url(self, song_id: str | int, level: str = "lossless") -> dict:
        """
        Get song URL from NextMusic API with AES-GCM encryption
        
        Args:
            song_id: Song ID
            level: Audio quality level (default: lossless)
        
        Returns:
            API response as dictionary
        """
        retry = 0
        while retry <= MAX_RETRY:
            try:
                # Step 1: Get encryption key
                random_sleep(1.0, reason="Before getting encryption key")
                key_data = self._get_encryption_key()
                key_id = key_data['keyId']
                key_token = key_data['keyToken']
                key = key_data['key']
                
                # Step 2: Encrypt request data
                request_data = {
                    "id": str(song_id),
                    "level": level
                }
                encrypted_data = self._encrypt_data(request_data, key)
                
                # Step 3: Make API request
                random_sleep(2.0, reason="Before NextMusic API request")
                api_request_body = {
                    "keyId": key_id,
                    "keyToken": key_token,
                    "data": encrypted_data
                }
                
                response = requests.post(
                    self.API_URL,
                    json=api_request_body,
                    headers=self.HEADERS,
                    timeout=30
                )
                response.raise_for_status()
                
                response_json = response.json()
                logger.debug(f"Response JSON keys: {response_json.keys()}")
                logger.debug(f"Has ciphertext: {'ciphertext' in response_json}")
                if 'ciphertext' in response_json:
                    logger.debug(f"Ciphertext preview: {response_json['ciphertext'][:100]}...")
                
                # Step 4: Decrypt response if it's encrypted
                if response_json.get('ciphertext'):
                    decrypted_data = self._decrypt_data(response_json['ciphertext'], key)
                    if decrypted_data:
                        logger.info(f"Finish get song URL for ID: {decrypted_data.get('data', {}).get('id', song_id)}")
                        return decrypted_data
                    else:
                        raise Exception("Response decryption failed")
                else:
                    # Response is not encrypted
                    logger.info(f"Finish get song URL for ID: {response_json.get('data', {}).get('id', song_id)}")
                    return response_json
                    
            except requests.exceptions.RequestException as e:
                if retry >= MAX_RETRY:
                    logger.error(f"Max retry reached, giving up: {e}")
                    break
                retry += 1
                logger.error(f"Error making request to NextMusic API: {e}, retry {retry}/{MAX_RETRY}")
            except Exception as e:
                if retry >= MAX_RETRY:
                    logger.error(f"Max retry reached, giving up: {e}")
                    break
                retry += 1
                logger.error(f"Error processing NextMusic API request: {e}, retry {retry}/{MAX_RETRY}")
        
        return {"code": 500, "message": "Failed to get song URL after retries", "data": None}


if __name__ == "__main__":
    # Initialize the tool
    tool = NextMusicTool()
    
    # Get song URL
    song_id = 238847
    result = tool.get_song_url(song_id)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("code") == 200:
        print("Download URL:", result["data"]["url"])