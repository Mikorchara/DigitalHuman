# 修改日期：2026-08-12

## 修改文件
- `core/tts_engine.py` — 删除死代码 `speak()` 及仅它使用的 `AudioPlayer.load_and_play()` ---  modify_0

## 修改原因
- `speak()` 标记"兼容旧 API"但**无任何调用方**（code_review #18 / others/code-review #5 均已指出）
- 当前正式流程为 `synthesize_async() → get_ready() → play_file()`，`speak()` 是旧版本遗留的一步式接口
- `AudioPlayer.load_and_play()` 仅被 `speak()` 调用，属连带死代码，一并删除

## 修改内容
- 删除 `AudioPlayer.load_and_play()` 方法（返回时长的播放接口，无调用方）
- 删除 `speak()` 函数及"兼容旧 API"注释块

## 影响范围
- 无：两处均无调用方，不影响现有合成/播放流程
- `main_window.py` 未引用 `speak` / `load_and_play`，无需改动
