# 位置: core/tts_engine.py, AudioPlayer.load_and_play() / 末尾 speak()

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

# ...（_delete_file / 队列 / _synthesize / _synth_worker / 公开 API 等略）...


# ── 兼容旧 API ─────────────────────────────────────────────

def speak(text: str, voice: str = "xiaoxiao", on_ready=None):
    """
    兼容旧 API：合成并播放（非阻塞）。
    """
    voice_name = VOICES.get(voice, VOICES["xiaoxiao"])
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = str(_CACHE_DIR / filename)

    def _work():
        asyncio.run(_synthesize(text, voice_name, filepath))
        duration = _audio.load_and_play(filepath)
        if on_ready:
            on_ready(duration)
    t = threading.Thread(target=_work, daemon=True)
    t.start()
