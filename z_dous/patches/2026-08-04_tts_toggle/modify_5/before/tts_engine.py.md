# ===== before: core/tts_engine.py, play_file + stop 函数 =====

def play_file(filepath: str):
    """播放已合成的音频文件（自动停止旧音频，防止重叠）"""
    _audio.stop()
    _audio.play(filepath)

def stop():
    """停止当前播放"""
    _audio.stop()