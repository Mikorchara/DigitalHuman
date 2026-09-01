# 开发路线图 — Digital Human Chat

> 维护：记录接下来的计划与当前进度。

## ✅ 已完成

- [x] 基础框架：PySide6 + QWebEngineView + 内建 HTTP 服务器
- [x] Live2D 数字人（Cubism SDK 5 Demo dist，模型 Haru）
- [x] AI 对话：DeepSeek API（OpenAI 兼容）
- [x] 对话上下文（历史 / 人设 / 参考资料，可编辑）
- [x] 语音合成：edge-tts + pygame 播放 + 文本节奏口型
- [x] TTS 开关、文件输入、上下文压缩/回退
- [x] TTS 临时文件"播完即删 + 退出清空"
- [x] 密钥配置外置（config.example.py 模板 + 环境变量）

## 🔜 下一步

### TTS 优化
- [ ] `edge-tts` 改用 `stream()` + **词边界精确口型同步**（替代估算时长）
      → 见 `z_docs/deep-dive/` 与 patches 记录
- [ ] （进阶）真·流式播放（mpv/ffplay 管道），降低首包延迟

### AI 多服务商
- [ ] `ai_client.py` 支持**多 AI 服务商可切换**（DeepSeek 被代理阻断时可切备用）
      → 统一 OpenAI 兼容接口：base_url / api_key / model 可配置

### Live2D 增强
- [ ] 多角色切换（SDK 自带 Hiyori/Mao/Ren 等模型）
- [ ] 情绪联动：根据 AI 回复自动切换表情/动作

### 体验 / 工程
- [ ] 会话历史持久化（重启恢复）
- [ ] PyInstaller 打包发布验证
- [ ] Markdown 渲染（代码块/列表）

## ⏸️ 暂缓

- 全局快捷键系统（pynput）
- 本地 TTS 引擎接入（Qwen3-TTS / Kokoro，需评估资源占用）
