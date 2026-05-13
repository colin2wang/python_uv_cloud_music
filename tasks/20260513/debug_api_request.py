"""
Debug script to capture complete request/response details for NextMusic API
"""
import json
import time
import base64
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def array_buffer_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')

def base64_to_array_buffer(base64_str: str) -> bytes:
    return base64.b64decode(base64_str)

def encrypt_data(data: dict, key_b64: str) -> str:
    key = base64_to_array_buffer(key_b64)
    
    data_with_timestamp = {
        **data,
        "timestamp": int(time.time() * 1000)
    }
    
    json_str = json.dumps(data_with_timestamp, separators=(',', ':'))
    plaintext = json_str.encode('utf-8')
    
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
    
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    
    encrypted = f"{array_buffer_to_base64(iv)}.{array_buffer_to_base64(tag)}.{array_buffer_to_base64(ciphertext)}"
    
    return encrypted

def main():
    print("=" * 80)
    print("NextMusic API Debug - Complete Request/Response Capture")
    print("=" * 80)
    
    # Step 1: Get encryption key
    print("\n[Step 1] Getting encryption key...")
    key_response = requests.post(
        'https://nextmusic.toubiec.cn/api/key',
        headers={
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-length': '0',
            'origin': 'https://wyapi.toubiec.cn',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        },
        timeout=10
    )
    
    print(f"Status: {key_response.status_code}")
    key_data = key_response.json()
    print(f"Response: {json.dumps(key_data, indent=2, ensure_ascii=False)}")
    
    if key_data.get('code') != 200 or not key_data.get('data'):
        print("ERROR: Failed to get encryption key")
        return
    
    key_id = key_data['data']['keyId']
    key_token = key_data['data']['keyToken']
    key = key_data['data']['key']
    
    print(f"\nKey ID: {key_id}")
    print(f"Key Token: {key_token}")
    print(f"Key (base64): {key}")
    print(f"Key length: {len(base64.b64decode(key))} bytes")
    
    # Step 2: Prepare and encrypt request data
    print("\n[Step 2] Preparing request data...")
    request_data = {
        "id": "238847",
        "level": "lossless"
    }
    
    print(f"Original data: {json.dumps(request_data, separators=(',', ':'))}")
    
    encrypted_data = encrypt_data(request_data, key)
    print(f"Encrypted data: {encrypted_data}")
    print(f"Encrypted length: {len(encrypted_data)} chars")
    
    # Step 3: Make API request
    print("\n[Step 3] Making API request...")
    api_request_body = {
        "keyId": key_id,
        "keyToken": key_token,
        "data": encrypted_data
    }
    
    print(f"Request body:")
    print(json.dumps(api_request_body, indent=2, ensure_ascii=False))
    
    headers = {
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
    
    response = requests.post(
        'https://nextmusic.toubiec.cn/api/getSongUrl',
        json=api_request_body,
        headers=headers,
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers:")
    for header_key, header_value in response.headers.items():
        print(f"  {header_key}: {header_value}")
    
    print(f"\nResponse Body:")
    print(response.text)
    
    # Step 4: Try to decrypt if response has ciphertext
    response_json = response.json()
    if response_json.get('ciphertext'):
        print("\n[Step 4] Attempting to decrypt response...")
        
        ciphertext_response = response_json['ciphertext']
        parts = ciphertext_response.split('.')
        
        if len(parts) != 3:
            print(f"ERROR: Invalid ciphertext format, expected 3 parts, got {len(parts)}")
            return
        
        iv_r = base64_to_array_buffer(parts[0])
        tag_r = base64_to_array_buffer(parts[1])
        ct_r = base64_to_array_buffer(parts[2])
        
        print(f"IV length: {len(iv_r)} bytes")
        print(f"Tag length: {len(tag_r)} bytes")
        print(f"Ciphertext length: {len(ct_r)} bytes")
        
        combined = tag_r + ct_r
        
        try:
            key_bytes = base64_to_array_buffer(key)
            print(f"Using key for decryption: {key[:30]}...")
            print(f"Key bytes length: {len(key_bytes)}")
            
            aesgcm = AESGCM(key_bytes)
            decrypted = aesgcm.decrypt(iv_r, combined, None)
            
            decrypted_json = json.loads(decrypted.decode('utf-8'))
            print(f"\nDecrypted response:")
            print(json.dumps(decrypted_json, indent=2, ensure_ascii=False))
            
        except Exception as e:
            import traceback
            print(f"ERROR: Decryption failed - {e}")
            traceback.print_exc()
            print(f"This suggests the key used for encryption is different from the one we have.")
    
    print("\n" + "=" * 80)
    print("Debug complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
