"""Stage 2: Debate analysis agent with multi-turn conversation and tool use."""

from __future__ import annotations

from .llm import call_llm
from .prompts import AGENT_SYSTEM, WELCOME_MESSAGE, SUGGESTION_PROMPTS


def run_agent_turn(
    user_message: str,
    debate_data: dict,
    api_key: str,
    conversation_history: list[dict],
    model: str = "deepseek-chat",
    base_url: str | None = None,
) -> str:
    """Process one user message and return the agent's response."""
    # Build chat context from conversation history
    context_parts = []
    for msg in conversation_history[-6:]:  # Last 6 messages for context
        role = "用户" if msg.get("role") == "user" else "AI"
        context_parts.append(f"{role}：{msg.get('content', '')}")
    context = "\n".join(context_parts)

    # Include debate data summary for reference
    qv = debate_data.get("quick_view", {})
    debate_summary = f"""当前辩论：{debate_data.get('topic', '未知')}
正方：{debate_data.get('affirmative_side', '')}
反方：{debate_data.get('negative_side', '')}
一句话总结：{qv.get('one_sentence_summary', '')}
正方Top3：{'; '.join(qv.get('affirmative_top3', []))}
反方Top3：{'; '.join(qv.get('negative_top3', []))}
最激烈交锋：{qv.get('hottest_clash', '')}
关键未回应问题：{qv.get('key_unresolved', '')}"""

    system = AGENT_SYSTEM + "\n\n以下是辩论数据：\n" + debate_summary
    user_msg = f"对话历史：\n{context}\n\n用户最新问题：{user_message}"

    return call_llm(
        system=system,
        user_message=user_msg,
        api_key=api_key,
        model=model,
        max_tokens=2048,
        base_url=base_url,
    )


def generate_welcome_message(debate_data: dict) -> str:
    """Generate the initial welcome message after compression is done."""
    qv = debate_data.get("quick_view", {})
    unresolved = debate_data.get("unresolved_issues", [])
    unans = len(unresolved)

    return WELCOME_MESSAGE.format(
        one_sentence=qv.get("one_sentence_summary", "这场辩论的信息已整理完毕"),
        hottest_clash=qv.get("hottest_clash", "多个议题"),
        unanswered=unans,
    )


def get_suggestions() -> list[str]:
    """Return suggested follow-up questions."""
    return SUGGESTION_PROMPTS
