"""TTS 语音合成 + 音频播放引擎"""
import asyncio
import os
import queue
import threading
import time
from pathlib import Path
from typing import Optional

import edge_tts
import pygame

# ── 项目根目录下的音频缓存 ──────────────────────────────────
_CACHE_DIR = Path(__file__).resolve().parent.parent / "tts_cache"
_CACHE_DIR.mkdir(exist_ok=True)

# 缓存保留天数（超过此天数的文件会在启动时清理）
_CACHE_MAX_AGE_DAYS = 1

# 可选中文语音
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",  # 活泼女声（默认）
    "yunxi":    "zh-CN-YunxiNeural",     # 阳光男声
    "xiaoyi":   "zh-CN-XiaoyiNeural",    # 温柔女声
    "yunjian":  "zh-CN-YunjianNeural",   # 沉稳男声
}


# ── 音频播放器 ──────────────────────────────────────────────

class AudioPlayer:
    """pygame 音频播放封装"""

    def __init__(self):
        self._init = False

    def _ensure_init(self):
        if not self._init:
            pygame.mixer.init(frequency=24000, size=-16, channels=1)
            self._init = True

    def load_and_play(self, filepath: str) -> float:
        """加载并播放音频，返回时长（秒）"""
        self._ensure_init()
        sound = pygame.mixer.Sound(filepath)
        sound.play()
        return sound.get_length()

    def play(self, filepath: str):
        """播放已存在的文件（需在主线程或已 init 的线程）"""
        self._ensure_init()
        sound = pygame.mixer.Sound(filepath)
        sound.play()

    def stop(self):
        """停止播放"""
        try:
            pygame.mixer.stop()
        except Exception:
            pass


_audio = AudioPlayer()
_last_file: Optional[str] = None  # 上一个播放的文件，用于自动清理


def _delete_file(filepath: Optional[str]):
    """安全删除文件，不存在或锁定则跳过"""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass  # 文件被锁定，跳过


# ── 结果队列：worker 线程 → 主线程 ─────────────────────────
_ready = queue.Queue()


async def _synthesize(text: str, voice: str, output_path: str) -> None:
    """使用 edge-tts 合成语音到文件"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def _synth_worker(text: str, voice: str):
    """后台线程：合成 MP3 → 读时长 → 存入队列"""
    voice_name = VOICES.get(voice, VOICES["xiaoxiao"])
    filename = f"tts_{abs(hash(text))}.mp3"
    filepath = str(_CACHE_DIR / filename)

    if not os.path.exists(filepath):
        asyncio.run(_synthesize(text, voice_name, filepath))

    # 后台线程里初始化 mixer，读取时长
    pygame.mixer.init(frequency=24000, size=-16, channels=1)
    sound = pygame.mixer.Sound(filepath)
    duration = sound.get_length()
    _ready.put((filepath, duration))


# ── 公开 API ────────────────────────────────────────────────

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


def synthesize_async(text: str, voice: str = "xiaoxiao"):
    """
    后台合成语音（非阻塞）。
    合成完成后通过 get_ready() 获取 (filepath, duration_sec)。
    """
    t = threading.Thread(
        target=_synth_worker,
        args=(text, voice),
        daemon=True,
    )
    t.start()


def get_ready():
    """
    非阻塞轮询：返回 (filepath, duration_sec) 或 None。
    主线程用 QTimer 定期调用。
    """
    try:
        return _ready.get_nowait()
    except queue.Empty:
        return None


def play_file(filepath: str):
    """播放音频（停旧音频 + 删旧文件 + 播新文件）"""
    global _last_file
    _audio.stop()
    _delete_file(_last_file)          # 删上一个
    _last_file = filepath             # 记新的
    _audio.play(filepath)


def stop():
    """停止当前播放，删除当前文件"""
    global _last_file
    _audio.stop()
    _delete_file(_last_file)
    _last_file = None


# ── 兼容旧 API ─────────────────────────────────────────────

def speak(text: str, voice: str = "xiaoxiao", on_ready=None):
    """
    兼容旧 API：合成并播放（非阻塞）。
    """
    voice_name = VOICES.get(voice, VOICES["xiaoxiao"])
    filename = f"tts_{abs(hash(text))}.mp3"
    filepath = str(_CACHE_DIR / filename)

    if os.path.exists(filepath):
        duration = _audio.load_and_play(filepath)
        if on_ready:
            on_ready(duration)
    else:
        def _work():
            asyncio.run(_synthesize(text, voice_name, filepath))
            duration = _audio.load_and_play(filepath)
            if on_ready:
                on_ready(duration)
        t = threading.Thread(target=_work, daemon=True)
        t.start()

