# 修改日期：2026-08-05

## 修改文件
- `core/ai_client.py` — 加 get_history / undo_last_round --- modify_0
- `ui/bridge.py` — 加历史管理 4 个 Slot + 信号 --- modify_1
- `ui/main_window.py` — 连接信号 + 推送历史 --- modify_1
- `web/index.html` — 上下文面板 HTML --- modify_2
- `web/app.js` — 面板切换 + showHistory --- modify_2
- `web/style.css` — 上下文面板样式 --- modify_2

## 修改原因
上下文管理不够直观，用户无法查看、回退、清空对话历史。

## 修改内容
- 标题栏新增 📋 按钮，点击切换聊天 ↔ 上下文面板
- 上下文面板显示对话历史的 user/assistant 列表
- "↩ 回退一轮" 删除最后一组对话
- "🗑 清空全部" 重置所有上下文
- ✕ 返回聊天面板

## 影响范围
- 前端：新增上下文面板 UI
- 后端：ai_client 新增 get_history / undo_last_round
