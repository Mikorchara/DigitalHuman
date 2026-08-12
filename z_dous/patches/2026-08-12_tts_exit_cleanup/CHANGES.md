# 修改日期：2026-08-12

## 修改文件
- `core/tts_engine.py` — 移除按天清理的 `cleanup_cache`；`clear_all_cache` 改为清空整个目录 ---  modify_0
- `ui/main_window.py` — 启动不再调 `cleanup_cache`；关闭窗口时清空 tts_cache ---  modify_1
- `z_dous/deep-dive/architecture.md` — 同步更新启动流程/退出清理描述 ---  modify_2

## 修改原因
- 每次运行程序，**最后一个 TTS 音频文件不会被删除**（`play_file` 只删"上一个"，`stop` 只在开始新一轮 TTS 前调用），导致 `tts_cache` 按运行次数累积残留（跑 3 次 → 3 个文件）
- 按时间清理的 `cleanup_cache`（>1 天）是多余的：文件本就是临时产物、播完即删，只需在**程序退出时清空整个 tts_cache** 即可
- 由"启动时按天清理"改为"退出时清空全部"，逻辑更简单、文件夹始终保持干净

## 修改内容
- `core/tts_engine.py`
  - 删除 `cleanup_cache()`（按天清理）及不再使用的 `_CACHE_MAX_AGE_DAYS`、`import time`
  - `clear_all_cache()`：改为遍历 `_CACHE_DIR` 删除**全部文件**（不再只匹配 `tts_*.mp3`），作为退出清理用
- `ui/main_window.py`
  - 顶部 import：`cleanup_cache` → `clear_all_cache`
  - `__init__`：删除启动时的 `cleanup_cache()` 调用
  - `closeEvent`：窗口关闭时调用 `clear_all_cache()` 清空 tts_cache

## 影响范围
- 仅 TTS 临时文件的清理时机与方式；不影响合成/播放流程
- `tts_cache` 目录在程序正常退出后为空；若程序崩溃仍可能有残留（极小概率，可接受）
