# ===== before: core/ai_client.py, summarize_history() 中 summary_prompt =====

    summary_prompt = (
        f"请用 一段文字 概括以下对话的要点，只提取关键信息（人名、偏好、事实等）：\n\n{conv_text}"
    )