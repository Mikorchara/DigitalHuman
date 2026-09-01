# 位置: core/ai_client.py, 错误分类提示（API Key 无效分支）

        if "api_key" in msg.lower() or "authentication" in msg.lower():
            return "[错误] API Key 无效，请检查 config.py"
