# NextMusicTool AES-GCM Encryption Adaptation Task Status

## 📅 Task Information
- **Start Date**: 2026-05-13
- **Last Updated**: 2026-05-13 21:45
- **Current Status**: ✅ Completed - AES-GCM encryption implemented successfully, API calls working normally, code refactored and optimized
- **Priority**: High

## 🎯 Task Objective
Fix `tool_next_music.py` to support the new AES-GCM encryption format of NextMusic API

---

## ✅ Completed Work

### 1. Analysis and Research
- [x] Obtained and analyzed JavaScript source code (`https://wyapi.toubiec.cn/assets/index-CkyuA-1-.js`)
- [x] Extracted key encryption functions: `_B()`, `hB()`, `gB()`, `he()`, `fB()`, `pB()`, `mB()`
- [x] Understood AES-GCM encryption flow and data format
- [x] Documented API call flow in `api_docs/next_misic_tool.md`

### 2. Code Implementation
- [x] Rewrote `NextMusicTool` class in `tool_next_music.py`
  - [x] Implemented `_get_encryption_key()` - Get encryption key
  - [x] Implemented `_encrypt_data()` - AES-GCM encryption
  - [x] Implemented `_decrypt_data()` - AES-GCM decryption
  - [x] Implemented `_array_buffer_to_base64()` and `_base64_to_array_buffer()`
  - [x] Updated `get_song_url()` method to use new encryption flow
- [x] Added complete browser-like HTTP Headers
- [x] Added debug logging output

### 3. Dependency Management
- [x] Added `cryptography>=42.0.0` to `pyproject.toml`
- [x] Ran `uv sync` to install new dependencies

### 4. Testing and Verification
- [x] Created test script `test_encryption_format.py` to verify encryption format
- [x] Confirmed encrypted output format matches browser (IV.tag.ciphertext, total length 130 chars)
- [x] Created test script `test_with_new_key.py` to test complete flow
- [x] Created test script `test_nextmusic_fixed.py` to test NextMusicTool class

### 5. Documentation
- [x] Updated `api_docs/next_misic_tool.md` with complete API call examples
- [x] Created memory "NextMusicTool AES-GCM Encryption Adaptation Complete Implementation Flow"

### 6. Code Refactoring and Optimization (2026-05-13 21:35)
- [x] Merged code from `test_by_google.py` into `tool_next_music_v2.py`
- [x] Replaced all `print()` with logger
- [x] Added retry mechanism with random backoff strategy (10-20 seconds)
- [x] Fixed return value type inconsistency issue
- [x] Added comprehensive exception handling

---

## ❌ Resolved Issues

### Issue: Response Decryption Failure (InvalidTag)
**Symptoms**: 
- API returns 200 with encrypted ciphertext
- But decryption with obtained key throws `cryptography.exceptions.InvalidTag` exception

**Root Cause**:
- **Incorrect order of tag and ciphertext combination during AES-GCM decryption**
- Original code used: `tag + ciphertext` (incorrect)
- Correct should be: `ciphertext + tag`

**Solution**:
- Modified line 185 in `_decrypt_data()` method:
  ```python
  # Incorrect implementation
  ciphertext_with_tag = tag + ciphertext
  
  # Correct implementation
  ciphertext_with_tag = ciphertext + tag
  ```

**Verification Results**:
- ✅ Successfully obtained song download link
- ✅ Decrypted data contains complete song information (id, url, br, level, size, md5, time)
- ✅ Test song ID 238847 successfully obtained lossless FLAC download link

---

### Issue: DNS Resolution Failure and Network Fluctuations
**Symptoms**: 
- Runtime error: `curl: (6) Could not resolve host: nextmusic.toubiec.cn`
- Temporary network issues cause request failures

**Solution**:
- Added retry mechanism in `tool_next_music_v2.py`
- Uses random backoff strategy (10-20 seconds)
- Maximum 5 retries (configurable via `MAX_RETRY` constant)
- Detailed logging for each attempt and error information

**Code Example**:
```python
def get_song_url(self, song_id: str, level: str = "lossless", max_retries: int = MAX_RETRY):
    """Get song URL from NextMusic API with retry mechanism"""
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            # ... API call logic ...
            return result
        except Exception as e:
            last_error = e
            logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
            if attempt < max_retries:
                import random
                wait_time = round(random.uniform(10, 20), 1)  # Random between 10-20 seconds, precise to 0.1s
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
    
    logger.error(f"All retries failed, last error: {str(last_error)}")
    return None
```

---

### Issue: Return Value Type Inconsistency
**Symptoms**: 
- `get_music_url()` initially only returned URL string
- Caller expected complete response dictionary (containing code and data)
- Caused `AttributeError: 'str' object has no attribute 'get'`

**Solution**:
- Modified return value: from returning `url` string to returning complete response dictionary
- For encrypted responses: return `decrypted_data` (complete dictionary)
- For unencrypted responses: return `response_json` (complete dictionary)
- Caller can access `result["code"]`, `result["data"]["url"]` and other fields

---

### Issue: Scattered Code and Dependencies
**Symptoms**: 
- Encryption/decryption logic in `test_by_google.py`
- Business logic in `tool_next_music_v2.py`
- Two files depend on each other, difficult to maintain

**Solution**:
- Merged all code into `NextMusicTool` class in `tool_next_music_v2.py`
- `test_by_google.py` retained as independent quick test script
- `NextMusicTool` is now a completely independent module, containing:
  - `encrypt_payload()` - Static method, encrypts request data
  - `decrypt_response()` - Static method, decrypts response data
  - `get_song_url()` - Instance method, complete API call flow

---

### Issue: Lack of Unified Logging System
**Symptoms**: 
- Used `print()` for output, unable to control log level
- No log file records, difficult to troubleshoot issues

**Solution**:
- Imported and used project's `logging_config.setup_logger()`
- All `print()` replaced with `logger.info()`, `logger.debug()`, `logger.error()`
- Logs output to both console and files in `logs/` directory
- Can control output detail level by adjusting log level

---

## 📋 Todo Items

### ✅ Completed Work

All tasks completed! NextMusicTool is now working properly.

#### Final Verification:
- [x] Test song ID 238847 - Successfully obtained lossless download link
- [x] Test song ID 26427662 - Successfully obtained lossless download link (using test_by_google.py)
- [x] Log level adjusted back to INFO (production environment)
- [x] Code cleaned up, unnecessary debug logs removed

---

## 📚 Related Files List

### Core Code Files
- `tool_next_music_v2.py` - NextMusicTool class implementation (**latest version**, includes complete implementation and retry mechanism)
- `test_by_google.py` - Independent test script (uses logger, suitable for quick testing)
- `tool_next_music.py` - Early version of NextMusicTool class (deprecated)
- `process_cloud_music.py` - Where NextMusicTool is called (lines 430-436)
- `config_manager.py` - Configuration management, contains `should_use_next_music_tool()` method

### Configuration Files
- `config.yml` - Contains `use_next_music_tool: true` configuration item (line 56)
- `pyproject.toml` - Project dependencies, added `cryptography`

### Documentation Files
- `api_docs/next_misic_tool.md` - API documentation and JavaScript source code (updated)
- `tasks/20260513/nextmusic_encryption_task.md` - This task status file

### Test Files (located in `tasks/20260513/`)

📖 **Detailed Explanation**: See [README_test_scripts.md](README_test_scripts.md) for the purpose and retention recommendations of each script.

#### Quick Overview:
- ✅ **test_encryption_format.py** (2.3KB) - Verify AES-GCM encryption algorithm correctness **[Must Keep]**
- ✅ **test_nextmusic_fixed.py** (1.7KB) - NextMusicTool integration test **[Must Keep]**
- ✅ **test_by_google.py** (3.5KB) - Quick testing tool with logger **[Recommended]**
- ⚠️ **test_with_new_key.py** (5.0KB) - Complete flow test using documentation keys **[Optional]**
- ❌ **test_nextmusic_encryption.py** (4.5KB) - Early exploratory test, obsolete **[Can Delete]**

💡 **Recommended Actions**: 
- Keep the first three core test scripts
- Consider deleting `test_nextmusic_encryption.py`
- Refer to the above README document for detailed evaluation

### Log Files
- `logs/cloud_music_2026-05-13_16-59-14.log` - Original error log (shows 400 error)

---

## 🔍 Key Technical Points

### AES-GCM Encryption Details
```python
# Encryption Flow
1. Get key: POST /api/key → {keyId, keyToken, key(base64)}
2. Prepare data: {id, level, timestamp(milliseconds)}
3. Serialize: JSON.stringify(data, separators=(',', ':'))
4. Generate IV: 12 bytes random value
5. Encrypt: AESGCM(key).encrypt(iv, plaintext, None) → ciphertext+tag
6. Split: ciphertext = result[:-16], tag = result[-16:]
7. Encode: base64(IV).base64(tag).base64(ciphertext)

# Decryption Flow
1. Split: parts = encrypted.split('.') → [iv_b64, tag_b64, ct_b64]
2. Decode: iv, tag, ciphertext = base64decode(parts)
3. Combine: combined = ciphertext + tag  # Note the order!
4. Decrypt: AESGCM(key).decrypt(iv, combined, None) → plaintext
5. Parse: JSON.parse(plaintext)
```

### Important Notes
- ✅ Should re-obtain key for each API call (`_B()` is called in `he()`)
- ✅ Request data must include `timestamp` field (millisecond-level timestamp)
- ✅ Response may be plaintext or encrypted (check for `ciphertext` field)
- ⚠️ **Tag and Ciphertext combination order: ciphertext first, tag second** (This is critical!)

---

## 💡 Next Action Recommendations

### ✅ Completed:
1. **Fixed decryption logic** - Changed tag + ciphertext to ciphertext + tag
2. **Verified functionality** - Successfully obtained download links for multiple songs
3. **Cleaned up code** - Removed debug logs, set appropriate log levels
4. **Added retry mechanism** - Random backoff between 10-20 seconds

### Long-term Optimization (Optional):
- [ ] Consider adding key caching mechanism (if keys have expiration)
- [x] Added more detailed error handling and logging - **Completed**
- [ ] Write unit tests covering encryption/decryption logic
- [x] Added retry mechanism and fallback strategy - **Completed**

---

## 📝 Notes

- JavaScript source code from: `https://wyapi.toubiec.cn/assets/index-CkyuA-1-.js`
- Encryption algorithm confirmed: AES-256-GCM (32-byte key)
- Python library: `cryptography.hazmat.primitives.ciphers.aead.AESGCM`
- **Key Discovery**: During decryption, tag and ciphertext combination order must be `ciphertext + tag`, not `tag + ciphertext`
- Test verification: Local encrypt/decrypt cycle successful, API calls also successful

---

## 📜 Version History

### v2.1 (2026-05-13 21:45) - Retry Mechanism Enhancement
**Major Improvements**:
- ✅ Changed retry backoff from exponential to random (10-20 seconds)
- ✅ Increased MAX_RETRY from 3 to 5
- ✅ More resilient to DNS and network issues
- ✅ Better avoids detection as bot behavior

**Affected Files**:
- `tool_next_music_v2.py` - Updated retry logic

### v2.0 (2026-05-13 21:35) - Code Refactoring and Optimization
**Major Improvements**:
- ✅ Merged code from `test_by_google.py` into `tool_next_music_v2.py`
- ✅ All `print()` replaced with logger, supports log file recording
- ✅ Added retry mechanism (max 3 retries, exponential backoff)
- ✅ Fixed return value type inconsistency (now returns complete response dictionary)
- ✅ Added comprehensive exception handling
- ✅ `NextMusicTool` is now a completely independent module

**Affected Files**:
- `tool_next_music_v2.py` - Main implementation file
- `test_by_google.py` - Retained as independent test script

### v1.0 (2026-05-13 16:59) - Initial Implementation
**Main Features**:
- ✅ AES-GCM encryption/decryption implementation
- ✅ NextMusic API integration
- ✅ Successfully obtained song download links

**Key Fix**:
- 🔧 Fixed AES-GCM decryption tag and ciphertext combination order
