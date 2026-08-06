# ===== after: core/ai_client.py, 末尾新增 section ⑤ =====

# ═══════════════════════════════════════════════════════════════
# ⑤ 异步接口 — 后台线程 + 队列 → 不阻塞主线程
# ═══════════════════════════════════════════════════════════════

import queue
import threading

_reply_queue: queue.Queue = queue.Queue()


def call_ai_async(text: str):
    """后台线程调用 AI，不阻塞。结果通过 get_ai_reply() 获取。"""
    def _worker():
        result = call_ai(text)
        _reply_queue.put(result)
    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def get_ai_reply() -> str | None:
    """非阻塞获取 AI 回复。无结果返回 None。"""
    try:
        return _reply_queue.get_nowait()
    except queue.Empty:
        return None

__all__ = ["call_ai", "call_coze", "call_ai_async", "get_ai_reply"]