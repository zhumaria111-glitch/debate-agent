"""Clean raw AI subtitle transcripts into structured debate text.

Called inline during the URL-paste pipeline: fetch → clean → compress.
Also usable offline via scripts/clean_transcripts.py for batch processing.
"""

from __future__ import annotations

import anthropic


CLEANING_PROMPT = """你是一个专业的辩论文字稿整理专家。你的任务是把 AI 语音识别生成的原始字幕整理成结构化的辩论文字稿。

原始字幕的问题：
- 没有标点符号
- 按字幕时间切分，不是按语义切分，句子碎片化
- 没有发言人标注
- 混杂了主持人闲聊、开场串场、广告口播、投票环节等非辩论内容
- 可能包含哲理辩（长陈词+主持人质询）、标准竞技辩论（立论/质询/自由辩论/结辩）等多种赛制

你需要输出的格式：

1. 删除开场闲聊、广告口播、主持人串场、投票计票、结束语（直接跳到辩论开始，辩论结束就停止）
2. 将碎片化的字幕行合并为完整的、有标点符号的段落
3. 根据上下文推断发言人角色，标注为：正方一辩/正二/正三/正四 或 反方一辩/反二/反三/反四。哲理辩中如果只有两位辩手+主持人，则标注为"正方"/"反方"/"主持人"
4. 标注辩论环节：正方一辩陈词、反四质询正一、自由辩论、正方结辩、反方结辩……主持人质询环节标注为"主持人提问"，辩手的回答要保留在对应的辩论方名下
5. 每段发言保持完整，不要再次碎片化
6. 主持人向辩手提问时：保留辩手的回答内容，标注清楚是谁在回答

参考输出格式：

cut-off
正方一辩陈词：
谢谢主席，大家好。当我方说起...(完整的立论内容)...

cut-off
反四质询正一：
反四：(问题)
正一：(回答)

cut-off
主持人提问：
主持人：(问题)
正方：(回答)

请直接输出整理后的文字稿，不要输出任何解释性文字。"""


def clean_transcript(
    raw_text: str,
    api_key: str,
    model: str = "deepseek-chat",
    base_url: str | None = None,
) -> str:
    """Clean raw AI subtitles into structured debate transcript.

    Args:
        raw_text: Raw AI-generated subtitles (no punctuation, no speakers).
        api_key: Anthropic-compatible API key.
        model: Model name to use for cleaning.
        base_url: Optional custom API base URL.

    Returns:
        Structured transcript with punctuation, speaker labels, and round markers.
    """
    client = _build_client(api_key, base_url)

    if len(raw_text) < 25000:
        return _call_claude(client, raw_text, model, CLEANING_PROMPT)

    # Long transcript: split into chunks, clean each, then concatenate
    chunks = _split_into_chunks(raw_text, chunk_size=20000)
    cleaned_chunks = []
    for i, chunk in enumerate(chunks):
        system = CLEANING_PROMPT + (
            f"\n注意：这是一场辩论的第 {i+1}/{len(chunks)} 部分。"
            f"请只整理这一部分的文字稿。"
        )
        result = _call_claude(client, chunk, model, system)
        cleaned_chunks.append(result)

    return "\n\n".join(cleaned_chunks)


def _build_client(api_key: str, base_url: str | None) -> anthropic.Anthropic:
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return anthropic.Anthropic(**kwargs)


def _call_claude(
    client: anthropic.Anthropic,
    text: str,
    model: str,
    system: str,
) -> str:
    """Call Claude API to clean text."""
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": text}],
    )
    for block in response.content:
        if getattr(block, "type", "") == "text":
            return block.text
    return response.content[0].text


def _split_into_chunks(text: str, chunk_size: int = 20000) -> list[str]:
    """Split text into roughly equal chunks at line boundaries.

    Raw AI subtitles use single-line breaks (\\n), not paragraphs.
    We split at the nearest line break to chunk_size to avoid cutting
    mid-sentence.
    """
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) < chunk_size:
            current += line + "\n"
        else:
            if current:
                chunks.append(current.rstrip("\n"))
            current = line + "\n"
    if current.strip():
        chunks.append(current.rstrip("\n"))
    return chunks
