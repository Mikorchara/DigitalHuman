"""
数字人聊天面板 — 全局配置

所有可调参数集中管理。
敏感信息（API Key）优先从环境变量读取，开发时可用默认值。
"""

import os
from pathlib import Path

# ── 项目路径 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "web"

# ── LLM / AI 配置 ─────────────────────────────────────
# 优先级：环境变量 > 此处默认值
# 部署时建议设置环境变量，避免密钥泄露到代码仓库
LLM_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY",
    "sk-c25305e9a187493c9f6700a973f3c129"
)
LLM_BASE_URL = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com/v1"
)
LLM_MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-chat"
)

# ── 窗口配置 ──────────────────────────────────────────
WINDOW_TITLE = " guide "
WINDOW_DEFAULT_SIZE = (960, 640)
WINDOW_MIN_SIZE = (640, 440)

# ── HTTP 服务器 ───────────────────────────────────────
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 0  # 0 = 自动分配可用端口

# ── TTS 语音 ──────────────────────────────────────────
TTS_ENABLED = False      # 默认关闭语音，调试时通过界面按钮开启
