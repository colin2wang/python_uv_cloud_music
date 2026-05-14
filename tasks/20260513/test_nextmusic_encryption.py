"""
Test script to understand NextMusic encryption algorithm
"""
import requests
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def get_key():
    """Get encryption key from API"""
    response = requests.post(
        'https://nextmusic.toubiec.cn/api/key',
        headers={
            'Content-Type': 'application/json',
            'Origin': 'https://wyapi.toubiec.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    return response.json()

def encrypt_data(data: dict, key_b64: str) -> str:
    """
    Encrypt data using AES
    
    Args:
        data: Dictionary to encrypt
        key_b64: Base64 encoded key
    
    Returns:
        Encrypted data as base64 string
    """
    # Decode the key
    key = base64.b64decode(key_b64)
    
    # Add timestamp to data (as shown in JS code line 142)
    import time
    data_with_timestamp = {
        **data,
        "timestamp": int(time.time() * 1000)  # JavaScript uses Date.now() which returns milliseconds
    }
    
    # Convert data to JSON string
    json_str = json.dumps(data_with_timestamp, separators=(',', ':'))
    print(f"Original JSON with timestamp: {json_str}")
    
    # Try different encryption modes
    # Mode 1: AES-ECB
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        padded_data = pad(json_str.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        print(f"Encrypted with ECB: {encrypted_b64}")
        return encrypted_b64
    except Exception as e:
        print(f"ECB failed: {e}")
    
    # Mode 2: AES-CBC with zero IV
    try:
        iv = b'\x00' * 16  # Zero IV
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(json_str.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        print(f"Encrypted with CBC (zero IV): {encrypted_b64}")
        return encrypted_b64
    except Exception as e:
        print(f"CBC failed: {e}")

def decrypt_data(ciphertext_b64: str, key_b64: str) -> dict:
    """
    Decrypt data using AES
    
    Args:
        ciphertext_b64: Base64 encoded ciphertext
        key_b64: Base64 encoded key
    
    Returns:
        Decrypted dictionary
    """
    # Decode the key and ciphertext
    key = base64.b64decode(key_b64)
    ciphertext = base64.b64decode(ciphertext_b64)
    
    # Decrypt using AES-ECB
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)
    
    # Parse JSON
    return json.loads(decrypted.decode('utf-8'))

if __name__ == "__main__":
    # Step 1: Get key
    print("=" * 60)
    print("Step 1: Getting encryption key...")
    print("=" * 60)
    key_response = get_key()
    print(json.dumps(key_response, indent=2, ensure_ascii=False))
    
    key_id = key_response['data']['keyId']
    key_token = key_response['data']['keyToken']
    key = key_response['data']['key']
    
    # Step 2: Encrypt test data
    print("\n" + "=" * 60)
    print("Step 2: Encrypting test data...")
    print("=" * 60)
    test_data = {
        "id": "2718994102",
        "level": "lossless"
    }
    
    encrypted = encrypt_data(test_data, key)
    print(f"Encrypted data: {encrypted}")
    
    # Step 3: Make API request
    print("\n" + "=" * 60)
    print("Step 3: Making API request...")
    print("=" * 60)
    api_url = "https://nextmusic.toubiec.cn/api/getSongUrl"
    request_body = {
        "keyId": key_id,
        "keyToken": key_token,
        "data": encrypted
    }
    
    print(f"Request body: {json.dumps(request_body, indent=2)}")
    
    response = requests.post(
        api_url,
        json=request_body,
        headers={
            'Content-Type': 'application/json',
            'Origin': 'https://wyapi.toubiec.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    print(f"\nResponse status: {response.status_code}")
    response_json = response.json()
    print(f"Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
    
    # Step 4: Decrypt response if needed
    if response_json.get('ciphertext'):
        print("\n" + "=" * 60)
        print("Step 4: Decrypting response...")
        print("=" * 60)
        decrypted = decrypt_data(response_json['ciphertext'], key)
        print(f"Decrypted response: {json.dumps(decrypted, indent=2, ensure_ascii=False)}")
