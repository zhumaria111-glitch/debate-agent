"""RAG knowledge base for cross-debate analysis.

Three-layer storage:
- transcript-level (PRIMARY): cleaned transcript chunks (~500 chars) — for
  detailed semantic search over the actual debate text
- claim-level (INDEX): extracted claims with evidence — precise lookup of
  specific arguments
- debate-level (NAVIGATION): topic + stance overview — answering "which
  debates discussed X?"

Supports hybrid search: dense (semantic embedding) + sparse (keyword BM25).
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

from src.models import StructuredDebate


EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 500   # characters per transcript chunk
CHUNK_OVERLAP = 100


class KnowledgeBase:
    def __init__(self, persist_dir: str = "data/knowledge_base"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )

        # Primary: full transcript chunks
        self.transcripts = self.client.get_or_create_collection(
            name="transcripts",
            embedding_function=self.ef,
            metadata={"description": "Transcript chunks (~500 chars, overlap 100)"},
        )
        # Index: extracted claims
        self.claims = self.client.get_or_create_collection(
            name="claims",
            embedding_function=self.ef,
            metadata={"description": "Extracted claims with evidence"},
        )
        # Navigation: debate overviews
        self.debates = self.client.get_or_create_collection(
            name="debates",
            embedding_function=self.ef,
            metadata={"description": "Full debate overviews"},
        )

    # ── Indexing ────────────────────────────────────────────────────────

    def add_debate(
        self, debate: StructuredDebate, transcript: str = ""
    ) -> str:
        """Index a debate. Pass the cleaned transcript for full-text search."""
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_topic = re.sub(r"[^\w一-鿿]+", "_", debate.topic).strip("_")
        debate_id = f"{safe_topic}_{ts}"

        # Check for duplicate
        existing = self.debates.get()
        for i, mid in enumerate(existing["metadatas"]):
            if mid and mid.get("topic") == debate.topic:
                return existing["ids"][i]

        # 1. Transcript chunks (primary retrieval)
        if transcript:
            chunks = _chunk_text(transcript)
            for i, chunk in enumerate(chunks):
                # Prepend debate topic as context for the chunk
                chunk_text = f"[{debate.topic}] {chunk}"
                self.transcripts.add(
                    ids=[f"{debate_id}_t{i}"],
                    documents=[chunk_text],
                    metadatas=[{
                        "debate_id": debate_id,
                        "topic": debate.topic,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }],
                )

        # 2. Claim-level index
        for i, r in enumerate(debate.rounds):
            for j, c in enumerate(r.claims):
                claim_text = f"[{debate.topic}] {c.side}主张：{c.content}"
                if c.evidence:
                    claim_text += f" | 证据：{c.evidence}"
                self.claims.add(
                    ids=[f"{debate_id}_c{i}_{j}"],
                    documents=[claim_text],
                    metadatas=[{
                        "debate_id": debate_id,
                        "topic": debate.topic,
                        "claim_id": c.id,
                        "side": c.side,
                        "round_name": r.round_name,
                        "content": c.content,
                        "evidence": c.evidence or "",
                        "responded": c.responded,
                        "rebuts": c.rebuts_claim_id or "",
                    }],
                )

        # 3. Debate-level overview
        debate_text = (
            f"辩题：{debate.topic}\n"
            f"正方立场：{debate.affirmative_side}\n"
            f"反方立场：{debate.negative_side}"
        )
        if debate.quick_view:
            debate_text += f"\n总结：{debate.quick_view.one_sentence_summary}"
        self.debates.add(
            ids=[debate_id],
            documents=[debate_text],
            metadatas=[{"debate_id": debate_id, "topic": debate.topic}],
        )

        # Persist full debate JSON + transcript for display
        full_dir = os.path.join(self.persist_dir, "full_debates")
        os.makedirs(full_dir, exist_ok=True)
        payload = debate.to_dict()
        payload["_transcript"] = transcript
        with open(os.path.join(full_dir, f"{debate_id}.json"), "w") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return debate_id

    # ── Retrieval ───────────────────────────────────────────────────────

    def search(self, query: str, n: int = 10) -> dict:
        """Search all layers. Transcript chunks are primary."""
        t_results = self.transcripts.query(query_texts=[query], n_results=n)
        c_results = self.claims.query(query_texts=[query], n_results=max(3, n // 3))
        d_results = self.debates.query(query_texts=[query], n_results=3)

        keywords = _extract_keywords(query)
        if keywords:
            t_results = _keyword_boost(t_results, keywords)
            c_results = _keyword_boost(c_results, keywords)

        return {
            "transcripts": t_results,
            "claims": c_results,
            "debates": d_results,
        }

    # ── Management ──────────────────────────────────────────────────────

    def list_debates(self) -> list[dict]:
        if self.debates.count() == 0:
            return []
        results = self.debates.get()
        return [
            {
                "debate_id": results["ids"][i],
                "topic": results["metadatas"][i].get("topic", ""),
                "summary": (results["documents"] or [""])[i],
            }
            for i in range(len(results["ids"]))
        ]

    def get_debate(self, debate_id: str) -> Optional[dict]:
        path = os.path.join(self.persist_dir, "full_debates", f"{debate_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def count(self) -> int:
        return self.debates.count()

    def count_chunks(self) -> int:
        return self.transcripts.count()

    def remove_debate(self, debate_id: str) -> None:
        for coll in [self.transcripts, self.claims, self.debates]:
            existing = coll.get()
            to_delete = [i for i in existing["ids"] if i.startswith(debate_id)]
            if to_delete:
                coll.delete(ids=to_delete)
        path = os.path.join(self.persist_dir, "full_debates", f"{debate_id}.json")
        if os.path.exists(path):
            os.remove(path)

    # ── RAG context builder ─────────────────────────────────────────────

    def build_context(self, query: str, n: int = 8) -> str:
        """Build context for RAG: transcript chunks (primary) + claims."""
        results = self.search(query, n=n)
        parts = []
        seen = set()

        # Primary: transcript chunks
        t_hits = results["transcripts"]
        if t_hits.get("documents") and t_hits["documents"][0]:
            parts.append("## 相关原文段落")
            for i, doc in enumerate(t_hits["documents"][0]):
                key = doc[:80]
                if key not in seen:
                    seen.add(key)
                    meta = t_hits["metadatas"][0][i] if t_hits["metadatas"] else {}
                    topic = meta.get("topic", "")
                    parts.append(f"### {topic}\n{doc}")

        # Supporting: claims as quick reference
        c_hits = results["claims"]
        if c_hits.get("documents") and c_hits["documents"][0]:
            parts.append("\n## 相关论点索引")
            for i, doc in enumerate(c_hits["documents"][0]):
                key = doc[:60]
                if key not in seen:
                    seen.add(key)
                    parts.append(f"- {doc}")

        return "\n".join(parts) if parts else "知识库中暂无相关内容。"


# ── Chunking ──────────────────────────────────────────────────────────

def _chunk_text(text: str) -> list[str]:
    """Split transcript into overlapping chunks at paragraph boundaries.

    Target ~CHUNK_SIZE chars per chunk with ~CHUNK_OVERLAP overlap.
    Splits at double-newline (paragraph) first, then at single-newline
    if a paragraph exceeds chunk_size.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) < CHUNK_SIZE:
            current += para + "\n\n" if current else para
        else:
            if current.strip():
                chunks.append(current.strip())
            # If single paragraph exceeds chunk size, split it further
            if len(para) > CHUNK_SIZE:
                current = para
                while len(current) > CHUNK_SIZE:
                    # Find nearest sentence break within range
                    split_at = current.rfind("。", 0, CHUNK_SIZE)
                    if split_at == -1:
                        split_at = CHUNK_SIZE
                    else:
                        split_at += 1  # include the period
                    chunks.append(current[:split_at].strip())
                    # Overlap: step back ~OVERLAP chars
                    start = split_at - CHUNK_OVERLAP
                    if start <= 0:
                        start = split_at  # no room for overlap, just advance
                    current = current[start:]
            else:
                current = para

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ── Helpers ────────────────────────────────────────────────────────────

def _extract_keywords(query: str) -> list[str]:
    """Extract meaningful keywords for sparse retrieval boost."""
    stops = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一",
             "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
             "没有", "看", "好", "自己", "这", "吗", "呢", "吧", "啊", "什么",
             "the", "is", "a", "an", "of", "to", "in", "and", "for", "on",
             "that", "this", "it", "with", "as", "by", "at", "from", "or"}
    tokens = re.findall(r"[一-鿿]{2,}|[A-Za-z]{3,}", query)
    return [t for t in tokens if t.lower() not in stops]


def _keyword_boost(results: dict, keywords: list[str]) -> dict:
    """Re-rank results: exact keyword matches float to top."""
    if not results.get("documents") or not results["documents"][0]:
        return results
    docs = results["documents"][0]
    metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
    ids = results["ids"][0]
    dists = results["distances"][0] if results.get("distances") else [0] * len(docs)

    scored = []
    for i, doc in enumerate(docs):
        score = sum(1 for kw in keywords if kw.lower() in doc.lower())
        adjusted = dists[i] - score * 0.15
        scored.append((adjusted, doc, metas[i], ids[i]))

    scored.sort(key=lambda x: x[0])
    return {
        "ids": [[s[3] for s in scored]],
        "documents": [[s[1] for s in scored]],
        "metadatas": [[s[2] for s in scored]],
        "distances": [[s[0] for s in scored]],
    }
