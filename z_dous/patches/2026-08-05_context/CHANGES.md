# 修改日期：2026-08-05

## 修改文件
- `core/ai_client.py` — 加对话历史管理 --- modify_0

## 修改原因
每次对话独立，AI 不知道上一轮说了什么，无法多轮对话。

## 修改内容
- 新增 `_history` 列表 + `_MAX_HISTORY_MSGS = 20`
- `call_ai()` 发送时把历史拼入 messages
- 回复后自动保存 user+assistant 到历史
- 超出上限自动裁剪旧消息
- `clear_history()` 供后续"新对话"按钮使用

## 影响范围
- `core/ai_client.py`：call_ai 的 messages 构建逻辑
