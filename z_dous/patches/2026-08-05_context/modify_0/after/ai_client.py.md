# ===== after: core/ai_client.py, 核心改动 =====

_history = []                    # 对话历史：[{role, content}, ...]
_MAX_HISTORY_MSGS = 20           # 最多保留 20 条（10 轮对话）

def clear_history():
    global _history
    _history = []

# call_ai() 中 messages 改为：
messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
messages.extend(_history)                    # ← 加载历史
messages.append({"role": "user", "content": user_message})

# 回复后保存：
_history.append({"role": "user", "content": user_message})
_history.append({"role": "assistant", "content": content})
if len(_history) > _MAX_HISTORY_MSGS:        # 自动裁旧
    _history = _history[-_MAX_HISTORY_MSGS:]