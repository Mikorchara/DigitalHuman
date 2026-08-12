# 位置: core/tts_engine.py, 顶部 imports / 常量区 / cleanup_cache() / clear_all_cache()

import asyncio
import os
import queue
import threading
import time
import uuid

# ── 项目根目录下的音频缓存 ──────────────────────────────────
_CACHE_DIR = Path(__file__).resolve().parent.parent / "tts_cache"
_CACHE_DIR.mkdir(exist_ok=True)

# 缓存保留天数（超过此天数的文件会在启动时清理）
_CACHE_MAX_AGE_DAYS = 1

# ...（VOICES / AudioPlayer / _delete_file / 队列 / _synthesize / _synth_worker 等略）...

def cleanup_cache(max_age_days: int = _CACHE_MAX_AGE_DAYS) -> int:
    """
    清理过期的 TTS 缓存文件。
    删除超过 max_age_days 天的 .mp3 文件。
    返回删除的文件数。
    """
    if not _CACHE_DIR.exists():
        return 0

    now = time.time()
    max_age_sec = max_age_days * 24 * 3600
    deleted = 0

    for f in _CACHE_DIR.glob("tts_*.mp3"):
        try:
            file_age = now - os.path.getmtime(f)
            if file_age > max_age_sec:
                os.remove(f)
                deleted += 1
        except OSError:
            pass

    if deleted:
        print(f"[TTS] 已清理 {deleted} 个过期缓存文件（>{max_age_days}天）")
    return deleted


def clear_all_cache() -> int:
    """
    清空所有 TTS 缓存文件（立即删除全部 .mp3）。
    返回删除的文件数。
    """
    if not _CACHE_DIR.exists():
        return 0

    deleted = 0
    for f in _CACHE_DIR.glob("tts_*.mp3"):
        try:
            os.remove(f)
            deleted += 1
        except OSError:
            pass

    if deleted:
        print(f"[TTS] 已清空全部 {deleted} 个缓存文件")
    return deleted
