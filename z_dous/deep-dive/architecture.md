# 架构说明 — 数字人聊天面板

> 面向需要深入理解系统的开发者。

---

## 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                     main.py (QApplication)                │
│                          │                                │
│                    MainWindow (PySide6)                   │
│  ┌───────────────────────┼──────────────────────────┐    │
│  │              QWebEngineView (Chromium)            │    │
│  │  ┌──────────────┐  QWebChannel  ┌──────────────┐ │    │
│  │  │ index.html   │◄─────────────►│ bridge.py    │ │    │
│  │  │  ┌────────┐  │               │  (QObject)   │ │    │
│  │  │  │app.js  │  │               └──────┬───────┘ │    │
│  │  │  └───┬────┘  │                      │         │    │
│  │  │      │       │               main_window.py   │    │
│  │  │  ┌───┴────┐  │                 │    │         │    │
│  │  │  │Live2D  │  │           ┌─────┘    └─────┐   │    │
│  │  │  │SDK dist│  │    ai_client.py    tts_engine.py │    │
│  │  │  └────────┘  │    (DeepSeek API)  (edge-tts)    │    │
│  │  └──────────────┘                                 │    │
│  └───────────────────────────────────────────────────┘    │
│                                                           │
│  http_server.py (127.0.0.1:随机端口)                       │
│  └── 提供 web/ 目录静态文件 (CORS)                         │
└──────────────────────────────────────────────────────────┘
```

---

## 数据流

### 1. 启动流程

```
main.py
  → QApplication 初始化
  → MainWindow.__init__()
    → cleanup_cache()            清理 TTS 缓存
    → _setup_ui()
      → Live2DPage               自定义 JS 诊断
      → http_server.start_server 启动 CORS HTTP 服务
      → webview.load(url)        加载 http://127.0.0.1:{port}/index.html
    → _setup_bridge()
      → QWebChannel 注册 bridge
      → loadFinished → 诊断 JS → setAutoIdle(false)
```

### 2. 页面加载流程

```
index.html
  ├─ <script src="qwebchannel.js">      Qt 内置
  ├─ <script src="live2dcubismcore.min.js">  Cubism Core
  ├─ <script type="module" src="assets/..."> 编译后的 Framework
  ├─ <script src="app.js">             应用逻辑
  │   ├─ new QWebChannel(...)          建立 Python↔JS 桥
  │   ├─ MutationObserver              捕获 SDK 动态 canvas
  │   └─ 兜底轮询(3s)                   确保 canvas 迁移
  └─ SDK 自动: 加载 Haru 模型 → 创建 canvas → 开始渲染
```

### 3. 用户消息处理（核心）

```
用户在聊天框输入 → Enter
  └─ app.js sendMsg()
      └─ bridge.send_message(text)          Web → Python (QWebChannel)
          └─ MainWindow._on_user_message(text)
              │
              ├─ ① call_ai_async(text)                后台线程 → DeepSeek API
              │    └─ QTimer 轮询 get_ai_reply()
              │
              ├─ ② send_to_web("addMessage", ...)     显示回复 + 解锁输入
              │
              ├─ ③ synthesize_async(reply)             后台线程（TTS 开关控制）
              │    └─ edge_tts.Communicate.save()      合成 MP3 → tts_cache/
              │    └─ queue.Queue.put(path, duration)  入队结果
              │
              ├─ ④ QTimer(200ms) 轮询 get_ready()     主线程
              │    └─ 拿到 (path, duration_sec)
              │       ├─ play_file(path)               pygame 播放
              │       └─ send_to_web("startSpeechLipSync", ...)
              │           └─ app.js → window.Live2D.startSpeechLipSync()
              │               └─ lappmodel.ts 每帧覆盖嘴参数
              │
              └─ ⑤ 口型结束 → stopLipSync → 嘴复位
```

---

## 模块职责

### Python 层

| 文件 | 类/函数 | 职责 |
|------|---------|------|
| `main.py` | `main()` | 入口：创建 QApplication + MainWindow |
| `ui/main_window.py` | `MainWindow` | 窗口管理、消息流水线编排 |
| `ui/main_window.py` | `Live2DPage` | JS console 消息拦截 + 过滤 |
| `ui/bridge.py` | `Bridge` | QWebChannel 双向通信 |
| `ui/http_server.py` | `start_server()` | CORS HTTP 静态文件服务 |
| `core/ai_client.py` | `call_ai()` / `call_ai_async()` | DeepSeek API 调用（同步 + 异步） |
| `core/tts_engine.py` | `synthesize_async()` | 后台 TTS 合成 |
| `core/tts_engine.py` | `get_ready()` / `play_file()` | 结果轮询 + 播放 |

### Web 层

| 文件 | 关键逻辑 |
|------|----------|
| `index.html` | 布局：`#chat-panel`(左 56%) + `#live2d-panel`(右 44%) |
| `app.js` | 桥接初始化、canvas 迁移、消息收发、Live2D 控制桩 |
| `style.css` | Win7 Aero 主题（灰蓝渐变 + 立体边框） |

### Live2D SDK（编译产物）

| 来源 | 产物 | 加载方式 |
|------|------|----------|
| `Core/live2dcubismcore.min.js` | Cubism Core | `<script>` 直接引入 |
| `Demo/src/*.ts` → `npm run build` | Framework JS | `<script type="module">` |
| `Resources/Haru/` | 模型文件 | SDK 运行时 fetch |

---

## SDK 编译部署

```powershell
# 1. 修改 TypeScript 源码
#    CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/

# 2. 编译
cd CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo
npm run build

# 3. 部署
Remove-Item web\sdk_dist\assets\* -Force
Copy-Item dist\assets\* web\sdk_dist\assets\ -Force
# 更新 index.html 中 <script src="sdk_dist/assets/..."> 文件名
```

### 已修改的 TS 源文件

| 文件 | 改动 |
|------|------|
| `lappmodel.ts` | `_autoIdle=false`、手动 LipSync 标志位 |
| `lappsubdelegate.ts` | 点击坐标改用 `getBoundingClientRect()` |
| `lappview.ts` | 背景精灵 `cover` 式填满 |
| `lappdefine.ts` | `BackImageName` 同步文件名 |
| `main.ts` | `window.Live2D` API、Speech lip sync v4 |

---

## 关键设计决策

| 决策 | 原因 |
|------|------|
| HTTP server 而非 file:// | `file://` 不支持 `../../` 相对路径，SDK 加载模型失败 |
| MutationObserver 迁移 canvas | SDK 在 body 下动态建 canvas，需迁移到右侧面板 |
| QWebChannel 而非 WebSocket | PySide6 原生支持，零配置 |
| AI 后台线程 + QTimer 轮询 | QWebChannel Slot 同步阻塞，必须异步避免 UI 冻结 |
| TTS 后台线程 + QTimer 轮询 | daemon 线程无法用 QTimer，必须主线程轮询 |
| TTS 默认关闭 | 调试效率优先，一键开关控制 |
| 取消按钮复用发送按钮 | 发送/取消互斥，避免新增按钮噪音 |
| 播完即删音频文件 | 无需缓存策略，磁盘自动清理 |
