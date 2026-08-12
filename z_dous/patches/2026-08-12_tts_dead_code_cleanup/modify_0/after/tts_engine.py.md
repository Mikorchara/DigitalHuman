# 位置: core/tts_engine.py, AudioPlayer 类（删 load_and_play）/ 文件末尾（删 speak）

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
# 文件在 stop() 后直接结束，无"兼容旧 API"区段
