"""
AI 对话客户端 — DeepSeek API（OpenAI 兼容格式）

职责：把用户消息发给 DeepSeek，拿回 AI 回复文本。

使用方式：
    from core.ai_client import call_ai
    reply = call_ai("你好")
"""

import logging
from pathlib import Path
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
    "每次回复控制在 2-5 句话。"
)

# 额外上下文（从 core/reference.md 加载，持久化参考资料）
_extra_context = ""
_REFERENCE_FILE = Path(__file__).resolve().parent / "reference.md"

# 人设（从 core/persona.md 加载，不存在则用默认 _SYSTEM_PROMPT）
_persona = ""
_PERSONA_FILE = Path(__file__).resolve().parent / "persona.md"


def load_reference():
    """从文件加载参考资料到上下文"""
    global _extra_context
    try:
        if _REFERENCE_FILE.exists():
            _extra_context = _REFERENCE_FILE.read_text(encoding="utf-8")
            _log.info("参考资料已加载: %d 字", len(_extra_context))
    except Exception as e:
        _log.warning("加载参考资料失败: %s", e)


def save_reference(content: str):
    """保存参考资料到文件并更新上下文"""
    global _extra_context
    try:
        _REFERENCE_FILE.write_text(content, encoding="utf-8")
        _extra_context = content
        _log.info("参考资料已保存: %d 字", len(content))
    except Exception as e:
        _log.error("保存参考资料失败: %s", e)


def get_reference() -> str:
    """返回当前参考资料内容"""
    return _extra_context


def load_persona():
    """从文件加载人设，不存在则用默认"""
    global _persona
    try:
        if _PERSONA_FILE.exists():
            content = _PERSONA_FILE.read_text(encoding="utf-8").strip()
            if content:
                _persona = content
                _log.info("人设已从文件加载: %d 字", len(content))
                return
    except Exception as e:
        _log.warning("加载人设文件失败: %s", e)
    _persona = ""  # 回退到默认 _SYSTEM_PROMPT


def save_persona(content: str):
    """保存人设到文件"""
    global _persona
    try:
        _PERSONA_FILE.write_text(content, encoding="utf-8")
        _persona = content.strip()
        _log.info("人设已保存: %d 字", len(content))
    except Exception as e:
        _log.error("保存人设失败: %s", e)


def get_persona() -> str:
    """返回当前人设"""
    return _persona


# 模块导入时自动加载
load_reference()
load_persona()


# ═══════════════════════════════════════════════════════════════
# ③ 核心函数 — 发消息，拿回复
# ═══════════════════════════════════════════════════════════════

_history = []                    # 对话历史：[{role, content}, ...]
_MAX_HISTORY_MSGS = 20           # 最多保留 20 条（10 轮对话）


def clear_history():
    """清空对话历史（新对话）"""
    global _history
    _history = []


def get_history():
    """返回当前对话历史（供前端展示）"""
    return list(_history)  # 返回副本，防止外部修改


def undo_last_round():
    """回退最后一轮对话（删除最后一条 user + assistant）"""
    global _history
    if len(_history) >= 2:
        _history = _history[:-2]
    elif _history:
        _history = []


def summarize_history() -> str:
    """用 AI 压缩旧历史为一段摘要，保留最近轮次不变。返回提示信息。"""
    global _history
    if len(_history) < 6:
        return "对话太短（少于 3 轮），无需压缩"

    # 取前一半旧消息让 AI 总结
    mid = len(_history) // 2
    old = _history[:mid]
    recent = _history[mid:]

    # 构造总结请求（不发给人设，直接问）
    conv_text = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Robot'}: {m['content']}"
        for m in old
    )

    # 检测是否含文件块 → 附加"大幅压缩文件"指令
    file_hint = ""
    if "[文件:" in conv_text:
        file_hint = (
            "\n\n注意：对话中可能包含 [文件: ...] 到 [/文件] 的文件内容。"
            "对每个文件块，只需概括其主题或关键事实，"
            "不要保留文件的具体内容细节，以最大限度压缩长度。"
        )

    summary_prompt = (
        f"请用 一段文字 概括以下对话的要点，只提取关键信息（人名、偏好、事实等）："
        f"{file_hint}\n\n{conv_text}"
    )

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3,     # 低温 = 更精准
            max_tokens=200,
        )
        summary = resp.choices[0].message.content
        if not summary:
            return "[错误] 摘要生成失败"

        # 用摘要替换旧消息（伪装成 system 消息）
        _history = [
            {"role": "system", "content": f"[对话摘要] {summary.strip()}"}
        ] + recent

        _log.info("历史已压缩: %d 条 → 1 条摘要 + %d 条最近", len(old), len(recent))
        return f"已压缩 {len(old)} 条为摘要（保留最近 {len(recent)} 条）"

    except Exception as e:
        _log.error("摘要生成失败: %s", e)
        return f"[错误] 摘要失败: {e}"  # 只有一条，全部清空

def call_ai(user_message: str) -> str:
    """
    调用 DeepSeek API，获取 AI 回复。

    参数:
        user_message: 用户在聊天框输入的消息（纯文本）

    返回:
        AI 的回复文本。出错时返回以 "[错误]" 开头的字符串。
    """
    if not user_message.strip():
        return "你好像什么都没说呢～ "

    global _history

    try:
        client = _get_client()

        # ★ 核心：messages = 人设 + 参考资料 + 历史 + 当前消息
        persona_text = _persona if _persona else _SYSTEM_PROMPT
        messages = [{"role": "system", "content": persona_text}]
        if _extra_context.strip():
            messages.append({"role": "system", "content": f"参考资料：\n{_extra_context}"})
        messages.extend(_history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=config.LLM_MODEL,            # "deepseek-chat"
            messages=messages,
            temperature=0.8,   # 0=严谨  1=创意  0.8=活泼但不乱说
            max_tokens=600,    # 限制回复最大长度
        )

        # ★ 提取回复文本：choices[0].message.content
        content = response.choices[0].message.content
        if content is None:
            return "[错误] AI 返回了空内容"

        # 保存到历史（限制总条数，超出自动裁旧）
        _history.append({"role": "user", "content": user_message})
        _history.append({"role": "assistant", "content": content})
        if len(_history) > _MAX_HISTORY_MSGS:
            _history = _history[-_MAX_HISTORY_MSGS:]

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

# ═══════════════════════════════════════════════════════════════
# ⑤ 异步接口 — 后台线程 + 队列 → 不阻塞主线程
# ═══════════════════════════════════════════════════════════════

import queue
import threading

_reply_queue: queue.Queue = queue.Queue()
_cancel_flag = False


def call_ai_async(text: str):
    """后台线程调用 AI，不阻塞。结果通过 get_ai_reply() 获取。"""
    global _cancel_flag
    _cancel_flag = False

    def _worker():
        result = call_ai(text)
        _reply_queue.put(result)
    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def get_ai_reply() -> Optional[str]:
    """非阻塞获取 AI 回复。无结果返回 None。已取消返回 "[已取消]"。"""
    global _cancel_flag
    if _cancel_flag:
        _cancel_flag = False
        # 清空队列中可能存在的旧结果
        try:
            while True:
                _reply_queue.get_nowait()
        except queue.Empty:
            pass
        return "[已取消]"
    try:
        return _reply_queue.get_nowait()
    except queue.Empty:
        return None


def cancel_ai():
    """设置取消标志，下次 get_ai_reply() 将返回 "[已取消]"."""
    global _cancel_flag
    _cancel_flag = True


__all__ = ["call_ai", "call_coze", "call_ai_async", "get_ai_reply", "cancel_ai",
           "clear_history", "get_history", "undo_last_round", "summarize_history",
           "get_reference", "save_reference", "get_persona", "save_persona"]

