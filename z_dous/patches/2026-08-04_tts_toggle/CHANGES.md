# 修改日期：2026-08-04

## 修改文件
- `config.py` — 加 TTS_ENABLED 开关 --- modify_0
- `ui/bridge.py` — 加 toggle_tts Slot + tts_toggled 信号 --- modify_1
- `ui/main_window.py` — 连接开关、条件跳过 TTS --- modify_2
- `web/index.html` — 标题栏加 🔇 按钮 --- modify_3
- `web/app.js` — toggleTTS / setTTSState 函数 --- modify_3
- `web/style.css` — TTS 按钮样式 --- modify_3

## 修改原因
调试时每次等待 TTS 合成+播放效率低，需一键开关语音功能。

## 修改内容
- 默认关闭语音（`TTS_ENABLED = False`），点击 🔇→🔊 开启
- 关闭时 AI 只回复文字，跳过 synthesize + play + lip sync
- 状态互相同步：Python → JS 初始推送，JS → Python 点击切换

## 影响范围
- `main_window.py`：_on_user_message 中 TTS 流水线被条件包裹
- 前端：标题栏右侧新增语音开关按钮

## 修改文件（续）
- `core/tts_engine.py` — play_file 前自动 stop --- modify_4
- `ui/main_window.py` — TTS 流水线开始时 stop 旧音频 --- modify_4

## 修改内容（续）
- 修复语音重叠：播新音频前 `_audio.stop()` 停止旧音频
- 播完即删：`play_file()` 自动删除上一个音频文件，无需缓存管理 --- modify_5
