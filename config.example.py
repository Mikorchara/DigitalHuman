"""
数字人聊天面板 — 全局配置（示例模板）

【使用方式】
1. 复制本文件为本地 `config.py`：
       copy config.example.py config.py
2. 在 config.py 中填写真实 API Key（本文件仅作模板，不含真实密钥）。
   或直接设置环境变量（优先级最高，无需改文件）：
       DEEPSEEK_API_KEY=sk-xxx
       DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
       DEEPSEEK_MODEL=deepseek-chat
3. `config.py` 已被 `.gitignore` 排除，不会上传到仓库。

【安全说明】
- 真实 API Key 请勿写入本文件，也不要提交到 git。
- 密钥建议通过环境变量注入，或填入本地 config.py（不入库）。
"""

import os
from pathlib import Path

# ── 项目路径 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "web"

# ── LLM / AI 配置 ─────────────────────────────────────
# 优先级：环境变量 > config.py 中的值
# 真实密钥：填入本地 config.py，或用环境变量 DEEPSEEK_API_KEY
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-在此填入你的API密钥")
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ── 窗口配置 ──────────────────────────────────────────
WINDOW_TITLE = " guide "
WINDOW_DEFAULT_SIZE = (960, 640)
WINDOW_MIN_SIZE = (640, 440)

# ── HTTP 服务器 ───────────────────────────────────────
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 0  # 0 = 自动分配可用端口

# ── TTS 语音 ──────────────────────────────────────────
TTS_ENABLED = False      # 默认关闭语音，调试时通过界面按钮开启
