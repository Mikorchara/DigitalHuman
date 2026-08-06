# 🎭 数字人聊天面板 — Digital Human Chat

> 桌面数字人聊天应用：左侧聊天面板 + 右侧 Live2D 虚拟形象，支持 AI 对话和语音合成。

![技术栈](https://img.shields.io/badge/Python-3.11+-blue) ![UI](https://img.shields.io/badge/UI-PySide6-green) ![Live2D](https://img.shields.io/badge/Live2D-Cubism_SDK_5-orange) ![TTS](https://img.shields.io/badge/TTS-edge--tts-purple)

---

## 🚀 快速启动

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 2. 设置工作目录
$env:PYTHONPATH = "."

# 3. 启动
python main.py
```

> 或直接复制以下整行到 PowerShell：
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned ; d:\digital_human\.venv\Scripts\Activate.ps1 ; $env:PYTHONPATH="." ; python d:\digital_human\main.py
> ```

---

## 🏗️ 架构概览

```
┌──────────────────────────────────────────────┐
│               PySide6 桌面窗口                 │
│  ┌────────────────┐  ┌────────────────────┐  │
│  │  左侧：聊天面板  │  │  右侧：Live2D 形象  │  │
│  │  (HTML/CSS/JS) │  │  (WebGL Canvas)    │  │
│  └───────┬────────┘  └─────────┬──────────┘  │
│          │   QWebChannel 桥接   │              │
│          └──────────┬──────────┘              │
│                     ▼                         │
│            Python 后端逻辑层                    │
│  ┌──────────┬───────────┬────────────────┐   │
│  │DeepSeek  │ edge-tts  │ pygame 音频播放 │   │
│  │  API     │ 语音合成   │ + 口型同步      │   │
│  └──────────┴───────────┴────────────────┘   │
└──────────────────────────────────────────────┘
```

### 用户消息处理流水线

```
输入 "你好"
  → call_ai_async("你好")         后台线程调用 AI
  → QTimer 轮询 get_ai_reply()    获取回复
  → 前端显示回复 + 解锁输入框
  → synthesize_async(reply)       后台合成 MP3
  → play_file(path)               pygame 播放音频
  → startSpeechLipSync(...)       Live2D 口型同步
```

---

## 📁 目录结构

```
digital_human/
├── main.py              程序入口
├── requirements.txt     依赖清单
├── core/                核心逻辑
│   ├── ai_client.py     AI 对话接口
│   └── tts_engine.py    TTS + 音频播放
├── ui/                  PySide6 UI
│   ├── main_window.py   主窗口 + 消息处理
│   ├── bridge.py        Python↔JS 桥接
│   └── http_server.py   内建 HTTP 服务
├── web/                 前端（HTTP 根目录）
│   ├── index.html       聊天 UI + Live2D 容器
│   ├── app.js           前端逻辑
│   ├── style.css        Win7 Aero 主题
│   └── sdk_dist/        Live2D 编译产物
├── z_dous/              📚 开发文档
│   ├── troubleshooting.md   已知坑
│   ├── deep-dive/           深入资料
│   └── patches/             修改记录
└── CubismSdkForWeb-5-r.5/  Live2D SDK 源码
```

---

## 🛠️ 技术栈

| 层 | 技术 |
|----|------|
| 桌面框架 | PySide6 + QWebEngineView |
| Live2D | Cubism SDK 5 for Web |
| AI 对话 | DeepSeek API |
| 语音合成 | edge-tts (Azure TTS) |
| 音频播放 | pygame |
| 前端 | 原生 HTML/CSS/JS |

---

## 📚 文档导航

| 你想… | 看这个 |
|--------|--------|
| 快速了解项目 | 👈 本页 |
| 修改代码（给 AI） | [`AGENTS.md`](AGENTS.md) |
| 遇到 bug | [`z_dous/troubleshooting.md`](z_dous/troubleshooting.md) |
| 了解架构细节 | [`z_dous/deep-dive/architecture.md`](z_dous/deep-dive/architecture.md) |
| 了解 Live2D 内部 | [`z_dous/deep-dive/live2d-internals.md`](z_dous/deep-dive/live2d-internals.md) |
| 接入新 AI | [`z_dous/ai_interface_guide.md`](z_dous/ai_interface_guide.md) |
| 功能演进历史 | [`z_dous/日志.md`](z_dous/日志.md) |

---

## 📄 许可

教育/个人项目，Live2D 模型版权归原版权方所有。
