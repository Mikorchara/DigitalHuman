# 位置: z_dous/deep-dive/architecture.md, 启动流程

```
main.py
  → QApplication 初始化
  → MainWindow.__init__()
    → _setup_ui()
      → Live2DPage               自定义 JS 诊断
      → http_server.start_server 启动 CORS HTTP 服务
      → webview.load(url)        加载 http://127.0.0.1:{port}/index.html
    → _setup_bridge()
      → QWebChannel 注册 bridge
      → loadFinished → 诊断 JS → setAutoIdle(false)
  → 退出: closeEvent → clear_all_cache() 清空 tts_cache
```
