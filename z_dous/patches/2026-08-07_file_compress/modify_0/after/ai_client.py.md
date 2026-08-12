# ===== after: core/ai_client.py, summarize_history() 中 =====

    # 检测是否含文件块 → 附加"大幅压缩文件"指令
    file_hint = ""
    if "[文件:" in conv_text:
        file_hint = (
            "\n\n注意：对话中可能包含 [文件: ...] 到 [/文件] 的文件内容。"
            "对每个文件块，只需用一句话概括其主题或关键事实，"
            "不要保留文件的具体内容细节，以最大限度压缩长度。"
        )

    summary_prompt = (
        f"请用 一段文字 概括以下对话的要点，只提取关键信息（人名、偏好、事实等）："
        f"{file_hint}\n\n{conv_text}"
    )