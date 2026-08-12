# 位置: core/tts_engine.py, _synth_worker() / speak()

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
