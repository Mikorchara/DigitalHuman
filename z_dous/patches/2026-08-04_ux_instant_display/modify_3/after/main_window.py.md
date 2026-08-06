# ===== after: ui/main_window.py, _on_user_message 方法 =====

    def _on_user_message(self, text: str):
        """用户发送消息 → AI 回复（后台线程）→ TTS 播放 + 口型同步"""
        from core.ai_client import call_ai_async, get_ai_reply
        self._cancel_pending()

        # 1. 后台线程调用 AI（立即返回，不阻塞 UI）
        call_ai_async(text)

        # 2. QTimer 轮询 AI 结果
        self._ai_pending = text
        _ai_timer = QTimer(self)

        def on_ai_ready():
            reply = get_ai_reply()
            if reply is None:
                return
            _ai_timer.stop()
            print(f"[AI] 回复长度: {len(reply)} 字")
            self.send_to_web("addMessage", {"role": "assistant", "content": reply})
            self.send_to_web("enableInput")
            # 3. TTS 流水线（不变）
            synthesize_async(reply, voice="xiaoxiao")
            ... # TTS QTimer 轮询

        _ai_timer.timeout.connect(on_ai_ready)
        _ai_timer.start(200)