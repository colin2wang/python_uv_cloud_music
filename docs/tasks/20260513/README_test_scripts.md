# NextMusicTool Test Scripts Documentation

## 📁 Location
All test scripts are located in: `tasks/20260513/`

---

## 📜 Test Scripts List

### 1. test_encryption_format.py (2.3KB)

#### 🎯 Purpose
Verifies the correctness of the AES-GCM encryption algorithm implementation, ensuring the encrypted output format matches the JavaScript implementation.

#### 📋 Functionality
- Performs encryption and decryption tests using a fixed key
- Outputs the encrypted data format (IV.tag.ciphertext)
- Compares the generated encrypted data format and length with browser examples
- Analyzes each part of the browser example data (IV, Tag, Ciphertext lengths)

#### 🔍 Test Coverage
```python
1. Key decoding and verification (32 bytes)
2. Data serialization (JSON with timestamp)
3. IV generation (12 bytes random value)
4. AES-GCM encryption
5. Splitting ciphertext and tag
6. Base64 encoding and formatting
7. Local decryption verification (encrypt→decrypt cycle)
8. Comparison with browser example
```

#### ✅ Should Keep?
**Yes - Highly Recommended**

**Reasons**:
- Quickly verifies the correctness of encryption algorithm implementation
- Can be run immediately after modifying encryption logic to confirm no basic functionality is broken
- Does not depend on network, can run offline
- Fast execution (< 1 second)

**Use Cases**:
- After modifying `_encrypt_data()` or `_decrypt_data()` methods
- When changing encryption libraries or adjusting encryption parameters
- When demonstrating encryption format to others

---

### 2. test_with_new_key.py (5.0KB)

#### 🎯 Purpose
Performs complete API call testing using sample keys provided in `api_docs/next_misic_tool.md`.

#### 📋 Functionality
- Uses fixed keys from documentation (keyId, keyToken, key)
- Executes complete flow: encrypt → API call → response handling → decrypt
- Includes detailed debug output and error tracking
- Automatically attempts decryption if response is encrypted

#### 🔍 Test Coverage
```python
1. Initialize with keys from documentation
2. Prepare test data (song_id + level + timestamp)
3. Encrypt request data
4. Construct API request body {keyId, keyToken, data}
5. Send POST request to /api/getSongUrl
6. Handle response (plaintext or encrypted)
7. If response has ciphertext, attempt decryption
8. Output complete request and response information
```

#### ⚠️ Should Keep?
**Conditional - For Issue Reproduction Only**

**Reasons**:
- ❌ Keys in documentation may have expired, unable to successfully call API
- ❌ Each run produces different results (depends on key validity)
- ✅ Can serve as a reference template to understand complete API call flow
- ✅ Can quickly replace and test when users provide new valid keys

**Use Cases**:
- When debugging needs to start from known keys
- When demonstrating API call flow to others
- As a reference for writing other test scripts

**Recommendation**:
- Can be kept as reference, but doesn't need frequent execution
- Consider deleting or archiving if unusable long-term

---

### 3. test_nextmusic_fixed.py (1.7KB)

#### 🎯 Purpose
Tests the complete functionality of the `NextMusicTool` class, verifying the entire toolchain works correctly.

#### 📋 Functionality
- Instantiates `NextMusicTool` class
- Calls `get_song_url()` method to retrieve song URL
- Validates returned data structure and fields
- Outputs concise success/failure information

#### 🔍 Test Coverage
```python
1. Import NextMusicTool class
2. Create tool instance
3. Call get_song_url(song_id, level)
4. Check if returned code is 200
5. Extract and display song info (name, artist, album, url, etc.)
6. Error handling and exception catching
```

#### ✅ Should Keep?
**Yes - Core Integration Test**

**Reasons**:
- Closest to actual usage scenario
- Verifies complete functionality of NextMusicTool class
- Code is concise, easy to understand and maintain
- Can be directly used for daily functional verification

**Use Cases**:
- Run after each modification to `tool_next_music_v2.py`
- Quick test to verify API is working properly
- Example code for other modules calling NextMusicTool

**Recommendation**:
- **Highly recommended to keep**
- Consider adding more test cases (different song_id, different quality levels)
- Can be expanded into a formal unit test suite

---

### 4. test_by_google.py (3.5KB)

#### 🎯 Purpose
Independent quick test script with logger support, useful for rapid API testing without full tool initialization.

#### 📋 Functionality
- Standalone implementation of encryption/decryption functions
- Direct API call without class wrapper
- Uses project's logging configuration
- Simple command-line interface for quick testing

#### 🔍 Test Coverage
```python
1. Direct function calls (encrypt_payload, decrypt_response)
2. Complete API flow test
3. Logger-based output (console + file)
4. Response parsing and validation
```

#### ✅ Should Keep?
**Yes - Quick Testing Tool**

**Reasons**:
- Lightweight alternative to full NextMusicTool class
- Useful for debugging specific API endpoints
- Easy to modify for experimental changes
- Demonstrates raw API interaction pattern

**Use Cases**:
- Quick API connectivity tests
- Debugging encryption/decryption issues
- Testing new API endpoints before integrating into main class

---

### 5. test_nextmusic_encryption.py (4.5KB)

#### 🎯 Purpose
Early encryption test script, exploratory testing before determining to use AES-GCM.

#### 📋 Functionality
- Attempts different encryption modes (AES-ECB, AES-CBC)
- Tests differences before and after adding timestamp
- Uses pycryptodome library for encryption

#### 🔍 Test Coverage
```python
1. Get key from /api/key
2. Try AES-ECB mode encryption
3. Try AES-CBC mode encryption (zero IV)
4. Add timestamp field test
5. Send API request verification
```

#### ❌ Should Keep?
**No - Safe to Delete**

**Reasons**:
- ❌ Determined to be incorrect encryption method (should use AES-GCM, not ECB/CBC)
- ❌ Code has been replaced by `test_encryption_format.py` and `test_nextmusic_fixed.py`
- ❌ Retains outdated implementation思路, may cause confusion
- ❌ Occupies space with no current value

**Use Cases**:
- None - Obsolete

**Recommendation**:
- **Safe to delete**
- If historical record needed, move to `archive/` directory
- Or already saved in Git history, no need to keep in working directory

---

## 📊 Summary and Recommendations

### Must Keep Scripts
| Script | Size | Importance | Purpose |
|--------|------|------------|---------|
| `test_encryption_format.py` | 2.3KB | ⭐⭐⭐⭐⭐ | Verify encryption algorithm correctness |
| `test_nextmusic_fixed.py` | 1.7KB | ⭐⭐⭐⭐⭐ | Integration test, verify complete functionality |
| `test_by_google.py` | 3.5KB | ⭐⭐⭐⭐ | Quick testing tool with logger |

### Optional Scripts
| Script | Size | Importance | Purpose |
|--------|------|------------|---------|
| `test_with_new_key.py` | 5.0KB | ⭐⭐ | Reference template, issue reproduction |

### Can Delete Scripts
| Script | Size | Importance | Reason |
|--------|------|------------|--------|
| `test_nextmusic_encryption.py` | 4.5KB | ⭐ | Obsolete, replaced |

---

## 💡 Recommended Cleanup Actions

### Option 1: Minimal Retention (Recommended)
```bash
# Delete obsolete scripts
rm tasks/20260513/test_nextmusic_encryption.py

# Keep core test scripts
- test_encryption_format.py    # Algorithm verification
- test_nextmusic_fixed.py      # Integration test
- test_by_google.py            # Quick testing
```

### Option 2: Full Retention (Conservative)
```bash
# Keep all scripts, but add comments explaining purpose
# Suitable for scenarios requiring detailed development process documentation
```

### Option 3: Archive Organization
```bash
# Create archive directory
mkdir tasks/20260513/archive

# Move obsolete and reference scripts
mv tasks/20260513/test_nextmusic_encryption.py tasks/20260513/archive/
mv tasks/20260513/test_with_new_key.py tasks/20260513/archive/

# Keep only core test scripts in main directory
- test_encryption_format.py
- test_nextmusic_fixed.py
- test_by_google.py
```

---

## 🔄 Future Testing Strategy

### Daily Development
1. After modifying encryption logic → Run `test_encryption_format.py`
2. After modifying API call logic → Run `test_nextmusic_fixed.py`
3. Both pass → Ready to commit code

### Troubleshooting
1. API returns error → Run `test_nextmusic_fixed.py` for detailed logs
2. Suspect encryption issue → Run `test_encryption_format.py` to verify algorithm
3. Need to compare with browser behavior → Reference `test_with_new_key.py` structure

### Future Extensions
Consider adding:
- [ ] Unit tests (using pytest)
- [ ] Performance tests (encryption/decryption speed)
- [ ] Boundary condition tests (empty data, wrong keys, etc.)
- [ ] Automated tests (CI/CD integration)

---

## 📝 Notes

- All test scripts require `cryptography` library installed
- Ensure `uv sync` has been executed before running tests
- Test scripts use DEBUG level logging to see detailed execution process
- If API continuously returns 400 errors, may need browser packet capture data from user
