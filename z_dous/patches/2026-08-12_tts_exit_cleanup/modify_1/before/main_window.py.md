# 位置: ui/main_window.py, 顶部 import / __init__ / closeEvent()

from core.tts_engine import cleanup_cache, synthesize_async, get_ready, play_file

    def __init__(self):
        super().__init__()

        # 启动时自动清理过期 TTS 缓存（默认 >1 天的文件）
        cleanup_cache()

        self.bridge = Bridge(self)

    def closeEvent(self, event):
        """关闭窗口时清理 WebView"""
        if self.webview:
            self.webview.page().deleteLater()
            self.webview.deleteLater()
        event.accept()
