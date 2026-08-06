# ===== before: ui/main_window.py, _on_user_message 方法 (L170-210) =====

    def _on_user_message(self, text: str):
        """用户发送消息 → AI 回复 → TTS 播放 + 口型同步（精确时长）"""
        # 1. 调用 AI 获取回复
        from core.ai_client import call_ai
        reply = call_ai(text)
        print(f"[AI] 回复长度: {len(reply)} 字")

        self.send_to_web("addMessage", {"role": "assistant", "content": reply})
        self.send_to_web("enableInput")

        # 取消旧消息的超时单发 + timer
        if self._tts_timeout_id is not None:
            QTimer.singleShot(0, lambda: None)  # noop
            self._tts_timer.stop() if self._tts_timer else None
        self._tts_timeout_id = None

        # 1. 后台合成 MP3
        synthesize_async(reply, voice="xiaoxiao")

        # 2. QTimer 轮询 → 拿到时长后播放音频 + 启动口型