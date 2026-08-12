# 修改日期：2026-08-12

## 修改文件
- `core/tts_engine.py` — 移除基于文本 hash 的伪缓存逻辑 ---  modify_0

## 修改原因
原 `_synth_worker` 用 `abs(hash(text))` 生成缓存文件名 + `os.path.exists` 跳过合成，但该"缓存"设计本身错误：

1. **AI 回复每次不同**：同一提问拿到的回答文本几乎不会重复，不存在可复用的 MP3
2. **Python str hash 进程随机加盐**：即使文本重复，`hash()` 每次进程启动结果也不同 → 跨进程必然不命中
3. **文件播完即删**：`play_file()`/`stop()` 已实现"播完删上一个文件"，缓存文件根本留不到下次使用

结论：`os.path.exists()` 缓存检查是死代码，文件名基于 hash 也无意义，应移除。每个语音生成唯一临时文件、播完即删。

## 修改内容
- `_synth_worker`：去掉 `abs(hash(text))` 文件名 + `os.path.exists` 跳过逻辑 → 改用 `uuid.uuid4()` 唯一文件名，每次都重新调用 edge-tts 合成
- `speak()`（兼容旧 API，当前无调用方）：同样移除 exists 缓存检查，改用唯一文件名，保持行为一致

## 影响范围
- TTS 合成流程：每次回复都会重新调用 edge-tts 合成（实际行为与修改前一致——原缓存从未命中过）
- `tts_cache/` 目录：仍作临时工作目录，文件播完即删；启动时 `cleanup_cache()` 兜底清理残留
