"""Data models for the debate analysis system."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class QuickView:
    one_sentence_summary: str = ""
    affirmative_top3: list[str] = field(default_factory=list)
    negative_top3: list[str] = field(default_factory=list)
    hottest_clash: str = ""
    key_unresolved: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Claim:
    id: str
    content: str
    side: str = ""  # 正方/反方 — 提出该论点的辩方
    evidence: str = ""
    rebuts_claim_id: Optional[str] = None
    responded: bool = False
    response_summary: str = ""


@dataclass
class DebateRound:
    round_name: str  # 立论/质询/自由辩论/结辩
    speaker: str
    side: str  # 正方/反方
    time_range: str = ""
    content_summary: str = ""
    claims: list[Claim] = field(default_factory=list)


@dataclass
class UnresolvedIssue:
    issue: str
    raised_by: str
    importance: str = "中"  # 高/中/低


@dataclass
class FactualClaim:
    claim: str
    speaker: str
    has_evidence: bool = False
    evidence_detail: str = ""


@dataclass
class StructuredDebate:
    topic: str = ""
    affirmative_side: str = ""
    negative_side: str = ""
    quick_view: Optional[QuickView] = None
    rounds: list[DebateRound] = field(default_factory=list)
    unresolved_issues: list[UnresolvedIssue] = field(default_factory=list)
    factual_claims: list[FactualClaim] = field(default_factory=list)
    raw_transcript: str = ""

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization / Streamlit session state."""
        result = {
            "topic": self.topic,
            "affirmative_side": self.affirmative_side,
            "negative_side": self.negative_side,
            "quick_view": asdict(self.quick_view) if self.quick_view else None,
            "rounds": [asdict(r) for r in self.rounds],
            "unresolved_issues": [asdict(u) for u in self.unresolved_issues],
            "factual_claims": [asdict(f) for f in self.factual_claims],
            "raw_transcript": self.raw_transcript,
        }
        # Convert claims within rounds
        for i, round_data in enumerate(result["rounds"]):
            round_data["claims"] = [asdict(c) for c in self.rounds[i].claims]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "StructuredDebate":
        """Reconstruct from dict."""
        qv = None
        if data.get("quick_view"):
            try:
                qv = QuickView(**data["quick_view"])
            except TypeError:
                # LLM may omit fields — fill missing with defaults
                qv_data = {
                    "one_sentence_summary": "",
                    "affirmative_top3": [],
                    "negative_top3": [],
                    "hottest_clash": "",
                    "key_unresolved": "",
                    "keywords": [],
                }
                qv_data.update(data["quick_view"])
                qv = QuickView(**qv_data)

        rounds = []
        for r in data.get("rounds", []):
            claims = [Claim(**c) for c in r.get("claims", [])]
            r_copy = {k: v for k, v in r.items() if k != "claims"}
            rounds.append(DebateRound(claims=claims, **r_copy))

        unresolved = [UnresolvedIssue(**u) for u in data.get("unresolved_issues", [])]
        factual = [FactualClaim(**f) for f in data.get("factual_claims", [])]

        return cls(
            topic=data.get("topic", ""),
            affirmative_side=data.get("affirmative_side", ""),
            negative_side=data.get("negative_side", ""),
            quick_view=qv,
            rounds=rounds,
            unresolved_issues=unresolved,
            factual_claims=factual,
            raw_transcript=data.get("raw_transcript", ""),
        )
