# 代码审查问题清单 — v2

## 🟡 v1 遗留问题

### 4. 死代码：`_resolve_web_path` 未使用 ⏭️ 有意保留

**文件**：`ui/main_window.py:78-84`

为 PyInstaller 打包预留，暂不删除。



## 🔵 建议

### 10. `web/app.js:8-12` 硬编码 200ms 等待

```javascript
setTimeout(function() {
    var w = panel.clientWidth; var h = panel.clientHeight;
    if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
}, 200);
```

若模型加载较慢（如首次加载 moc3），200ms 可能不够。已有 500ms 轮询兜底，但两处时间差可能导致短暂闪烁。

---

## 🔵 Suggestions

### 15. worker 线程初始化 pygame mixer 仅用于读时长

**文件**：`core/tts_engine.py:78`

可以用轻量库（如 `mutagen`）获取 MP3 时长，避免在后台线程初始化整个音频引擎。

### 18. `speak()` 标记"兼容旧 API"但无旧代码依赖

**文件**：`core/tts_engine.py:117-133`

该函数无任何调用方，建议移除或等待实际需要时再加。

### 19. `abs(hash(text))` 防负 hash 已过时

**文件**：`core/tts_engine.py:75`

Python 3.12+ 默认启用 hash 随机化，`hash()` 不再为负。`abs()` 可保留但不必要。


---

