# ===== before: ui/main_window.py, _setup_bridge 方法 =====

    def _setup_bridge(self):
        channel = QWebChannel(self)
        channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(channel)
        self.webview.loadFinished.connect(self._on_load_finished)
        self.bridge.message_received.connect(self._on_user_message)