# ===== after: ui/bridge.py, 新增信号 + Slot =====

    cancel_requested = Signal()         # 用户点击了取消按钮

    @Slot()
    def cancel(self):
        logger.info("[用户] 取消等待")
        self.cancel_requested.emit()