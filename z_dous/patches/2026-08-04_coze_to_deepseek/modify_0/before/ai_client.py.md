"""Coze AI 测试客户端 — Bot: test_1"""
import requests

_BOT_ID = "7566152243020464178"
_URL = "https://api.coze.cn/open_api/v2/chat"


def call_coze(question: str) -> str:
    """调用 Coze test_1 机器人，返回 AI 回复文本"""
    token = "pat_b1wWYtNyfMW9N2ZZlL1kVU06w1cEhxnZ3DOj8exGvCoFkPySkW4tXLSjR3agD0Y2"

    payload = {
        "bot_id": _BOT_ID,
        "user": "digital_human_2_user",
        "query": question,
        "stream": False,
    }

    try:
        resp = requests.post(
            _URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

        if resp.status_code != 200:
            return f"[网络错误] HTTP {resp.status_code}"

        data = resp.json()
        if data.get("code") != 0:
            return f"API 调用失败: {data.get('msg', '未知错误')}"

        messages = data.get("messages", [])
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("type") == "answer":
                return msg.get("content", "(空)")
        for msg in messages:
            if msg.get("role") == "assistant":
                return msg.get("content", "(空)")
        return "未找到 AI 回复内容"

    except requests.RequestException as e:
        return f"[网络错误] {e}"
    except json.JSONDecodeError:
        return "[错误] 响应解析失败"

__all__ = ["call_coze"]
