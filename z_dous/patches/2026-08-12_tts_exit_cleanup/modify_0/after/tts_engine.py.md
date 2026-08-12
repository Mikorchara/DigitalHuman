# 位置: core/tts_engine.py, 顶部 imports / 常量区 / clear_all_cache()

import asyncio
import os
import queue
import threading
import uuid

# ── 项目根目录下的音频临时目录 ──────────────────────────────
# 音频文件均为临时产物，播完即删；程序退出时清空整个目录
_CACHE_DIR = Path(__file__).resolve().parent.parent / "tts_cache"
_CACHE_DIR.mkdir(exist_ok=True)

# ...（VOICES / AudioPlayer / _delete_file / 队列 / _synthesize / _synth_worker 等略）...

def clear_all_cache() -> int:
    """
    清空 tts_cache 目录下所有临时音频文件（程序退出时调用）。
    返回删除的文件数。
    """
    if not _CACHE_DIR.exists():
        return 0

    deleted = 0
    for f in _CACHE_DIR.iterdir():
        try:
            if f.is_file():
                f.unlink()
                deleted += 1
        except OSError:
            pass

    if deleted:
        print(f"[TTS] 已清空 {deleted} 个临时音频文件")
    return deleted
