# ===== after: core/tts_engine.py, play_file + stop + _delete_file =====

_last_file: Optional[str] = None  # 上一个播放的文件，用于自动清理

def _delete_file(filepath: Optional[str]):
    """安全删除文件，不存在或锁定则跳过"""
    if filepath and os.path.exists(filepath):
        try: os.remove(filepath)
        except OSError: pass

def play_file(filepath: str):
    global _last_file
    _audio.stop()
    _delete_file(_last_file)          # 删上一个
    _last_file = filepath
    _audio.play(filepath)

def stop():
    global _last_file
    _audio.stop()
    _delete_file(_last_file)
    _last_file = None