# ===== after: core/tts_engine.py, play_file 函数 =====

def play_file(filepath: str):
    """播放已合成的音频文件（自动停止旧音频，防止重叠）"""
    _audio.stop()
    _audio.play(filepath)