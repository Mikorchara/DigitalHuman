# AI Instructions — Digital Human Chat

> 本文件是 AI 协作规范，维护此项目时请遵循。

---

## 1. 项目基本信息

| 项 | 内容 |
|----|------|
| 项目名称 | Digital Human Chat（数字人聊天面板） |
| 创建日期 | 2026-08（自 JavaFX 版迁移，已独立开发） |
| 主要技术栈 | Python / PySide6 / QWebEngineView / Live2D Cubism SDK 5 / DeepSeek API / edge-tts |

## 2. 项目目标与范围

- **目标**：桌面数字人聊天应用——左侧聊天面板 + 右侧 Live2D 虚拟形象，支持 AI 对话与语音合成（含口型同步）。
- **范围**：聊天 / AI（DeepSeek）/ TTS / Live2D 控制 / 上下文管理 / 文件输入。

## 3. 关键架构决策记录

| 决策 | 原因 |
|------|------|
| Live2D 使用 SDK Demo dist（不手写渲染器） | 投影矩阵、mask 渲染等无法手写覆盖（核心约束） |
| HTTP server 而非 file:// | SDK 依赖 `../../` 相对路径，file:// 下加载失败 |
| QWebChannel 而非 WebSocket | PySide6 原生支持，零配置 |
| AI/TTS 后台线程 + QTimer 轮询 | 避免 UI 冻结；daemon 线程不能用 QTimer |
| TTS 临时文件"播完即删 + 退出清空" | AI 回复每次不同，缓存无意义；磁盘保持干净 |
| 密钥不入库（config.example.py 模板） | 防密钥泄露，环境变量优先 |

## 4. 环境依赖与配置说明

| 依赖 | 说明 |
|------|------|
| PySide6 | 桌面框架（Essentials + Addons） |
| edge-tts | 在线 TTS（Azure，需网络） |
| pygame | 音频播放（SDL2） |
| openai | DeepSeek API 调用 |

**配置**：真实密钥放本地 `config.py`（gitignore）或用环境变量 `DEEPSEEK_API_KEY`；模板见 `config.example.py`。

## 5. 协作规范与代码风格

- 遵循 PEP 8；类名 PascalCase，函数/变量 snake_case
- 资源文件路径通过 `config`/`resource` 解析，不硬编码
- AI 模块独立于 UI，仅通过信号/回调通信
- 修改前先查阅 `z_docs/troubleshooting.md` 与 `z_docs/code_review.md`
- 修改已有代码前，先在 `z_docs/patches/` 创建补丁记录（见下）
- 出现技术失误时，总结到 `z_docs/troubleshooting.md` 使经验可复用

---

## 6. 修改规范

### 原则

1. **任何对已有代码的修改，必须先备份记录。**
2. **优先新增文件，而非改动已有文件。**
3. **修改最小化** — 只改必要的，不动无关代码。

### 修改记录流程

每次修改已有文件时，按以下步骤操作：

```
z_docs/patches/
└── YYYY-MM-DD_简要描述/
    ├── CHANGES.md          # 修改说明：改了什么、为什么改
    ├── before/             # 修改前的原始文件副本
    │   └── xxx.py
    └── after/              # 修改后的文件副本
        └── xxx.py
```

#### CHANGES.md 模板

```markdown
# 修改日期：YYYY-MM-DD
# 修改人：[姓名]

## 修改文件
- `path/to/file.py`

## 修改原因
[简述为什么要改]

## 修改内容
- 改了 A
- 加了 B

## 影响范围
[哪些功能会受影响]
```

---

## 附录

### 核心命令

```powershell
# 启动
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned ; d:\digital_human\.venv\Scripts\Activate.ps1 ; $env:PYTHONPATH="." ; python d:\digital_human\main.py

# 修改 TypeScript 后重新编译部署
cd CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo; npm run build
# → dist/assets/* 覆盖到 web/sdk_dist/assets/，更新 index.html <script> 引用

# 修改 Python 后清理缓存
Get-ChildItem -Recurse __pycache__ | Remove-Item -Recurse -Force
```

### 关键文件速查

| 文件 | 职责 |
|------|------|
| `main.py` | 程序入口 |
| `ui/main_window.py` | 主窗口、消息处理流水线 |
| `ui/bridge.py` | Python ↔ JS 桥接（QWebChannel） |
| `ui/http_server.py` | CORS HTTP 服务器 |
| `core/ai_client.py` | AI 对话接口（`call_ai` / `call_ai_async`） |
| `core/tts_engine.py` | TTS 合成 + 音频播放 |
| `web/index.html` | 聊天 UI + Live2D 容器 |
| `web/app.js` | 前端逻辑、Live2D API 桥接 |
| `web/style.css` | Win7 Aero 主题 |
| `config.example.py` | 配置模板（真实密钥放本地 `config.py`） |

### Live2D 控制 API

> SDK 源码位于 `CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/`。

| 方法 | 参数 | 说明 |
|------|------|------|
| `playMotion(group, no, pri?)` | 组名,索引,优先级 | 播放指定动作 |
| `playRandomMotion(group, pri?)` | 组名,优先级 | 随机播放组内动作 |
| `setExpression(exprId)` | 表情 ID | 切换表情 |
| `setParameter(paramId, value)` | 参数名,值 | 一次性参数设置 |
| `startSpeechLipSync(text, durMs)` | 回复文本,时长 ms | 节奏式说话口型 |
| `stopLipSync()` | 无 | 立即闭嘴并复位 |
| `setAutoIdle(enabled)` | 布尔 | 切换自动待机循环 |

### Haru 模型关键参数

- 10 个 Idle 动作 + 1 个 TapBody 动作
- 张嘴正确组合：`ParamMouthForm=-2.0` + `ParamMouthOpenY=1.0`
- `_autoIdle=false`（默认关闭自动待机）
- 更多模型细节见 `z_docs/deep-dive/l2d-internals.md`

### 详细参考

- 开发路线图：`z_docs/ROADMAP.md`
- 已知陷阱 / 常见错误：`z_docs/troubleshooting.md`
- 代码审查清单：`z_docs/code_review.md`
- 构建与运行：`z_docs/BUILD_RUN.md`
- 项目结构：`z_docs/structure.md`
- 深入讲解：`z_docs/deep-dive/`
- PySide6 官方文档：https://doc.qt.io/qtforpython-6/
