"""TTS 语音合成 + 音频播放引擎"""
import asyncio
import os
import queue
import threading
import uuid
from pathlib import Path
from typing import Optional

import edge_tts
import pygame

# ── 项目根目录下的音频临时目录 ──────────────────────────────
# 音频文件均为临时产物，播完即删；程序退出时清空整个目录
_CACHE_DIR = Path(__file__).resolve().parent.parent / "tts_cache"
_CACHE_DIR.mkdir(exist_ok=True)

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
    """后台线程：合成 MP3 → 读时长 → 存入队列（每次新文件，播完即删）"""
    voice_name = VOICES.get(voice, VOICES["xiaoxiao"])
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = str(_CACHE_DIR / filename)

    asyncio.run(_synthesize(text, voice_name, filepath))

    # 后台线程里初始化 mixer，读取时长
    pygame.mixer.init(frequency=24000, size=-16, channels=1)
    sound = pygame.mixer.Sound(filepath)
    duration = sound.get_length()
    _ready.put((filepath, duration))


# ── 公开 API ────────────────────────────────────────────────

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

