# 修改日期：2026-08-04

## 修改文件
- `web/app.js` — sendMsg 异步化 + 输入框锁定 --- modify_0
- `ui/main_window.py` — AI 回复后解锁输入 --- modify_1

## 修改原因
用户发送消息后，输入框卡住直到 AI 回复才刷新。bridge.send_message 同步阻塞
导致浏览器无法重绘 DOM。需将桥接调用异步化，并锁定/解锁输入框。

## 修改内容
- `setTimeout` 延迟 bridge.send_message，让浏览器先渲染用户消息
- 发送时锁定输入框（disabled + 视觉提示）
- AI 回复后 Python 通知前端解锁

## 影响范围
- `web/app.js`：sendMsg 函数 + 新增 lock/unlock 辅助函数
- `ui/main_window.py`：_on_user_message 末尾追加解锁调用
