# AI Instructions — Digital Human Chat (Python / PySide6)

* 维护此数字人聊天面板项目。遵循 PEP 8。
* **关键约束**：Live2D 渲染使用 SDK Demo dist（已验证），不要用手写渲染器。

---

## 1. 修改规范

### 必须遵守

1. **修改已有代码前，先在 `z_dous/patches/` 创建补丁记录**（见下方模板）。
2. **修改前查阅 `z_dous/troubleshooting.md`**，避免重蹈已知坑。

### 补丁记录模板

每次修改时创建：

```
z_dous/patches/YYYY-MM-DD_简要描述/
├── CHANGES.md              # 总览：原因、文件列表、影响范围
├── modify_0/                # 第 1 个修改（完全重写 → 存全文）
│   ├── before/
│   │   └── 文件名.py.md     # 修改前全文（.md 后缀避免 IDE 报错）
│   └── after/
│       └── 文件名.py.md     # 修改后全文
└── modify_1/                # 第 2 个修改（小改动 → 只存差异）
    ├── before/
    │   └── 文件名.py.md     # 仅改动部分 + 上下文
    └── after/
        └── 文件名.py.md     # 仅改动部分 + 上下文
```

**规则**：
- **完全重写**（如换库、换 API）→ `before/after` 存**文件全文**
- **小改动**（如改函数名、几行代码）→ `before/after` 只存**改动的代码段**，文件头加 `# 位置: path/to/file.py, 方法/位置` 注释
- 每个被修改的文件一个 `modify_N/` 目录，按序编号
- **所有 patch 文件统一用 `.md` 后缀**（如 `ai_client.py.md`），避免 IDE 对裸 `.py` 文件报语法错误

`CHANGES.md` 格式：
```markdown
# 修改日期：YYYY-MM-DD

## 修改文件
- `path/to/file.py` — 简述改动 ---  modify_0
- `path/to/other.py` — 简述改动 ---  modify_1

## 修改原因
[简述]

## 修改内容
- 改了 A
- 加了 B

## 影响范围
[哪些功能受影响]
```

---

## 2. 项目概览

桌面数字人聊天应用：左侧聊天面板 + 右侧 Live2D 形象。

| 组件 | 技术 |
|------|------|
| 桌面框架 | PySide6 (QWebEngineView) |
| Web 入口 | 内建 HTTP server (CORS) |
| JS 诊断 | Live2DPage.javaScriptConsoleMessage → Python 终端 |
| Live2D 引擎 | Cubism SDK 5 Demo dist |
| 模型 | Haru（唯一） |
| AI | DeepSeek API（`core/ai_client.py`） |
| TTS | edge-tts + pygame |

详细架构见 `z_dous/deep-dive/architecture.md`。

---

## 3. 核心命令

```powershell
# 启动（PowerShell）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned ; d:\digital_human\.venv\Scripts\Activate.ps1 ; $env:PYTHONPATH="." ; python d:\digital_human\main.py

# 修改 TypeScript 后重新编译部署
cd CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo; npm run build
# → dist/assets/* 覆盖到 web/sdk_dist/assets/，更新 index.html <script> 引用

# 修改 Python 后清理缓存
Get-ChildItem -Recurse __pycache__ | Remove-Item -Recurse -Force
```

---

## 4. 关键文件速查

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

---

## 5. Live2D 控制 API

> SDK 源码位于 `CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/`。

### window.Live2D 方法一览

| 方法 | 参数 | 说明 |
|------|------|------|
| `playMotion(group, no, pri?)` | 组名,索引,优先级 | 播放指定动作 |
| `playRandomMotion(group, pri?)` | 组名,优先级 | 随机播放组内动作 |
| `setExpression(exprId)` | 表情 ID | 切换表情 |
| `setParameter(paramId, value)` | 参数名,值 | 一次性参数设置 |
| `startSpeechLipSync(text, durMs)` | 回复文本,时长 ms | 节奏式说话口型 |
| `stopLipSync()` | 无 | 立即闭嘴并复位 |
| `setAutoIdle(enabled)` | 布尔 | 切换自动待机循环 |

### 消息处理调用链

```
main_window.py _on_user_message()
  ├─ call_ai_async(text)                        → 后台线程 AI
  ├─ QTimer 轮询 get_ai_reply() → reply
  ├─ send_to_web("addMessage", ...)              → 显示回复
  ├─ synthesize_async(reply)                     → 后台合成 MP3
  ├─ QTimer 轮询 get_ready() → (path, duration)
  ├─ play_file(path)                             → pygame 播放
  └─ send_to_web("startSpeechLipSync", ...)      → 口型同步
```

### Haru 模型关键参数

- 10 个 Idle 动作 + 1 个 TapBody 动作
- 张嘴正确组合：`ParamMouthForm=-2.0` + `ParamMouthOpenY=1.0`
- `_autoIdle=false`（默认关闭自动待机）
- 更多模型细节见 `z_dous/deep-dive/live2d-internals.md`

---

## 6. 环境依赖

- `edge-tts` 需网络连接（Azure TTS）
- `pygame` 依赖 SDL2（Linux 需 `apt install libsdl2-mixer-2.0-0`）
- `openai` 用于 DeepSeek API 调用
