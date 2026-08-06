# AI 回复接口接入指南

> 写给 AI 回答功能开发者：你只需实现一个 `call_ai` 函数，数字人系统会自动完成显示→语音→口型的全链路。

---

## 一、你要改的文件

**只有这一个**：`core/ai_client.py`

---

## 二、你只需实现一个函数

```python
def call_ai(user_message: str) -> str:
    """
    参数:
        user_message : str — 用户在聊天框输入的内容

    返回:
        str — AI 的回复文本（纯字符串）
    """
    # ← 在这里写你的 AI 调用逻辑
    return "这是一条 AI 回复"
```

### 契约（必须遵守）

| 规则 | 说明 |
|------|------|
| **入参** | 一个参数 `user_message: str`，就是用户刚发送的消息 |
| **出参** | 返回 `str`，就是 AI 的回复（纯文本，不要 JSON） |
| **阻塞** | 函数内部可以同步等待（发 HTTP 请求等），数字人系统会自动处理 TTS + 口型 |
| **错误** | 如果出错，返回以 `[错误]` 开头的字符串即可，不要抛异常 |
| **文件** | 只改 `core/ai_client.py`，别改其他文件 |

---

## 三、数字人系统如何调用你的函数

```
用户在聊天框输入 "今天天气怎么样？"
        ↓
main_window._on_user_message("今天天气怎么样？")
        ↓
reply = call_ai("今天天气怎么样？")    ← 调用你的函数
        ↓
show(reply)  → 显示在聊天面板
synthesize_async(reply)  → 后台合成语音
play_file(...)  → 播放音频
startSpeechLipSync(text, durMs)  → 驱动口型
```

你只需保证 `call_ai` 返回一段文本，后面的显示→语音→口型数字人系统全自动完成。

---

## 四、接入示例（替换当前的 Coze 调用）

```python
# core/ai_client.py

import requests
import json

def call_ai(user_message: str) -> str:
    """调用你们的 AI 接口，返回回复文本"""

    # ===== 1. 构造请求 =====
    payload = {
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    try:
        resp = requests.post(
            "https://你的AI接口地址",
            headers={
                "Authorization": "Bearer 你的密钥",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except Exception as e:
        return f"[错误] 网络请求失败: {e}"

    # ===== 2. 解析响应 =====
    if resp.status_code != 200:
        return f"[错误] HTTP {resp.status_code}"

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return "[错误] 响应不是有效 JSON"

    # ===== 3. 提取回复文本 =====
    reply = data.get("reply") or data.get("content") or data.get("answer")
    if not reply:
        return "[错误] 响应中未找到回复内容"

    return reply
```

---

## 五、错误处理规范

你的函数**不应该抛异常**。如果抛异常会崩掉整个应用。

| 情况 | 返回示例 |
|------|----------|
| 成功 | `"你好！今天天气不错～"` |
| 网络错误 | `"[错误] 网络请求失败: ..."` |
| HTTP 错误 | `"[错误] HTTP 500: ..."` |
| 响应无回复 | `"[错误] 响应中未找到回复内容"` |

---

## 六、当前状态

| 项目 | 值 |
|------|-----|
| **占位实现** | `core/ai_client.py`（Coze test_1 Bot，仅测试用） |
| **你要替换的函数** | `call_ai` → 移除 Coze 逻辑，接入你们的接口 |

---

## 七、检查清单

- [ ] 函数名是 `call_ai`
- [ ] 函数接收 `user_message: str` 一个参数
- [ ] 函数返回 `str`
- [ ] 错误时返回 `"[错误] ..."`，不抛异常
- [ ] `python main.py` 发消息验证
