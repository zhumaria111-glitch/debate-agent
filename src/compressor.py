"""Stage 1: Compress debate transcript into structured data + 3-min quick view."""

import json
import re
from .llm import call_llm
from .models import (
    StructuredDebate,
    QuickView,
    DebateRound,
    Claim,
    UnresolvedIssue,
    FactualClaim,
)
from .prompts import COMPRESSOR_SYSTEM


def _filter_fields(data: dict, dataclass_type: type) -> dict:
    """Filter dict to only include fields valid for the given dataclass."""
    valid = {f.name for f in dataclass_type.__dataclass_fields__.values()}
    return {k: v for k, v in data.items() if k in valid}


def _safe_construct_quickview(data: dict) -> QuickView:
    """Construct QuickView with fallback defaults for missing fields."""
    defaults = {
        "one_sentence_summary": "",
        "affirmative_top3": [],
        "negative_top3": [],
        "hottest_clash": "",
        "key_unresolved": "",
        "keywords": [],
    }
    defaults.update(_filter_fields(data, QuickView))
    return QuickView(**defaults)


def compress_transcript(
    transcript: str,
    api_key: str,
    model: str = "claude-sonnet-4-6",
    max_chars_per_chunk: int = 15000,
    base_url: str | None = None,
) -> StructuredDebate:
    """Compress a debate transcript into structured analysis data.

    For transcripts shorter than max_chars_per_chunk, processes in a single pass.
    For longer transcripts, splits into overlapping chunks and merges.
    """
    if len(transcript) <= max_chars_per_chunk:
        return _single_pass_compress(transcript, api_key, model, base_url)
    else:
        return _chunked_compress(transcript, api_key, model, max_chars_per_chunk, base_url)


def _single_pass_compress(
    transcript: str, api_key: str, model: str, base_url: str | None = None
) -> StructuredDebate:
    """Process the entire transcript in one LLM call."""
    raw_output = call_llm(
        system=COMPRESSOR_SYSTEM,
        user_message=transcript,
        api_key=api_key,
        model=model,
        max_tokens=8192,
        base_url=base_url,
    )
    debate_data = _parse_json_response(raw_output)
    debate_data["raw_transcript"] = transcript
    return StructuredDebate.from_dict(debate_data)


def _chunked_compress(
    transcript: str, api_key: str, model: str, chunk_size: int, base_url: str | None = None
) -> StructuredDebate:
    """Split long transcript into chunks, process each, then merge.

    Strategy: split by double-newline (paragraph boundaries) to respect
    natural debate turn boundaries. If a chunk exceeds chunk_size, split
    at the last complete paragraph within the limit.
    """
    paragraphs = transcript.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Process each chunk to extract structured data
    all_rounds = []
    all_unresolved = []
    all_factual = []

    # Use a simplified prompt for chunk-level extraction
    chunk_system = COMPRESSOR_SYSTEM + (
        "\n注意：这是一场辩论的部分片段。请只分析这一片段中的内容，"
        "并标注论点ID时添加片段编号前缀。"
    )

    for i, chunk in enumerate(chunks):
        for attempt in range(2):
            try:
                raw = call_llm(
                    system=chunk_system,
                    user_message=chunk,
                    api_key=api_key,
                    model=model,
                    max_tokens=8192,
                    base_url=base_url,
                )
                data = _parse_json_response(raw)
                break
            except (ValueError, json.JSONDecodeError) as e:
                if attempt == 0:
                    continue
                print(f"⚠️ Chunk {i+1}/{len(chunks)} JSON 解析失败（已重试）: {e}")
                data = {}
        all_rounds.extend(data.get("rounds", []))
        all_unresolved.extend(data.get("unresolved_issues", []))
        all_factual.extend(data.get("factual_claims", []))

    # Merge: run a final pass to generate the quick_view from all extracted data
    merge_prompt = f"""以下是辩论的结构化分析数据（多段合并）：

辩题：{all_rounds[0].get('content_summary', '') if all_rounds else '未知'}

各段论点摘要：
{json.dumps([r.get('content_summary', '') for r in all_rounds], ensure_ascii=False)}

未解决问题：
{json.dumps(all_unresolved, ensure_ascii=False)}

请基于以上信息生成 quick_view。必须遵守以下规则：
- one_sentence_summary：一句话总结全场（不超过80字），禁止为空
- affirmative_top3：正方最重要的3个论点，每条15-30字，必须恰好3条，禁止返回 []
- negative_top3：反方最重要的3个论点，每条15-30字，必须恰好3条，禁止返回 []
- hottest_clash：双方交锋最激烈的一个议题（20字以内），禁止为空字符串
- key_unresolved：全场最关键的一个未被回应的问题（20字以内），禁止为空字符串
- keywords：5个关键词
只输出 quick_view JSON：
```json
{{
  "topic": "...",
  "affirmative_side": "...",
  "negative_side": "...",
  "quick_view": {{...}}
}}
```"""

    merge_raw = call_llm(
        system="你是辩论分析专家。基于已有分析数据生成最终摘要。只输出 JSON。",
        user_message=merge_prompt,
        api_key=api_key,
        model=model,
        max_tokens=2048,
        base_url=base_url,
    )

    merge_data = _parse_json_response(merge_raw)

    # Convert dict claims to Claim objects (same as from_dict)
    rounds = []
    for r in all_rounds:
        r_filtered = _filter_fields(r, DebateRound)
        claims_raw = r_filtered.pop("claims", [])
        claims = [Claim(**_filter_fields(c, Claim)) for c in claims_raw]
        rounds.append(DebateRound(claims=claims, **r_filtered))

    return StructuredDebate(
        topic=merge_data.get("topic", ""),
        affirmative_side=merge_data.get("affirmative_side", ""),
        negative_side=merge_data.get("negative_side", ""),
        quick_view=_safe_construct_quickview(merge_data.get("quick_view", {})),
        rounds=rounds,
        unresolved_issues=[UnresolvedIssue(**_filter_fields(u, UnresolvedIssue)) for u in all_unresolved],
        factual_claims=[FactualClaim(**_filter_fields(f, FactualClaim)) for f in all_factual],
        raw_transcript=transcript,
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Remove markdown code fences if present
    text = text.strip()

    # Try to find JSON within ```json ... ``` blocks
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1).strip()

    # Find the outermost { ... }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt repair: remove trailing commas, fix unquoted keys
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"LLM 返回 JSON 无法解析。原始输出前 300 字符: {text[:300]}")
