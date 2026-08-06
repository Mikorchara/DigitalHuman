# ===== after: core/ai_client.py, section ⑤（加取消标志）=====

_reply_queue: queue.Queue = queue.Queue()
_cancel_flag = False

def call_ai_async(text: str):
    global _cancel_flag
    _cancel_flag = False
    def _worker():
        result = call_ai(text)
        _reply_queue.put(result)
    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def get_ai_reply() -> Optional[str]:
    global _cancel_flag
    if _cancel_flag:
        _cancel_flag = False
        try:
            while True: _reply_queue.get_nowait()
        except queue.Empty: pass
        return "[已取消]"
    try:
        return _reply_queue.get_nowait()
    except queue.Empty:
        return None

def cancel_ai():
    global _cancel_flag
    _cancel_flag = True