"""Ingest all 6 built-in debates into the knowledge base."""
import os, sys, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", None)
MODEL = "deepseek-chat"

from src.knowledge_base import KnowledgeBase
from src.compressor import compress_transcript

BUILT_IN = [
    {"topic": "是否应该全面推行四天工作制", "transcript_file": "data/sample_debate.txt", "type": "政策辩"},
    {"topic": "爱情是/不是人类的必需品", "transcript_file": "data/eval/debate_01.txt", "type": "价值辩"},
    {"topic": "拐卖妇女儿童应该/不应该买卖同罪", "transcript_file": "data/eval/debate_02_cleaned.txt", "type": "政策辩"},
    {"topic": "网络暴力的根源是恶意还是愚蠢", "transcript_file": "data/eval/debate_03_cleaned.txt", "type": "事实辩"},
    {"topic": "脱口秀还是辩论更能回应世界", "transcript_file": "data/eval/debate_04_cleaned.txt", "type": "哲理辩"},
    {"topic": "技术是否中立", "transcript_file": "data/eval/debate_05_cleaned.txt", "type": "哲理辩"},
]

kb = KnowledgeBase(os.path.join(ROOT, "data", "knowledge_base"))
existing = {d["topic"] for d in kb.list_debates()}

for debate in BUILT_IN:
    if debate["topic"] in existing:
        print(f"[SKIP] Already in KB: {debate['topic']}")
        continue

    path = os.path.join(ROOT, debate["transcript_file"])
    if not os.path.exists(path):
        print(f"[MISS] Transcript not found: {path}")
        continue

    with open(path) as f:
        transcript = f.read()

    print(f"[COMPRESS] {debate['topic']} ({len(transcript)} chars)...")
    try:
        data = compress_transcript(transcript, API_KEY, model=MODEL, base_url=BASE_URL)
    except Exception as e:
        print(f"[FAIL] Compress error: {e}")
        continue

    print(f"[INDEX] {debate['topic']}...")
    debate_id = kb.add_debate(data, transcript=transcript)
    print(f"[OK] {debate['topic']} → {debate_id}")

print(f"\nDone. KB now has {kb.count()} debates, {kb.count_chunks()} chunks.")
