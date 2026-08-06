"""Python ↔ Web 双向通信桥接"""
import json
import logging

from PySide6.QtCore import QObject, Signal, Slot, Property

logger = logging.getLogger(__name__)


class Bridge(QObject):
    """通过 QWebChannel 暴露给 JS 的桥接对象"""

    # Python → Web: 由 Python 调用 JS 函数实现，不需要信号
    # Web → Python: JS 调用 @Slot 方法，内部发射信号让 UI 层处理

    message_received = Signal(str)      # 用户发送了聊天消息
    expression_changed = Signal(str)    # Live2D 表情切换通知
    cancel_requested = Signal()         # 用户点击了取消按钮
    tts_toggled = Signal()              # 用户点击了语音开关
    history_undo = Signal()             # 回退一轮对话
    history_clear = Signal()            # 清空全部历史
    history_summarize = Signal()        # 压缩历史
    reference_requested = Signal()       # 请求参考资料
    reference_save = Signal(str)         # 保存参考资料
    persona_requested = Signal()          # 请求人设
    persona_save = Signal(str)            # 保存人设
    file_requested = Signal(str)          # 请求读取文件（路径）
    history_requested = Signal()        # 请求历史数据

    def __init__(self, parent=None):
        super().__init__(parent)

    # ======================== Web → Python（Slot） ========================

    @Slot(str)
    def send_message(self, text: str):
        """JS 调用：用户发送了聊天消息"""
        text = text.strip()
        if text:
            logger.info(f"[用户] {text}")
            self.message_received.emit(text)

    @Slot(str)
    def notify_expression(self, name: str):
        """JS 调用：Live2D 表情发生了变化"""
        logger.info(f"[表情] {name}")
        self.expression_changed.emit(name)

    @Slot()
    def cancel(self):
        """JS 调用：用户点击取消按钮"""
        logger.info("[用户] 取消等待")
        self.cancel_requested.emit()

    @Slot()
    def toggle_tts(self):
        """JS 调用：用户点击语音开关"""
        logger.info("[用户] 切换语音开关")
        self.tts_toggled.emit()

    @Slot()
    def request_history(self):
        """JS 调用：请求对话历史数据"""
        self.history_requested.emit()

    @Slot()
    def undo_round(self):
        """JS 调用：回退最后一轮对话"""
        self.history_undo.emit()

    @Slot()
    def clear_context(self):
        """JS 调用：清空全部上下文"""
        self.history_clear.emit()

    @Slot()
    def summarize_context(self):
        """JS 调用：压缩对话历史"""
        self.history_summarize.emit()

    @Slot()
    def request_reference(self):
        """JS 调用：请求参考资料内容"""
        self.reference_requested.emit()

    @Slot(str)
    def save_reference(self, content: str):
        """JS 调用：保存参考资料"""
        self.reference_save.emit(content)

    @Slot()
    def request_persona(self):
        """JS 调用：请求人设内容"""
        self.persona_requested.emit()

    @Slot(str)
    def save_persona(self, content: str):
        """JS 调用：保存人设"""
        self.persona_save.emit(content)

    @Slot(str)
    def request_file(self, path: str):
        """JS 调用：请求读取文件"""
        self.file_requested.emit(path.strip())

    @Slot(result=str)
    def get_status(self) -> str:
        """JS 调用：获取当前系统状态"""
        return json.dumps({"ready": True, "model_loaded": False})
