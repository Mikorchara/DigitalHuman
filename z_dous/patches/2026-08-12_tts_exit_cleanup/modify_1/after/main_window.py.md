# 位置: ui/main_window.py, 顶部 import / __init__ / closeEvent()

from core.tts_engine import clear_all_cache, synthesize_async, get_ready, play_file

    def __init__(self):
        super().__init__()

        self.bridge = Bridge(self)

    def closeEvent(self, event):
        """关闭窗口时清理 WebView + 清空 TTS 临时文件"""
        if self.webview:
            self.webview.page().deleteLater()
            self.webview.deleteLater()
        clear_all_cache()
        event.accept()
