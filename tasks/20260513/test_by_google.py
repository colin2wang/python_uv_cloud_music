import base64
import json
import os
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# Note here: replaced the original requests library
from curl_cffi import requests

from util_logging import setup_logger

logger = setup_logger(__name__)

HEADERS = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://wyapi.toubiec.cn',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}


def encrypt_payload(payload: dict, base64_key: str) -> str:
    payload['timestamp'] = int(time.time() * 1000)
    plain_text = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    key = base64.b64decode(base64_key)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(iv, plain_text, None)

    cipher_text = encrypted[:-16]
    auth_tag = encrypted[-16:]

    return f"{base64.b64encode(iv).decode('utf-8')}.{base64.b64encode(auth_tag).decode('utf-8')}.{base64.b64encode(cipher_text).decode('utf-8')}"


def decrypt_response(response_data: str, base64_key: str) -> dict:
    parts = response_data.split('.')
    iv = base64.b64decode(parts[0])
    auth_tag = base64.b64decode(parts[1])
    cipher_text = base64.b64decode(parts[2])
    key = base64.b64decode(base64_key)
    aesgcm = AESGCM(key)
    decrypted_bytes = aesgcm.decrypt(iv, cipher_text + auth_tag, None)
    return json.loads(decrypted_bytes.decode('utf-8'))


def get_music_url(song_id: str, level: str = "lossless"):

    logger.info("1. Fetching session key...")
    # impersonate="chrome120" is the key! It makes the website firewall think this is a real Chrome browser request
    key_res = requests.post("https://nextmusic.toubiec.cn/api/key", headers=HEADERS, impersonate="chrome120")
    key_res.raise_for_status()

    key_info = key_res.json().get('data', {})
    key_id = key_info.get('keyId')
    key_token = key_info.get('keyToken')
    aes_key = key_info.get('key')
    logger.info(f"   [Success] Got KeyId: {key_id}")

    logger.info(f"\n2. Requesting song playback URL (SongID: {song_id})...")
    url_payload = {
        "id": song_id,
        "level": level
    }

    request_body = {
        "keyId": key_id,
        "keyToken": key_token,
        "data": encrypt_payload(url_payload, aes_key)
    }

    logger.debug(json.dumps(request_body, indent=2))
    song_res = requests.post("https://nextmusic.toubiec.cn/api/getSongUrl", json=request_body, headers=HEADERS,
                             impersonate="chrome120")
    logger.debug(song_res.text)
    song_res.raise_for_status()
    response_json = song_res.json()

    if 'ciphertext' in response_json:
        logger.info("\n3. Server returned ciphertext, decrypting...")
        decrypted_data = decrypt_response(response_json['ciphertext'], aes_key)
        logger.info("\n==== Decryption Result ====")
        logger.info(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
        if 'data' in decrypted_data and 'url' in decrypted_data['data']:
            logger.info(f"\n🎵 Song direct URL obtained successfully: {decrypted_data['data']['url']}")
            return decrypted_data
    else:
        logger.info("\n==== Parsing Result (Unencrypted) ====")
        logger.info(json.dumps(response_json, indent=4, ensure_ascii=False))
        return response_json

    return None

if __name__ == "__main__":
    get_music_url("26427662", "standard")