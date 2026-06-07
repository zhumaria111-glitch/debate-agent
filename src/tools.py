"""Search and analysis tools for debate data.

Each tool operates on the StructuredDebate data (passed as dict for
Streamlit session state compatibility) and the raw transcript.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ── Tool definitions (Anthropic tool-use format) ──────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "search_transcript",
        "description": "在辩论原文中搜索关键词，返回包含该词的上下文段落。用于定位某个概念、数据或表述在辩论中的具体位置。",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "要搜索的关键词或短语",
                },
                "context_sentences": {
                    "type": "integer",
                    "description": "返回匹配位置前后各多少句上下文，默认2",
                    "default": 2,
                },
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "get_argument_chain",
        "description": "追踪一个论点的完整攻防链条：谁提出的、被谁反驳了、反驳是否有效、是否有再反驳。输入议题关键词即可。",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "要追踪的议题关键词，如'四天工作制'、'经济影响'",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "compare_positions",
        "description": "对比正反双方在某个具体议题上的立场，包括各自论点和证据。",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "要对比的议题，如'公平性'、'实施成本'",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_unresolved_issues",
        "description": "列出辩论中被提出但未被有效回应的所有问题，按重要性排序。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_speaker_analysis",
        "description": "分析某个辩手的论证风格、核心论点、逻辑漏洞和整体表现。",
        "input_schema": {
            "type": "object",
            "properties": {
                "speaker": {
                    "type": "string",
                    "description": "辩手名称",
                }
            },
            "required": ["speaker"],
        },
    },
    {
        "name": "check_factual_claims",
        "description": "列出辩论中所有引用数据或事实的主张，标注是否有证据支撑。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_quick_summary",
        "description": "返回辩论的3分钟速览卡片：一句话总结、双方Top3论点、最激烈交锋点和关键未回应问题。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────


def search_transcript(debate_data: dict, keyword: str, context_sentences: int = 2) -> str:
    """Search raw transcript for keyword with surrounding context."""
    transcript = debate_data.get("raw_transcript", "")
    if not transcript:
        # Fall back to searching in structured data
        return _search_structured(debate_data, keyword)

    keyword_lower = keyword.lower()
    sentences = _split_sentences(transcript)
    matches = []

    for i, sent in enumerate(sentences):
        if keyword_lower in sent.lower():
            start = max(0, i - context_sentences)
            end = min(len(sentences), i + context_sentences + 1)
            context = "".join(sentences[start:end])
            matches.append(f"[位置 {i+1}/{len(sentences)}] ...{context.strip()}...")

    if not matches:
        return f"未在辩论原文中找到与「{keyword}」相关的内容。"

    if len(matches) > 5:
        matches = matches[:5]
        matches.append(f"...（共找到 {len(matches)} 处匹配，以上为前5处）")

    return "\n\n---\n\n".join(matches)


def get_argument_chain(debate_data: dict, topic: str) -> str:
    """Trace the full attack/defense chain for a topic."""
    rounds = debate_data.get("rounds", [])
    related_claims = []

    for r_idx, round_data in enumerate(rounds):
        for claim in round_data.get("claims", []):
            if topic.lower() in claim.get("content", "").lower():
                related_claims.append({
                    "round": round_data.get("round_name", f"回合{r_idx+1}"),
                    "speaker": round_data.get("speaker", "未知"),
                    "side": round_data.get("side", ""),
                    "claim_id": claim.get("id", ""),
                    "content": claim.get("content", ""),
                    "rebuts": claim.get("rebuts_claim_id"),
                    "responded": claim.get("responded", False),
                    "response": claim.get("response_summary", ""),
                })

    if not related_claims:
        return f"未找到与「{topic}」直接相关的论点攻防记录。试试用更宽泛的关键词，或先用 search_transcript 定位相关段落。"

    lines = [f"## 「{topic}」论点攻防链\n"]
    for i, c in enumerate(related_claims, 1):
        line = f"{i}. [{c['round']}] {c['side']} {c['speaker']}：{c['content']}"
        if c["rebuts"]:
            line += f"\n   ↳ 反驳了论点 {c['rebuts']}"
        if c["responded"]:
            line += f"\n   ↳ 被回应：{c['response']}"
        elif i < len(related_claims):
            line += "\n   ↳ ⚠️ 未被有效回应"
        lines.append(line)

    return "\n".join(lines)


def compare_positions(debate_data: dict, topic: str) -> str:
    """Compare affirmative vs negative positions on a specific topic."""
    rounds = debate_data.get("rounds", [])
    aff_claims = []
    neg_claims = []

    for round_data in rounds:
        for claim in round_data.get("claims", []):
            if topic.lower() in claim.get("content", "").lower():
                entry = f"- [{round_data.get('round_name', '')}] {round_data.get('speaker', '')}：{claim.get('content', '')}"
                if claim.get("evidence"):
                    entry += f"（证据：{claim['evidence']}）"
                if round_data.get("side") == "正方":
                    aff_claims.append(entry)
                else:
                    neg_claims.append(entry)

    lines = [f"## 正反双方在「{topic}」上的立场对比\n"]
    lines.append(f"### 正方（{debate_data.get('affirmative_side', '')}）")
    lines.extend(aff_claims if aff_claims else ["（未涉及此议题）"])
    lines.append(f"\n### 反方（{debate_data.get('negative_side', '')}）")
    lines.extend(neg_claims if neg_claims else ["（未涉及此议题）"])

    if aff_claims and neg_claims:
        lines.append(f"\n> 双方在此议题上共交锋 {min(len(aff_claims), len(neg_claims))} 个回合。")

    return "\n".join(lines)


def get_unresolved_issues(debate_data: dict) -> str:
    """List all unresolved issues sorted by importance."""
    issues = debate_data.get("unresolved_issues", [])
    if not issues:
        return "辩论中所有问题都得到了回应（或未能识别出未解决的问题）。"

    # Sort by importance
    importance_order = {"高": 0, "中": 1, "低": 2}
    issues = sorted(issues, key=lambda x: importance_order.get(x.get("importance", "中"), 1))

    lines = ["## 未回应的关键问题\n"]
    for i, issue in enumerate(issues, 1):
        imp = issue.get("importance", "中")
        emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(imp, "")
        lines.append(f"{i}. {emoji} **{issue.get('issue', '')}**")
        lines.append(f"   提出方：{issue.get('raised_by', '未知')} | 重要性：{imp}")

    return "\n".join(lines)


def get_speaker_analysis(debate_data: dict, speaker: str) -> str:
    """Analyze a specific speaker's performance."""
    rounds = debate_data.get("rounds", [])
    speaker_rounds = []
    claims = []
    factual = []

    for r_idx, round_data in enumerate(rounds):
        if speaker in round_data.get("speaker", ""):
            speaker_rounds.append(round_data)
            for claim in round_data.get("claims", []):
                claims.append(claim)

    for fc in debate_data.get("factual_claims", []):
        if speaker in fc.get("speaker", ""):
            factual.append(fc)

    if not speaker_rounds:
        return f"未找到辩手「{speaker}」的发言记录。请检查名字是否准确。"

    lines = [f"## {speaker} 辩论表现分析\n"]
    lines.append(f"- 发言回合：{len(speaker_rounds)} 个")
    lines.append(f"- 提出论点：{len(claims)} 个")
    lines.append(f"- 引用数据：{len(factual)} 次")

    if claims:
        lines.append(f"\n### 核心论点")
        for c in claims:
            status = "✓ 被回应" if c.get("responded") else "⚠ 未被有效回应"
            lines.append(f"- {c.get('content', '')} [{status}]")

    if factual:
        lines.append(f"\n### 引用的事实主张")
        for f in factual:
            evidence_status = "✓ 有证据" if f.get("has_evidence") else "⚠ 未提供证据"
            lines.append(f"- {f.get('claim', '')} [{evidence_status}]")
            if f.get("evidence_detail"):
                lines.append(f"  详情：{f['evidence_detail']}")

    lines.append(f"\n### 表现评价")
    unresolved = sum(1 for c in claims if not c.get("responded"))
    lines.append(f"- 论点未被回应的比例：{unresolved}/{len(claims)}" if claims else "- 无")
    lines.append(f"- 对{debate_data.get('topic', '辩论')}的贡献度：{'高' if len(claims) >= 3 else '中'}")

    return "\n".join(lines)


def check_factual_claims(debate_data: dict) -> str:
    """List all factual claims and their evidence status."""
    claims = debate_data.get("factual_claims", [])
    if not claims:
        return "辩论中未发现引用数据或事实的主张。"

    lines = ["## 事实性主张核查\n"]
    for i, fc in enumerate(claims, 1):
        status = "✅ 有证据支撑" if fc.get("has_evidence") else "⚠️ 未提供证据"
        lines.append(f"{i}. {fc.get('claim', '')}")
        lines.append(f"   发言人：{fc.get('speaker', '未知')} | {status}")
        if fc.get("evidence_detail"):
            lines.append(f"   证据：{fc['evidence_detail']}")

    # Summary
    with_evidence = sum(1 for f in claims if f.get("has_evidence"))
    lines.insert(1, f"共 {len(claims)} 个事实性主张，其中 {with_evidence} 个有证据支撑，{len(claims) - with_evidence} 个缺乏支撑。\n")

    return "\n".join(lines)


def get_quick_summary(debate_data: dict) -> str:
    """Return the quick view card."""
    qv = debate_data.get("quick_view", {})
    if not qv:
        return "暂无可用的辩论摘要。"

    return f"""## 📋 3分钟速览

### 辩题
{debate_data.get('topic', '未知')}

### 一句话总结
{qv.get('one_sentence_summary', '')}

### 正方核心立场
{debate_data.get('affirmative_side', '')}
{chr(10).join(f'- {p}' for p in qv.get('affirmative_top3', []))}

### 反方核心立场
{debate_data.get('negative_side', '')}
{chr(10).join(f'- {p}' for p in qv.get('negative_top3', []))}

### 🔥 最激烈交锋
{qv.get('hottest_clash', '')}

### ⚠️ 关键未回应问题
{qv.get('key_unresolved', '')}

### 关键词
{' | '.join(qv.get('keywords', []))}
"""


# ── Tool dispatcher ───────────────────────────────────────────────────

TOOL_HANDLERS = {
    "search_transcript": search_transcript,
    "get_argument_chain": get_argument_chain,
    "compare_positions": compare_positions,
    "get_unresolved_issues": get_unresolved_issues,
    "get_speaker_analysis": get_speaker_analysis,
    "check_factual_claims": check_factual_claims,
    "get_quick_summary": get_quick_summary,
}


def execute_tool(tool_name: str, tool_input: dict, debate_data: dict) -> str:
    """Execute a tool by name and return the result string."""
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return f"未知工具：{tool_name}"
    try:
        return handler(debate_data, **tool_input)
    except Exception as e:
        return f"工具执行出错：{str(e)}"


# ── Helpers ───────────────────────────────────────────────────────────

def _split_sentences(text: str) -> list[str]:
    """Split Chinese text into sentences."""
    import re
    # Split on Chinese/English punctuation
    sentences = re.split(r"(?<=[。！？；\.\!\?\n])", text)
    return [s for s in sentences if s.strip()]


def _search_structured(debate_data: dict, keyword: str) -> str:
    """Fallback: search structured data when raw transcript is unavailable."""
    results = []
    keyword_lower = keyword.lower()

    for round_data in debate_data.get("rounds", []):
        for claim in round_data.get("claims", []):
            if keyword_lower in claim.get("content", "").lower():
                results.append(
                    f"[{round_data.get('round_name', '')}] {round_data.get('side', '')} "
                    f"{round_data.get('speaker', '')}：{claim.get('content', '')}"
                )

    if not results:
        return f"未找到与「{keyword}」相关的内容。"

    return "\n".join(results)
