# NextMusicTool 测试脚本说明

## 📁 位置
所有测试脚本位于：`tasks/test_scripts/`

---

## 📜 测试脚本清单

### 1. test_encryption_format.py (2.3KB)

#### 🎯 作用
验证 AES-GCM 加密算法的实现是否正确，确保加密输出格式与 JavaScript 实现一致。

#### 📋 功能
- 使用固定的密钥进行加密和解密测试
- 输出加密后的数据格式（IV.tag.ciphertext）
- 对比生成的加密数据与浏览器示例的格式和长度
- 分析浏览器示例数据的各个部分（IV、Tag、Ciphertext 的长度）

#### 🔍 测试内容
```python
1. 密钥解码和验证（32 bytes）
2. 数据序列化（JSON with timestamp）
3. IV 生成（12 bytes 随机值）
4. AES-GCM 加密
5. 分割 ciphertext 和 tag
6. Base64 编码和格式化
7. 本地解密验证（加密→解密循环）
8. 与浏览器示例对比
```

#### ✅ 是否需要保留
**是 - 强烈推荐保留**

**理由**：
- 快速验证加密算法实现的正确性
- 当修改加密逻辑时，可以立即运行此脚本确认没有破坏基本功能
- 不依赖网络，可以离线运行
- 执行速度快（< 1秒）

**使用场景**：
- 修改 `_encrypt_data()` 或 `_decrypt_data()` 方法后
- 更换加密库或调整加密参数时
- 需要向他人展示加密格式时

---

### 2. test_with_new_key.py (5.0KB)

#### 🎯 作用
使用 `api_docs/next_misic_tool.md` 中提供的示例密钥进行完整的 API 调用测试。

#### 📋 功能
- 使用文档中的固定密钥（keyId, keyToken, key）
- 执行完整的流程：加密 → API 调用 → 响应处理 → 解密
- 包含详细的调试输出和错误追踪
- 如果响应被加密，自动尝试解密

#### 🔍 测试内容
```python
1. 使用文档中的密钥初始化
2. 准备测试数据（song_id + level + timestamp）
3. 加密请求数据
4. 构造 API 请求 body {keyId, keyToken, data}
5. 发送 POST 请求到 /api/getSongUrl
6. 处理响应（明文或加密）
7. 如果响应有 ciphertext，尝试解密
8. 输出完整的请求和响应信息
```

#### ⚠️ 是否需要保留
**有条件保留 - 仅用于问题复现**

**理由**：
- ❌ 文档中的密钥可能已过期，无法成功调用 API
- ❌ 每次运行都会得到不同的结果（取决于密钥时效性）
- ✅ 可以作为参考模板，了解完整的 API 调用流程
- ✅ 当用户提供新的有效密钥时，可以快速替换测试

**使用场景**：
- 需要从已知的密钥开始调试时
- 向他人演示 API 调用流程时
- 作为编写其他测试脚本的参考

**建议**：
- 可以保留作为参考，但不必经常运行
- 如果长期无法使用，可以考虑删除或归档

---

### 3. test_nextmusic_fixed.py (1.7KB)

#### 🎯 作用
测试 `NextMusicTool` 类的完整功能，验证整个工具链是否正常工作。

#### 📋 功能
- 实例化 `NextMusicTool` 类
- 调用 `get_song_url()` 方法获取歌曲 URL
- 验证返回的数据结构和字段
- 输出简洁的成功/失败信息

#### 🔍 测试内容
```python
1. 导入 NextMusicTool 类
2. 创建工具实例
3. 调用 get_song_url(song_id, level)
4. 检查返回的 code 是否为 200
5. 提取并显示歌曲信息（name, artist, album, url 等）
6. 错误处理和异常捕获
```

#### ✅ 是否需要保留
**是 - 核心集成测试**

**理由**：
- 最接近实际使用场景的测试
- 验证 NextMusicTool 类的完整功能
- 代码简洁，易于理解和维护
- 可以直接用于日常功能验证

**使用场景**：
- 每次修改 `tool_next_music.py` 后运行
- 验证 API 是否正常工作的快速测试
- 作为其他模块调用 NextMusicTool 的示例代码

**建议**：
- **强烈推荐保留**
- 可以考虑添加更多测试用例（不同的 song_id、不同的 quality level）
- 可以扩展为正式的单元测试套件

---

### 4. test_nextmusic_encryption.py (4.5KB)

#### 🎯 作用
早期的加密测试脚本，在确定使用 AES-GCM 之前的探索性测试。

#### 📋 功能
- 尝试使用不同的加密模式（AES-ECB、AES-CBC）
- 测试添加 timestamp 前后的差异
- 使用 pycryptodome 库进行加密

#### 🔍 测试内容
```python
1. 从 /api/key 获取密钥
2. 尝试 AES-ECB 模式加密
3. 尝试 AES-CBC 模式加密（零 IV）
4. 添加 timestamp 字段测试
5. 发送 API 请求验证
```

#### ❌ 是否需要保留
**否 - 可以安全删除**

**理由**：
- ❌ 已被确定为错误的加密方式（应该用 AES-GCM，不是 ECB/CBC）
- ❌ 代码已被 `test_encryption_format.py` 和 `test_nextmusic_fixed.py` 替代
- ❌ 保留了过时的实现思路，可能造成混淆
- ❌ 占用空间且不再有价值

**使用场景**：
- 无 - 已过时

**建议**：
- **可以安全删除**
- 如果需要保留历史记录，可以移动到 `archive/` 目录
- 或者在 Git 历史中已经保存，无需保留在工作目录

---

## 📊 总结与建议

### 必须保留的脚本
| 脚本 | 大小 | 重要性 | 用途 |
|------|------|--------|------|
| `test_encryption_format.py` | 2.3KB | ⭐⭐⭐⭐⭐ | 验证加密算法正确性 |
| `test_nextmusic_fixed.py` | 1.7KB | ⭐⭐⭐⭐⭐ | 集成测试，验证完整功能 |

### 可选保留的脚本
| 脚本 | 大小 | 重要性 | 用途 |
|------|------|--------|------|
| `test_with_new_key.py` | 5.0KB | ⭐⭐ | 参考模板，问题复现 |

### 可以删除的脚本
| 脚本 | 大小 | 重要性 | 原因 |
|------|------|--------|------|
| `test_nextmusic_encryption.py` | 4.5KB | ⭐ | 已过时，被替代 |

---

## 💡 推荐的清理操作

### 方案 1: 最小化保留（推荐）
```bash
# 删除过时脚本
rm tasks/test_scripts/test_nextmusic_encryption.py

# 保留核心测试脚本
- test_encryption_format.py    # 算法验证
- test_nextmusic_fixed.py      # 集成测试
```

### 方案 2: 完整保留（谨慎型）
```bash
# 保留所有脚本，但添加注释说明
# 适合需要详细记录开发过程的场景
```

### 方案 3: 归档整理
```bash
# 创建归档目录
mkdir tasks/test_scripts/archive

# 移动过时和参考脚本
mv tasks/test_scripts/test_nextmusic_encryption.py tasks/test_scripts/archive/
mv tasks/test_scripts/test_with_new_key.py tasks/test_scripts/archive/

# 只保留核心测试脚本在主目录
- test_encryption_format.py
- test_nextmusic_fixed.py
```

---

## 🔄 后续测试策略

### 日常开发
1. 修改加密逻辑后 → 运行 `test_encryption_format.py`
2. 修改 API 调用逻辑后 → 运行 `test_nextmusic_fixed.py`
3. 两者都通过 → 可以提交代码

### 问题排查
1. API 返回错误 → 运行 `test_nextmusic_fixed.py` 查看详细日志
2. 怀疑加密问题 → 运行 `test_encryption_format.py` 验证算法
3. 需要对比浏览器行为 → 参考 `test_with_new_key.py` 的结构

### 未来扩展
可以考虑添加：
- [ ] 单元测试（使用 pytest）
- [ ] 性能测试（加密/解密速度）
- [ ] 边界条件测试（空数据、错误密钥等）
- [ ] 自动化测试（CI/CD 集成）

---

## 📝 备注

- 所有测试脚本都需要安装 `cryptography` 库
- 运行测试前确保已执行 `uv sync`
- 测试脚本使用 DEBUG 级别日志，可以看到详细的执行过程
- 如果 API 持续返回 400 错误，可能需要用户提供浏览器抓包数据
