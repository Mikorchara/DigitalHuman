"""数字人主窗口 —— 聊天面板 + Live2D 形象"""
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWebEngineCore import QWebEnginePage

from ui.bridge import Bridge
from ui.http_server import start_server
from core.tts_engine import cleanup_cache, synthesize_async, get_ready, play_file
import config


class Live2DPage(QWebEnginePage):
    """拦截 JS console 消息打印到 Python 终端"""

    # 已知无意义的 SDK 刷屏警告，直接静默
    _FILTER = (
        "Shader program is not initialized",
        "Cannot read properties of null",
    )

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 过滤 SDK 刷屏警告
        for keyword in self._FILTER:
            if keyword in message:
                return
        prefix = {0: "🌐", 1: "⚠️", 2: "❌"}.get(level, "  ")
        src = os.path.basename(sourceID) if sourceID else "?"
        print(f"{prefix} [JS:{src}:{lineNumber}] {message}")


class MainWindow(QMainWindow):
    """聊天面板 + 数字人形象的桌面窗口"""

    TITLE = " guide "
    DEFAULT_SIZE = (960, 640)
    MIN_SIZE = (640, 440)

    def __init__(self):
        super().__init__()

        # 启动时自动清理过期 TTS 缓存（默认 >1 天的文件）
        cleanup_cache()

        self.bridge = Bridge(self)
        self.webview: QWebEngineView | None = None

        # TTS 轮询状态（#20 类型注解）
        self._tts_timer: QTimer | None = None
        self._tts_pending: str = ""
        self._tts_timeout_id: int | None = None
        self._ai_timer: QTimer | None = None  # AI 轮询计时器（取消用）

        self._setup_ui()
        self._setup_bridge()

    # ------------------------------------------------------------------
    #  UI 搭建
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle(self.TITLE)
        self.resize(*self.DEFAULT_SIZE)
        self.setMinimumSize(*self.MIN_SIZE)

        # 居中显示
        screen = self.screen().availableGeometry()
        self.move(
            (screen.width() - self.DEFAULT_SIZE[0]) // 2,
            (screen.height() - self.DEFAULT_SIZE[1]) // 2,
        )

        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        # ★ 关键：阻止 Qt 在 Chromium 渲染之前画白色背景
        # Chromium compositor 延迟/失败时（如右键任务栏），Qt 先清空 widget 为白色
        # → WA_OpaquePaintEvent 告诉 Qt「我会画满整个区域，别先清空」
        self.webview.setAttribute(Qt.WA_OpaquePaintEvent, True)
        # 同时把调色板底色设为与页面渐变接近的颜色
        pal = self.webview.palette()
        pal.setColor(QPalette.Window, QColor("#c8d8e8"))
        self.webview.setPalette(pal)
        self.webview.setAutoFillBackground(True)

        # 使用自定义 Page 捕获 JS 错误到 Python 终端
        page = Live2DPage(self)
        # ★ 关键：设置页面背景色与 body 一致，消除 Chromium 合成间隙的白色闪烁
        #    QWebEngineView 默认白色背景在 WebGL 每帧合成时短暂露出 → 闪白
        page.setBackgroundColor(QColor("#c8d8e8"))
        self.webview.setPage(page)

        # 允许本地文件 fetch（Live2D 模型由 JS 动态加载）
        settings = self.webview.page().settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(settings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # 启动 HTTP 服务器
        web_dir = str(Path(__file__).resolve().parent.parent / "web")
        self._http_port = start_server(web_dir, port=0)

        # 加载整合页面（聊天面板 + Live2D canvas）
        url = QUrl(f"http://127.0.0.1:{self._http_port}/index.html")
        print(f"[MAIN] {url.toString()}")
        self.webview.setUrl(url)

    def _resolve_web_path(self, filename: str) -> Path:
        """解析 web/ 目录下的资源路径，兼容开发 & PyInstaller 打包"""
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent.parent  # digital_human/
        return base / "web" / filename

    # ------------------------------------------------------------------
    #  QWebChannel 桥接
    # ------------------------------------------------------------------

    def _setup_bridge(self):
        """注册 bridge 对象，同时把 JS 回调方法注入页面"""

        channel = QWebChannel(self)
        channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(channel)

        # 页面加载完成后注入回调列表，确保 qwebchannel.js 已就绪
        self.webview.loadFinished.connect(self._on_load_finished)

        # 桥接：用户消息 → 简单回显（后续接入 AI）
        self.bridge.message_received.connect(self._on_user_message)
        self.bridge.cancel_requested.connect(self._on_cancel)
        self.bridge.tts_toggled.connect(self._on_tts_toggle)
        self.bridge.history_requested.connect(self._on_history_requested)
        self.bridge.history_undo.connect(self._on_history_undo)
        self.bridge.history_clear.connect(self._on_history_clear)
        self.bridge.history_summarize.connect(self._on_history_summarize)
        self.bridge.reference_requested.connect(self._on_reference_requested)
        self.bridge.reference_save.connect(self._on_reference_save)
        self.bridge.persona_requested.connect(self._on_persona_requested)
        self.bridge.persona_save.connect(self._on_persona_save)
        self.bridge.file_requested.connect(self._on_file_requested)

    def _on_load_finished(self, ok: bool):
        if not ok:
            print("[ERROR] 页面加载失败")
            return
        print("[OK] 页面加载完成，桥接就绪")

        # 停用自动待机循环 → 角色保持初始姿态不动
        QTimer.singleShot(1500, lambda: self.set_live2d_auto_idle(False))
        # 推送 TTS 初始状态给前端
        QTimer.singleShot(1200, lambda: self.send_to_web("setTTSState", config.TTS_ENABLED))

        # 延迟执行诊断 JS（确保所有脚本执行完毕）
        QTimer.singleShot(1000, self._run_diagnostics)

    def _run_diagnostics(self):
        """注入诊断代码检查 JS 环境"""
        self.webview.page().runJavaScript("""
            (function() {
                var msgs = [];
                msgs.push('bridge=' + typeof bridge);
                
                var panel = document.getElementById('live2d-panel');
                if (panel) {
                    var c = panel.querySelector('canvas');
                    msgs.push('canvas=' + (c ? c.width + 'x' + c.height : 'none'));
                }
                
                return msgs.join(' | ');
            })()
        """, lambda result: print(f"[诊断] {result}"))

    # ------------------------------------------------------------------
    #  消息处理
    # ------------------------------------------------------------------

    def _on_user_message(self, text: str):
        """用户发送消息 → AI 回复（后台线程）→ TTS 播放 + 口型同步"""
        from core.ai_client import call_ai_async, get_ai_reply, cancel_ai

        # 取消旧任务
        cancel_ai()

        # 1. 后台线程调用 AI（立即返回，不阻塞 UI）
        call_ai_async(text)

        # 2. QTimer 轮询 AI 结果
        _ai_timer = QTimer(self)
        self._ai_timer = _ai_timer  # 保存引用，供 _on_cancel 使用

        def on_ai_ready():
            reply = get_ai_reply()
            if reply is None:
                return
            _ai_timer.stop()
            self._ai_timer = None

            # 取消的内容不触发 TTS
            if reply == "[已取消]":
                self.send_to_web("enableInput")
                return

            print(f"[AI] 回复长度: {len(reply)} 字")
            self.send_to_web("addMessage", {"role": "assistant", "content": reply})
            self.send_to_web("enableInput")

            # 3. TTS 流水线（开关控制）
            if not config.TTS_ENABLED:
                return

            from core.tts_engine import stop as tts_stop
            tts_stop()
            synthesize_async(reply, voice="xiaoxiao")
            self._tts_pending = reply
            _tts_timer = QTimer(self)

            def on_tts_ready():
                result = get_ready()
                if result is None:
                    return
                filepath, duration_sec = result
                play_file(filepath)
                dur_ms = int(duration_sec * 1000)
                print(f"[TTS] 音频时长 {duration_sec:.1f}s, 启动口型 {dur_ms}ms")
                self.send_to_web("startSpeechLipSync", {"text": self._tts_pending, "durMs": dur_ms})
                _tts_timer.stop()

            _tts_timer.timeout.connect(on_tts_ready)
            _tts_timer.start(200)

        _ai_timer.timeout.connect(on_ai_ready)
        _ai_timer.start(200)

    def _on_cancel(self):
        """用户点击取消按钮 → 终止 AI 等待"""
        from core.ai_client import cancel_ai
        cancel_ai()
        if self._ai_timer:
            self._ai_timer.stop()
            self._ai_timer = None
        self.send_to_web("enableInput")

    def _on_tts_toggle(self):
        """用户点击语音开关"""
        config.TTS_ENABLED = not config.TTS_ENABLED
        state = "开启" if config.TTS_ENABLED else "关闭"
        print(f"[TTS] 语音已{state}")
        self.send_to_web("setTTSState", config.TTS_ENABLED)

    def _on_history_requested(self):
        """前端请求历史数据"""
        from core.ai_client import get_history
        self.send_to_web("showHistory", get_history())

    def _on_history_undo(self):
        """回退最后一轮对话"""
        from core.ai_client import undo_last_round, get_history
        undo_last_round()
        self.send_to_web("showHistory", get_history())

    def _on_history_clear(self):
        """清空全部上下文"""
        from core.ai_client import clear_history, get_history
        clear_history()
        self.send_to_web("showHistory", get_history())

    def _on_history_summarize(self):
        """压缩对话历史为摘要"""
        from core.ai_client import summarize_history, get_history
        result = summarize_history()
        print(f"[历史] {result}")
        self.send_to_web("showHistory", get_history())
        self.send_to_web("addMessage", {"role": "assistant", "content": f"📝 {result}"})

    def _on_reference_requested(self):
        """前端请求参考资料"""
        from core.ai_client import get_reference
        self.send_to_web("showReference", get_reference())

    def _on_reference_save(self, content: str):
        """前端保存参考资料"""
        from core.ai_client import save_reference
        save_reference(content)
        self.send_to_web("addMessage", {"role": "assistant", "content": "📝 参考资料已更新"})

    def _on_persona_requested(self):
        """前端请求人设"""
        from core.ai_client import get_persona
        persona = get_persona()
        # 如果人设为空，返回默认 _SYSTEM_PROMPT 给前端展示
        self.send_to_web("showPersona", persona)

    def _on_persona_save(self, content: str):
        """前端保存人设"""
        from core.ai_client import save_persona
        save_persona(content)
        self.send_to_web("addMessage", {"role": "assistant", "content": "🎭 人设已更新"})

    def _on_file_requested(self, path: str):
        """前端请求读取文件 → 验证 → 返回内容或错误"""
        from pathlib import Path
        p = Path(path)

        # ① 扩展名白名单
        _TEXT_EXTS = {".txt", ".md", ".py", ".json", ".csv", ".log",
                      ".html", ".css", ".js", ".xml", ".yaml", ".yml",
                      ".ini", ".cfg", ".toml", ".rst", ".tex", ".java",
                      ".c", ".cpp", ".h", ".ts", ".sh", ".bat", ".ps1"}

        if p.suffix.lower() not in _TEXT_EXTS:
            self.send_to_web("fileError",
                f"不支持的文件类型: {p.suffix}（仅限纯文本文件）")
            return

        # ② 存在性 + 可访问性
        if not p.exists():
            self.send_to_web("fileError", f"文件不存在: {path}")
            return
        if not p.is_file():
            self.send_to_web("fileError", f"不是文件: {path}")
            return

        # ③ 内容检查（防止伪装的二进制文件）
        try:
            raw = p.read_bytes()
            if b"\x00" in raw[:8192]:  # 扩大到 8KB
                self.send_to_web("fileError", "不是纯文本文件（含二进制内容）")
                return
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            self.send_to_web("fileError", "文件编码不支持（需要 UTF-8）")
            return
        except PermissionError:
            self.send_to_web("fileError", "没有读取权限")
            return

        print(f"[文件] 已加载: {p.name} ({len(text)} 字)")
        self.send_to_web("fileContent", {"name": p.name, "text": text})

    def _start_lip_sync(self, text: str):
        """模拟说话口型：根据文本长度计算节奏（已弃用，保留兼容）"""
        dur = max(2000, min(len(text) * 200, 8000))
        self.send_to_web("startSpeechLipSync", {"text": text, "durMs": dur})

    # ------------------------------------------------------------------
    #  Python → Web 工具方法
    # ------------------------------------------------------------------

    def send_to_web(self, function: str, arg=None):
        """安全地向 Web 页面发送 JS 调用"""
        import json

        if arg is None:
            code = f"{function}()"
        elif isinstance(arg, str):
            escaped = json.dumps(arg)
            code = f"{function}({escaped})"
        else:
            code = f"{function}({json.dumps(arg)})"

        self.webview.page().runJavaScript(code)

    # --- Live2D 控制 API ---

    def set_live2d_expression(self, expr_id: str):
        """切换 Live2D 表情"""
        self.send_to_web("setExpression", expr_id)

    def set_live2d_parameter(self, param_id: str, value: float):
        """设置 Live2D 参数（0.0 ~ 1.0）"""
        self.send_to_web("setParameter", {"id": param_id, "value": value})

    def play_live2d_motion(self, group: str, no: int = 0):
        """播放 Live2D 动作"""
        self.send_to_web("playMotion", {"group": group, "no": no})

    def set_live2d_auto_idle(self, enabled: bool):
        """开关键自动待机动作"""
        self.send_to_web("setAutoIdle", enabled)

    # ------------------------------------------------------------------
    #  窗口事件
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        """关闭窗口时清理 WebView"""
        if self.webview:
            self.webview.page().deleteLater()
            self.webview.deleteLater()
        event.accept()
