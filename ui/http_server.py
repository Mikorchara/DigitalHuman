"""内建 HTTP 服务器 —— 解决 file:// 协议下相对路径问题"""
import http.server
import socketserver
import threading


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """添加 CORS 头 + 正确的 MIME 类型"""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".json": "application/json",
        ".wasm": "application/wasm",
        ".moc3": "application/octet-stream",
        ".png": "image/png",
        ".css": "text/css",
        ".html": "text/html",
    }

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # 静默日志（Python 端用 Live2DPage 诊断）


def start_server(directory: str, port: int = 0) -> int:
    """启动 HTTP 服务器，返回实际端口号"""
    handler = lambda *args, **kwargs: CORSHTTPRequestHandler(*args, directory=directory, **kwargs)
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)

    actual_port = httpd.server_address[1]

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    print(f"[HTTP] Server started at http://127.0.0.1:{actual_port} (serving {directory})")
    return actual_port
