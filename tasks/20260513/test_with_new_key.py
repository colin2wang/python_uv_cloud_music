"""
Test complete encryption and decryption cycle with the new key from docs
"""
import json
import time
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def test_full_cycle():
    # Use the key from the updated documentation
    key_b64 = "K1y+dWroyYOKjb885yHoHZN0USTG/hwrztc57nzDd5o="
    key_id = "343d6fa3-7238-4a7e-9e00-78b47228144c"
    key_token = "f3377da5-e8f1-42b5-9803-5c83fba59406"
    
    print("=" * 60)
    print("Testing Complete Encryption/Decryption Cycle")
    print("=" * 60)
    print(f"Key ID: {key_id}")
    print(f"Key Token: {key_token}")
    print(f"Key (base64): {key_b64}")
    
    # Decode key
    key = base64.b64decode(key_b64)
    print(f"Key length: {len(key)} bytes\n")
    
    # Test data (as would be sent to API)
    test_data = {
        "id": "2718994102",
        "level": "lossless",
        "timestamp": int(time.time() * 1000)
    }
    
    print("Original data:")
    print(json.dumps(test_data, indent=2))
    
    # Encrypt
    json_str = json.dumps(test_data, separators=(',', ':'))
    plaintext = json_str.encode('utf-8')
    iv = os.urandom(12)
    
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
    
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    
    encrypted = f"{base64.b64encode(iv).decode()}.{base64.b64encode(tag).decode()}.{base64.b64encode(ciphertext).decode()}"
    
    print(f"\nEncrypted data:")
    print(encrypted)
    print(f"Length: {len(encrypted)} chars\n")
    
    # Now decrypt it back
    print("Decrypting...")
    parts = encrypted.split('.')
    iv_decoded = base64.b64decode(parts[0])
    tag_decoded = base64.b64decode(parts[1])
    ciphertext_decoded = base64.b64decode(parts[2])
    
    # Combine tag + ciphertext
    combined = tag_decoded + ciphertext_decoded
    
    # Decrypt
    aesgcm2 = AESGCM(key)
    decrypted_plaintext = aesgcm2.decrypt(iv_decoded, combined, None)
    
    # Parse JSON
    decrypted_data = json.loads(decrypted_plaintext.decode('utf-8'))
    
    print("\nDecrypted data:")
    print(json.dumps(decrypted_data, indent=2))
    
    # Verify
    print("\n" + "=" * 60)
    if decrypted_data['id'] == test_data['id'] and decrypted_data['level'] == test_data['level']:
        print("✓ SUCCESS: Encryption/Decryption cycle works correctly!")
    else:
        print("✗ FAILED: Data mismatch after decryption")
    print("=" * 60)
    
    # Now test with actual API call
    print("\n" + "=" * 60)
    print("Testing with actual API call...")
    print("=" * 60)
    
    import requests
    
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
    
    api_request = {
        "keyId": key_id,
        "keyToken": key_token,
        "data": encrypted
    }
    
    print(f"Making POST request to https://nextmusic.toubiec.cn/api/getSongUrl")
    print(f"Request body preview: {json.dumps(api_request, ensure_ascii=False)[:200]}...\n")
    
    try:
        response = requests.post(
            'https://nextmusic.toubiec.cn/api/getSongUrl',
            json=api_request,
            headers=headers,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        response_json = response.json()
        print(f"\nResponse JSON:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        
        # If response has ciphertext, decrypt it
        if response_json.get('ciphertext'):
            print("\n" + "=" * 60)
            print("Response is encrypted, attempting to decrypt...")
            print("=" * 60)
            
            ciphertext_response = response_json['ciphertext']
            parts = ciphertext_response.split('.')
            iv_r = base64.b64decode(parts[0])
            tag_r = base64.b64decode(parts[1])
            ct_r = base64.b64decode(parts[2])
            
            combined_r = tag_r + ct_r
            
            aesgcm3 = AESGCM(key)
            decrypted_response = aesgcm3.decrypt(iv_r, combined_r, None)
            
            decrypted_json = json.loads(decrypted_response.decode('utf-8'))
            
            print("\nDecrypted response:")
            print(json.dumps(decrypted_json, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_cycle()
