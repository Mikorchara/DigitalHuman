# 代码审查问题清单 — v2

---

## 🟡 待处理

### 1. `_start_lip_sync` 已弃用但仍保留

**文件**：`ui/main_window.py`

v3 已接入 TTS 语音合成，实际口型由 `_on_user_message` 中的 TTS 路径驱动，此方法不再被新代码调用。保留作为兼容，但可考虑移除。

### 2. 死代码：`_resolve_web_path` 未使用

**文件**：`ui/main_window.py`

为 PyInstaller 打包预留，暂不删除。

---

## 🔵 建议

### 3. `web/app.js` 硬编码 200ms 等待

若模型加载较慢（如首次加载 moc3），200ms 可能不够。已有 500ms 轮询兜底，但两处时间差可能导致短暂闪烁。

### 4. worker 线程初始化 pygame mixer 仅用于读时长

**文件**：`core/tts_engine.py`

可以用轻量库（如 `mutagen`）获取 MP3 时长，避免在后台线程初始化整个音频引擎。

### 5. `speak()` 标记"兼容旧 API"但无旧代码依赖

**文件**：`core/tts_engine.py`

该函数无任何调用方，建议移除或等待实际需要时再加。

### 6. `abs(hash(text))` 防负 hash 已过时

**文件**：`core/tts_engine.py`

Python 3.12+ 默认启用 hash 随机化，`hash()` 不再为负。`abs()` 可保留但不必要。
