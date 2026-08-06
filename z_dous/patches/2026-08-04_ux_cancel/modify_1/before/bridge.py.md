# ===== before: ui/bridge.py, 全文 =====

class Bridge(QObject):
    message_received = Signal(str)
    expression_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def send_message(self, text: str):
        text = text.strip()
        if text:
            logger.info(f"[用户] {text}")
            self.message_received.emit(text)