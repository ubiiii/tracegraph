"""Evidence quality metrics."""

from __future__ import annotations

from tracegraph.data.models import RetrievedNode


def supporting_fact_coverage(retrieved_nodes: list[RetrievedNode], gold_supporting_facts: list[dict]) -> float:
    """Approximate supporting fact title hit rate."""
    if not gold_supporting_facts:
        return 0.0
    gold_titles = {g.get("title", "").lower() for g in gold_supporting_facts}
    ret_titles = {r.chunk.title.lower() for r in retrieved_nodes}
    return len(gold_titles & ret_titles) / max(1, len(gold_titles))


def document_recall_at_k(retrieved_nodes: list[RetrievedNode], gold_titles: list[str]) -> float:
    """Document-level recall of gold titles."""
    if not gold_titles:
        return 0.0
    ret_titles = {r.chunk.title.lower() for r in retrieved_nodes}
    gt = {t.lower() for t in gold_titles}
    return len(ret_titles & gt) / max(1, len(gt))


def citation_hit_rate(answer_output, gold_supporting_facts: list[dict]) -> float:
    """Approximate citation hit from source lines containing title strings."""
    if not gold_supporting_facts:
        return 0.0
    source_text = " ".join(answer_output.sources).lower()
    gold_titles = {g.get("title", "").lower() for g in gold_supporting_facts}
    hits = sum(1 for t in gold_titles if t and t in source_text)
    return hits / max(1, len(gold_titles))
