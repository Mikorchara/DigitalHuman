# 修改日期：2026-08-05

## 修改文件
- `core/ai_client.py` — 加 summarize_history() --- modify_0
- `ui/bridge.py` — 加 summarize_context Slot + 信号 --- modify_0
- `ui/main_window.py` — 连接信号 + 处理 --- modify_0
- `web/index.html` — 上下文面板加 📝 按钮 --- modify_0
- `web/app.js` — summarizeContext() --- modify_0

## 修改原因
手动压缩旧对话历史为摘要，释放上下文空间。

## 修改内容
- `summarize_history()`：取前一半旧消息 → 让 AI 总结为 2-3 句话 → 替换为摘要
- 上下文面板新增"📝 压缩"按钮
- 压缩结果推送到聊天面板显示

## 影响范围
- `core/ai_client.py`：新增摘要函数
- 前端：上下文面板多一个操作按钮
