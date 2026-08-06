# 修改日期：2026-08-04

## 修改文件
- `core/ai_client.py` — 加取消标志 + cancel_ai() --- modify_0
- `ui/bridge.py` — 加 cancel Slot + cancel_requested 信号 --- modify_1
- `ui/main_window.py` — 连接取消信号 + _on_cancel --- modify_2
- `web/app.js` — 发送按钮变身取消按钮 ✕ --- modify_3

## 修改原因
用户等待 AI 回复时无法取消，必须等超时或回复完成。

## 修改内容
- `ai_client.py`：全局 `_cancel_flag`，`cancel_ai()` 设标志，`get_ai_reply()` 检测后返回 `[已取消]`
- `bridge.py`：新增 `cancel()` Slot 和 `cancel_requested` 信号
- `main_window.py`：`_on_cancel` 停止 AI 计时器 + 解锁输入
- `app.js`：`disableInput` 中按钮文字切换 `➤` ↔ `✕`，`cancelRequest()` 调 `bridge.cancel()`

## 影响范围
- 发送/取消按钮交互
- AI 轮询流程（`[已取消]` 不触发 TTS）
