# ===== before: core/tts_engine.py, play_file 函数 =====

def play_file(filepath: str):
    """播放已合成的音频文件"""
    _audio.play(filepath)