# ===== before: core/ai_client.py, call_ai() messages 部分 =====

        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.8,
            max_tokens=600,
        )