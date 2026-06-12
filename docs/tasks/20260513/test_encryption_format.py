"""
Simple test to check encryption format
"""
import json
import time
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def test_encryption():
    # Sample key from API
    key_b64 = "IxPWUKBbcAz0NI9RFszQFaZrjv2cAwuUl/bXks8b8bg="
    key = base64.b64decode(key_b64)
    
    print(f"Key length: {len(key)} bytes")
    print(f"Key (hex): {key.hex()}")
    
    # Test data
    data = {
        "id": "2718994102",
        "level": "lossless",
        "timestamp": int(time.time() * 1000)
    }
    
    json_str = json.dumps(data, separators=(',', ':'))
    print(f"\nJSON: {json_str}")
    
    plaintext = json_str.encode('utf-8')
    print(f"Plaintext length: {len(plaintext)} bytes")
    
    # Generate IV
    iv = os.urandom(12)
    print(f"IV length: {len(iv)} bytes")
    print(f"IV (base64): {base64.b64encode(iv).decode()}")
    
    # Encrypt
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
    
    print(f"\nCiphertext+tag length: {len(ciphertext_with_tag)} bytes")
    
    # Split
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Tag length: {len(tag)} bytes")
    
    # Format
    encrypted = f"{base64.b64encode(iv).decode()}.{base64.b64encode(tag).decode()}.{base64.b64encode(ciphertext).decode()}"
    
    print(f"\nEncrypted format:")
    print(encrypted)
    print(f"\nEncrypted length: {len(encrypted)} chars")
    
    # Compare with browser example
    browser_example = "IbrEVoGs6x74aGDe.hfZm4LjTdRIG+yyQ2iCmbg==.pp5PYs8cogvf1GSqgN3fXiBl7d6LotZjkjMBKNBbyKwXRR203RdPAyBiYwrBmPEuhENkZjuYy/y3GGfGdBi2gg=="
    print(f"\nBrowser example:")
    print(browser_example)
    print(f"Browser example length: {len(browser_example)} chars")
    
    # Check parts
    print("\n=== Browser example analysis ===")
    parts = browser_example.split('.')
    print(f"Number of parts: {len(parts)}")
    for i, part in enumerate(parts):
        print(f"Part {i}: length={len(part)}, value={part[:50]}...")
        try:
            decoded = base64.b64decode(part)
            print(f"  Decoded length: {len(decoded)} bytes")
        except Exception as e:
            print(f"  Decode error: {e}")

if __name__ == "__main__":
    test_encryption()
