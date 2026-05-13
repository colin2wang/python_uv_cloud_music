# NextMusicTool AES-GCM 加密适配任务状态

## 📅 任务信息
- **开始时间**: 2026-05-13
- **当前状态**: 🔄 进行中 - 加密实现完成，API 调用测试失败
- **优先级**: 高

## 🎯 任务目标
修复 `tool_next_music.py` 以支持 NextMusic API 的新 AES-GCM 加密格式

---

## ✅ 已完成的工作

### 1. 分析与研究
- [x] 获取并分析 JavaScript 源码 (`https://wyapi.toubiec.cn/assets/index-CkyuA-1-.js`)
- [x] 提取关键加密函数：`_B()`, `hB()`, `gB()`, `he()`, `fB()`, `pB()`, `mB()`
- [x] 理解 AES-GCM 加密流程和數據格式
- [x] 记录 API 调用流程到 `api_docs/next_misic_tool.md`

### 2. 代码实现
- [x] 重写 `tool_next_music.py` 中的 `NextMusicTool` 类
  - [x] 实现 `_get_encryption_key()` - 获取加密密钥
  - [x] 实现 `_encrypt_data()` - AES-GCM 加密
  - [x] 实现 `_decrypt_data()` - AES-GCM 解密
  - [x] 实现 `_array_buffer_to_base64()` 和 `_base64_to_array_buffer()`
  - [x] 更新 `get_song_url()` 方法使用新的加密流程
- [x] 添加完整的浏览器-like HTTP Headers
- [x] 添加调试日志输出

### 3. 依赖管理
- [x] 在 `pyproject.toml` 中添加 `cryptography>=42.0.0`
- [x] 运行 `uv sync` 安装新依赖

### 4. 测试验证
- [x] 创建测试脚本 `test_encryption_format.py` 验证加密格式
- [x] 确认加密输出格式与浏览器一致（IV.tag.ciphertext，总长度130 chars）
- [x] 创建测试脚本 `test_with_new_key.py` 测试完整流程
- [x] 创建测试脚本 `test_nextmusic_fixed.py` 测试 NextMusicTool 类

### 5. 文档记录
- [x] 更新 `api_docs/next_misic_tool.md` 包含完整的 API 调用示例
- [x] 创建记忆 "NextMusicTool AES-GCM 加密适配完整实现流程"

---

## ❌ 当前问题

### API 调用失败
**现象**: 
- 调用 `https://nextmusic.toubiec.cn/api/getSongUrl` 返回 **400 Bad Request**
- 错误消息: `"Invalid session or payload"`

**已排除的原因**:
- ✅ API endpoint 可访问（不是 404）
- ✅ Headers 完整（包含所有必需的浏览器特征头）
- ✅ 加密格式正确（已通过本地加解密测试验证）
- ✅ 密钥获取成功（从 `/api/key` 实时获取）

**可能的原因**:
1. ⚠️ **密钥时效性问题** - 每次获取的密钥可能有短时效性，或者需要与特定的 keyId/keyToken 配对使用
2. ⚠️ **服务器端防自动化检测** - 可能检测到非浏览器环境而拒绝服务
3. ⚠️ **加密细节差异** - JavaScript Web Crypto API 和 Python cryptography 库可能存在细微的实现差异
4. ⚠️ **缺少额外的验证字段** - 请求数据可能需要额外的字段或签名

---

## 📋 待办事项

### 方案 A: 继续调试 NextMusicTool（需要用户协助）

#### 需要用户提供的信息：
1. **浏览器抓包数据**
   - [ ] 在浏览器中成功调用 `/api/getSongUrl` 的完整请求和响应
   - [ ] 包括：
     - 请求 URL
     - 请求 Headers（完整）
     - 请求 Body（原始的 JSON，包括 keyId, keyToken, data）
     - 响应 Status Code
     - 响应 Headers
     - 响应 Body（如果加密，提供 ciphertext 字段）
   
2. **时序信息**
   - [ ] 从调用 `/api/key` 到调用 `/api/getSongUrl` 的时间间隔
   - [ ] 是否每次请求都重新获取密钥，还是复用之前的密钥

3. **JavaScript 执行环境**
   - [ ] 确认是否有其他前置条件（如 cookies、localStorage 等）
   - [ ] 是否有额外的中间件或拦截器处理请求

#### 需要进一步调查的代码：
- [ ] 检查 `api_docs/next_misic_tool.md` 中的 `he()` 函数是否有遗漏的逻辑
- [ ] 查看是否有其他相关的辅助函数未被发现
- [ ] 对比 Python 生成的加密数据与浏览器实际发送的数据（逐字节对比）

#### 调试步骤：
1. [ ] 使用浏览器开发者工具 Network 面板捕获成功的请求
2. [ ] 提取请求中的所有数据（keyId, keyToken, encrypted data）
3. [ ] 使用相同的密钥在 Python 中重新加密相同的数据
4. [ ] 对比两个加密结果是否一致
5. [ ] 如果不一致，逐步排查差异点（IV、padding、encoding 等）

### 方案 B: 禁用 NextMusicTool（推荐备选方案）

如果方案 A 无法解决，建议采用此方案：

- [ ] 修改 `config.yml`，将 `metadata.use_next_music_tool` 改为 `false`
- [ ] 测试主 API (`dm.jfjt.cc` 或 `musicapi.lxchen.cn`) 是否能正常返回下载链接
- [ ] 验证歌曲下载功能是否正常
- [ ] 更新 README 或文档说明 NextMusicTool 的当前状态

---

## 📚 相关文件清单

### 核心代码文件
- `tool_next_music.py` - NextMusicTool 类实现（已修改）
- `process_cloud_music.py` - 调用 NextMusicTool 的地方（第430-436行）
- `config_manager.py` - 配置管理，包含 `should_use_next_music_tool()` 方法

### 配置文件
- `config.yml` - 包含 `use_next_music_tool: true` 配置项（第56行）
- `pyproject.toml` - 项目依赖，已添加 `cryptography`

### 文档文件
- `api_docs/next_misic_tool.md` - API 文档和 JavaScript 源码（已更新）
- `tasks/nextmusic_encryption_task.md` - 本任务状态文件

### 测试文件（位于 `tasks/test_scripts/`）

📖 **详细说明**: 查看 [test_scripts/README_test_scripts.md](test_scripts/README_test_scripts.md) 了解每个脚本的作用和保留建议。

#### 快速概览：
- ✅ **test_encryption_format.py** (2.3KB) - 验证 AES-GCM 加密算法正确性 **[必须保留]**
- ✅ **test_nextmusic_fixed.py** (1.7KB) - NextMusicTool 集成测试 **[必须保留]**
- ⚠️ **test_with_new_key.py** (5.0KB) - 使用文档密钥的完整流程测试 **[可选保留]**
- ❌ **test_nextmusic_encryption.py** (4.5KB) - 早期探索性测试，已过时 **[可以删除]**

💡 **建议操作**: 
- 保留前两个核心测试脚本
- 可以考虑删除 `test_nextmusic_encryption.py`
- 详细评估请参考上述 README 文档

### 日志文件
- `logs/cloud_music_2026-05-13_16-59-14.log` - 原始错误日志（显示 400 错误）

---

## 🔍 关键技术点

### AES-GCM 加密细节
```python
# 加密流程
1. 获取密钥: POST /api/key → {keyId, keyToken, key(base64)}
2. 准备数据: {id, level, timestamp(毫秒)}
3. 序列化: JSON.stringify(data, separators=(',', ':'))
4. 生成 IV: 12 bytes 随机值
5. 加密: AESGCM(key).encrypt(iv, plaintext, None) → ciphertext+tag
6. 分割: ciphertext = result[:-16], tag = result[-16:]
7. 编码: base64(IV).base64(tag).base64(ciphertext)

# 解密流程
1. 分割: parts = encrypted.split('.') → [iv_b64, tag_b64, ct_b64]
2. 解码: iv, tag, ciphertext = base64decode(parts)
3. 组合: combined = tag + ciphertext  # 注意顺序！
4. 解密: AESGCM(key).decrypt(iv, combined, None) → plaintext
5. 解析: JSON.parse(plaintext)
```

### 重要注意事项
- ⚠️ 每次 API 调用都应重新获取密钥（`_B()` 在 `he()` 中被调用）
- ⚠️ 请求数据必须包含 `timestamp` 字段（毫秒级时间戳）
- ⚠️ 响应可能是明文或加密（检查是否有 `ciphertext` 字段）
- ⚠️ Tag 和 Ciphertext 的组合顺序：**tag 在前，ciphertext 在后**

---

## 💡 下一步行动建议

### 立即可做的：
1. **询问用户选择方案**
   - 方案 A: 继续调试（需要用户提供浏览器抓包数据）
   - 方案 B: 禁用 NextMusicTool，使用主 API

2. **如果选择方案 A**，指导用户：
   - 打开浏览器开发者工具 (F12)
   - 访问 https://wyapi.toubiec.cn
   - 切换到 Network 面板
   - 执行一次歌曲解析操作
   - 找到 `/api/getSongUrl` 请求
   - 复制请求和响应的详细信息

3. **如果选择方案 B**，立即执行：
   - 修改 `config.yml`
   - 测试主 API 功能
   - 更新相关文档

### 长期优化：
- [ ] 考虑添加密钥缓存机制（如果密钥有有效期）
- [ ] 添加更详细的错误处理和日志
- [ ] 编写单元测试覆盖加密/解密逻辑
- [ ] 考虑添加重试机制和降级策略

---

## 📝 备注

- JavaScript 源码来自: `https://wyapi.toubiec.cn/assets/index-CkyuA-1-.js`
- 加密算法确认: AES-256-GCM (32字节密钥)
- Python 库: `cryptography.hazmat.primitives.ciphers.aead.AESGCM`
- 测试时发现本地加解密循环成功，但 API 调用失败，说明问题可能在服务端验证而非加密算法本身
