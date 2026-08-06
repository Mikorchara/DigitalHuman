# ===== after: ui/main_window.py, L170-177（_on_user_message 方法）=====

    def _on_user_message(self, text: str):
        """用户发送消息 → AI 回复 → TTS 播放 + 口型同步（精确时长）"""
        # 1. 调用 AI 获取回复
        from core.ai_client import call_ai
        reply = call_ai(text)                                      # ← 改动点
        print(f"[AI] 回复长度: {len(reply)} 字")

        self.send_to_web("addMessage", {"role": "assistant", "content": reply})
        # ... 后续 TTS + 口型逻辑不变
