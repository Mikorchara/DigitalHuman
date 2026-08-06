# ===== after: ui/main_window.py, 连接取消 + _on_cancel =====

    self.bridge.cancel_requested.connect(self._on_cancel)

    # __init__ 新增
    self._ai_timer: QTimer | None = None

    def _on_cancel(self):
        from core.ai_client import cancel_ai
        cancel_ai()
        if self._ai_timer:
            self._ai_timer.stop()
            self._ai_timer = None
        self.send_to_web("enableInput")