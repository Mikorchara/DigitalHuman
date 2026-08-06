"""
AI 对话客户端 — DeepSeek API（OpenAI 兼容格式）

职责：把用户消息发给 DeepSeek，拿回 AI 回复文本。
不关心 UI 显示、TTS 播放——只做一件事：跟 AI 服务器通信。

使用方式：
    from core.ai_client import call_ai
    reply = call_ai("你好")
"""

import logging
from typing import Optional

from openai import OpenAI

import config

_log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# ① 客户端 — 延迟初始化（首次调用时才创建连接）
# ═══════════════════════════════════════════════════════════════

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """获取或创建 OpenAI 客户端（懒加载，避免导入时就连接）"""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=config.LLM_BASE_URL,   # "https://api.deepseek.com/v1"
            api_key=config.LLM_API_KEY,      # "sk-..."
        )
        _log.info("AI 客户端已初始化: %s", config.LLM_MODEL)
    return _client


# ═══════════════════════════════════════════════════════════════
# ② 人设 — System Prompt（定义 AI 的角色和语气）
# ═══════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = (
    "你叫 Haru，是一个活泼可爱的桌面虚拟助手。"
    "请用简洁、自然的中文回答，像朋友聊天一样。"
    "可以适当使用表情符号（😊✨👍）。"
    "每次回复控制在 2-5 句话。"
)


# ═══════════════════════════════════════════════════════════════
# ③ 核心函数 — 发消息，拿回复
# ═══════════════════════════════════════════════════════════════

def call_ai(user_message: str) -> str:
    """
    调用 DeepSeek API，获取 AI 回复。

    参数:
        user_message: 用户在聊天框输入的消息（纯文本）

    返回:
        AI 的回复文本。出错时返回以 "[错误]" 开头的字符串。
    """
    if not user_message.strip():
        return "你好像什么都没说呢～ 😊"

    try:
        client = _get_client()

        # ★ 核心：messages 数组 — AI 看到的"聊天记录"
        #    system = 人设（告诉 AI 它是谁）
        #    user   = 用户刚发的消息
        response = client.chat.completions.create(
            model=config.LLM_MODEL,            # "deepseek-chat"
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.8,   # 0=严谨  1=创意  0.8=活泼但不乱说
            max_tokens=600,    # 限制回复最大长度
        )

        # ★ 提取回复文本：choices[0].message.content
        content = response.choices[0].message.content
        if content is None:
            return "[错误] AI 返回了空内容"

        _log.info("AI 回复: %d 字", len(content))
        return content.strip()

    except Exception as e:
        # ── 分类错误，给用户友好的提示 ──
        _log.error("AI 调用失败: %s", e)
        msg = str(e)

        if "api_key" in msg.lower() or "authentication" in msg.lower():
            return "[错误] API Key 无效，请检查 config.py"
        if "timeout" in msg.lower():
            return "[错误] AI 服务响应超时，请稍后重试"
        if "connection" in msg.lower():
            return "[错误] 无法连接 AI 服务，请检查网络"
        return f"[错误] {msg[:100]}"


# ═══════════════════════════════════════════════════════════════
# ④ 兼容性别名 — 旧代码不用改也能跑
# ═══════════════════════════════════════════════════════════════

call_coze = call_ai   # main_window.py 目前还是 import call_coze

__all__ = ["call_ai", "call_coze"]
