# 项目详细结构 — Digital Human Chat

```
digital_human/
├── main.py               # 程序入口：QApplication + MainWindow
├── config.example.py     # 配置模板（密钥占位，提交到 git）
├── config.py             # 本地真实配置（gitignore，不入库）
├── requirements.txt      # Python 依赖
├── README.md             # 项目说明
├── AGENTS.md             # AI 协作规范
│
├── core/                 # 后端核心逻辑
│   ├── __init__.py
│   ├── ai_client.py      # DeepSeek 对话接口（call_ai / call_ai_async）
│   ├── tts_engine.py     # TTS 合成 + 音频播放（edge-tts + pygame）
│   ├── persona.md        # AI 人设（可编辑）
│   └── reference.md      # 参考资料（可编辑，AI 自动引用）
│
├── ui/                   # PySide6 桌面层
│   ├── __init__.py
│   ├── main_window.py    # 主窗口、消息处理流水线
│   ├── bridge.py         # Python ↔ JS 桥接（QWebChannel）
│   └── http_server.py    # 内建 CORS HTTP 服务器
│
├── web/                  # 前端（HTTP 服务器根目录）
│   ├── index.html        # 聊天 UI + Live2D 容器
│   ├── app.js            # 前端逻辑、Live2D API 桥接
│   ├── style.css         # Win7 Aero 主题
│   ├── sdk_dist/         # Live2D 编译产物（Core + assets + Resources）
│   ├── Resources/        # 模型资源（SDK 运行时 fetch）
│   └── Framework/        # Framework 着色器等
│
├── tts_cache/            # TTS 临时音频（播完即删，退出清空）
│
├── z_docs/               # 📚 项目文档
│   ├── ROADMAP.md        # 开发路线图 / 计划
│   ├── troubleshooting.md# 已知问题与踩坑（改前必读）
│   ├── code_review.md    # 代码审查报告（初始空白）
│   ├── BUILD_RUN.md      # 环境配置与运行指南
│   ├── structure.md      # 本文档（详细结构）
│   ├── deep-dive/        # 分模块深入讲解
│   │   ├── architecture.md
│   │   ├── l2d-internals.md
│   │   └── ...（含日志/接口指南等归档）
│   └── patches/          # 补丁记录（YYYY-MM-DD_描述/CHANGES.md + before/after）
│
└── CubismSdkForWeb-5-r.5/  # Live2D SDK 源码（编译用，含源码与模型资源）
    └── Samples/TypeScript/Demo/   # Demo 源码（改后 npm run build）
```

## 数据流向（一次对话）

```
用户输入 → web/app.js → QWebChannel(bridge) → ui/main_window.py
  → core/ai_client.py (DeepSeek) → 回复 → 前端显示
  → core/tts_engine.py (edge-tts 合成 → pygame 播放 → 口型同步)
```
