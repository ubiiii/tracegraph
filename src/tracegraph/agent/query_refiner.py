"""Query refinement logic."""

from __future__ import annotations

from tracegraph.data.models import MissingEvidenceDecision, RetrievedNode


class QueryRefiner:
    """Refine query with missing concepts and evidence hints."""

    def refine(self, question: str, missing_evidence_decision: MissingEvidenceDecision, prior_context: list[RetrievedNode], llm) -> str:
        """Return refined query or original question."""
        if not missing_evidence_decision.needs_callback:
            return question
        extra_terms: list[str] = []
        extra_terms.extend(missing_evidence_decision.missing_concepts)
        for node in prior_context[:3]:
            extra_terms.extend(node.chunk.entities[:2])
            extra_terms.extend(node.chunk.keywords[:2])
        dedup = []
        seen = set()
        for term in [t.strip().lower() for t in extra_terms if t.strip()]:
            if term not in seen:
                seen.add(term)
                dedup.append(term)
        suffix = " ".join(dedup[:8])
        refined = f"{question} {suffix}".strip()
        return refined[:400]
