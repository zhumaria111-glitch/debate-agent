"""Evaluate RAG knowledge base with 10 test queries across 5 dimensions."""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", None)
MODEL = "deepseek-chat"

from src.knowledge_base import KnowledgeBase
from src.agent import run_kb_turn

QUERIES = [
    # ── Dimension 1: 检索命中率 ──
    {
        "id": 1,
        "dim": "检索命中率 + 细节可检索性",
        "query": "马尔库塞单向度的人",
        "expected": "技术是否中立 — 反方一辩陈词引用马尔库塞「单向度的人」概念",
    },
    {
        "id": 2,
        "dim": "检索命中率 + 细节可检索性",
        "query": "海德格尔四因说 技术的本质",
        "expected": "技术是否中立 — 反方一辩陈词，四因说论述",
    },
    {
        "id": 3,
        "dim": "检索命中率 + 细节可检索性",
        "query": "赌场荷官发牌",
        "expected": "技术是否中立 — 反方一辩：荷官发牌中立但赌场机制要盈利",
    },
    {
        "id": 4,
        "dim": "检索命中率 + 细节可检索性",
        "query": "吉普赛人那块冰 烫的",
        "expected": "技术是否中立 — 反方结辩引用马尔克斯《百年孤独》",
    },
    {
        "id": 5,
        "dim": "检索命中率 + 细节可检索性",
        "query": "雅斯贝尔斯 技术意义",
        "expected": "技术是否中立 — 正方一辩引用雅斯贝尔斯「人赋予了技术与意义」",
    },
    # ── Dimension 3: 跨视频对比 ──
    {
        "id": 6,
        "dim": "跨视频对比 + 引用准确性",
        "query": "在这几场辩论里，哪一方的论证策略最大胆或最创新？为什么？",
        "expected": "多场辩论原文；技术是否中立(肖磊黑魔法/白魔法框架)；脱口秀vs辩论(论证方式对比)",
    },
    {
        "id": 7,
        "dim": "跨视频对比 + 引用准确性",
        "query": "知识库里哪些辩论提到了自由意志？各方是怎么用的？",
        "expected": "技术是否中立(正方核心论点)；爱情辩论(自由意志与爱情选择)；恶意vs愚蠢(自由意志与责任)",
    },
    {
        "id": 8,
        "dim": "检索命中率 + 跨视频对比",
        "query": "这几场辩论里辩手用过哪些历史事件作为例子？",
        "expected": "技术是否中立(甲午海战、布鲁诺、秦始皇)；拐卖妇女儿童(具体案件)",
    },
    # ── Dimension 5: 细节可检索性 — 盲区测试 ──
    {
        "id": 9,
        "dim": "细节可检索性（盲区测试）",
        "query": "莱茵河 阿尔卑斯山",
        "expected": "技术是否中立 — 反方一辩：莱茵河的壮美/阿尔卑斯山的日出日落",
    },
    {
        "id": 10,
        "dim": "细节可检索性（综合盲区）",
        "query": "罗德柴尔斯 青霉素",
        "expected": "技术是否中立 — 反方引用罗氏死于细菌感染的事例",
    },
]


def main():
    kb = KnowledgeBase(os.path.join(ROOT, "data", "knowledge_base"))
    print(f"KB: {kb.count()} debates, {kb.count_chunks()} chunks\n")

    # Build debate overview
    debates = kb.list_debates()
    overview = "\n".join(f"- {d['topic']}: {d['summary'][:100]}" for d in debates)

    results = []
    for q in QUERIES:
        print(f"{'='*60}")
        print(f"Query {q['id']}: {q['query']}")
        print(f"Expected: {q['expected']}")
        print(f"{'='*60}")

        # Step 1: Search KB for raw hits
        search_results = kb.search(q["query"], n=8)
        t_hits = search_results["transcripts"]
        c_hits = search_results["claims"]

        n_transcript_hits = len(t_hits["documents"][0]) if t_hits.get("documents") and t_hits["documents"][0] else 0
        n_claim_hits = len(c_hits["documents"][0]) if c_hits.get("documents") and c_hits["documents"][0] else 0

        print(f"\nTranscript chunks found: {n_transcript_hits}")
        if n_transcript_hits > 0:
            for i, doc in enumerate(t_hits["documents"][0][:5]):
                meta = t_hits["metadatas"][0][i] if t_hits["metadatas"] else {}
                dist = t_hits["distances"][0][i] if t_hits.get("distances") else 0
                print(f"  [{meta.get('topic','')}] dist={dist:.3f} | {doc[:120]}...")

        # Step 2: Build RAG context
        kb_ctx = kb.build_context(q["query"], n=8)

        # Step 3: Ask AI for analysis
        print("\n--- AI Response ---")
        ai_response = run_kb_turn(
            user_message=q["query"],
            kb_context=kb_ctx,
            debate_overview=overview,
            api_key=API_KEY,
            model=MODEL,
            base_url=BASE_URL,
        )
        print(ai_response[:800])

        results.append({
            "id": q["id"],
            "query": q["query"],
            "dim": q["dim"],
            "expected": q["expected"],
            "n_transcript_hits": n_transcript_hits,
            "n_claim_hits": n_claim_hits,
            "ai_response": ai_response,
        })
        print()

    # Save raw results
    out_path = os.path.join(ROOT, "data", "eval", "kb_eval_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
