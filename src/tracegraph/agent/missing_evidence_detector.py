"""Missing evidence detection."""

from __future__ import annotations

import re

from tracegraph.data.models import MissingEvidenceDecision, RetrievedNode


class MissingEvidenceDetector:
    """Heuristic + optional LLM missing evidence detector."""

    def analyze(self, question: str, draft_answer: str, retrieved_context: list[RetrievedNode], llm) -> MissingEvidenceDecision:
        """Return callback decision."""
        q = question.lower()
        multi_hop_hint = any(k in q for k in ["and", "why", "justified", "which clause", "based on"])
        doc_count = len({n.chunk.doc_id for n in retrieved_context})
        uncertain = any(k in draft_answer.lower() for k in ["unknown", "unclear", "insufficient"])
        q_terms = {t for t in re.findall(r"\w+", q) if len(t) > 3}
        a_terms = {t for t in re.findall(r"\w+", draft_answer.lower()) if len(t) > 3}
        overlap_ratio = len(q_terms & a_terms) / max(1, len(q_terms))
        facet_mismatch = multi_hop_hint and overlap_ratio < 0.35
        needs = uncertain or (multi_hop_hint and doc_count < 2) or facet_mismatch or not retrieved_context
        reason = "insufficient evidence breadth/facet coverage" if needs else "evidence sufficient"
        missing: list[str] = []
        if "clause" in q and "clause" not in draft_answer.lower():
            missing.append("compliance clause")
        if "policy" in q and "policy" not in draft_answer.lower():
            missing.append("policy reference")
        return MissingEvidenceDecision(needs_callback=needs, reason=reason, missing_concepts=missing, confidence=0.7 if needs else 0.8)
