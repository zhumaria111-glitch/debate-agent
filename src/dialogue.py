"""Stage 2: Debate analysis and multi-turn dialogue."""

from __future__ import annotations

from .llm import call_llm
from .prompts import DIALOGUE_SYSTEM, WELCOME_MESSAGE, SUGGESTION_PROMPTS


def run_dialogue_turn(
    user_message: str,
    debate_data: dict,
    api_key: str,
    conversation_history: list[dict],
    model: str = "deepseek-chat",
    base_url: str | None = None,
    kb_context: str = "",
) -> str:
    """Process one user message and return the assistant's response.

    Args:
        kb_context: Optional cross-debate knowledge base context (RAG).
    """
    # Build chat context from conversation history
    context_parts = []
    for msg in conversation_history[-6:]:
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

    system = DIALOGUE_SYSTEM + "\n\n以下是辩论数据：\n" + debate_summary
    if kb_context:
        system += "\n\n## 知识库中其他辩论的相关内容（可用于跨视频对比分析）\n" + kb_context
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


KB_DIALOGUE_SYSTEM = """你是一个专业的辩论研究助手。你可以访问用户个人知识库中多场辩论的原文和论点。

你的能力：
- 从知识库中检索多场辩论的原文段落来回答问题
- 跨视频对比不同辩论中类似论证的异同
- 总结知识库中辩手的论证风格和常用策略
- 找出知识库中反复出现的论证模式

回复原则：
1. 回答时引用知识库中的具体原文，标注来自哪场辩论。
2. 如果同一概念在多场辩论中出现，主动对比分析。
3. 保持中立，不偏向任何一方。
4. 如果知识库中没有相关信息，诚实告知。
5. 回复简洁、有洞察力。"""


def run_kb_turn(
    user_message: str,
    kb_context: str,
    debate_overview: str,
    api_key: str,
    model: str = "deepseek-chat",
    base_url: str | None = None,
) -> str:
    """Process a KB-only query with cross-debate context."""
    system = KB_DIALOGUE_SYSTEM

    if debate_overview:
        system += "\n\n## 知识库中所有辩论概览\n" + debate_overview

    if kb_context:
        system += "\n\n## 与问题最相关的原文和论点\n" + kb_context
    else:
        system += "\n\n知识库中暂无与当前问题高度相关的内容。请基于辩论概览尽量回答。"

    return call_llm(
        system=system,
        user_message=user_message,
        api_key=api_key,
        model=model,
        max_tokens=2048,
        base_url=base_url,
    )
