"""Novelty and redundancy scoring."""

from __future__ import annotations

import re

from tracegraph.data.models import Chunk


def jaccard_token_overlap(a: str, b: str) -> float:
    """Compute token overlap ratio."""
    sa = set(re.findall(r"\w+", a.lower()))
    sb = set(re.findall(r"\w+", b.lower()))
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def entity_overlap_score(a_entities: list[str], b_entities: list[str]) -> float:
    """Compute entity overlap ratio."""
    sa, sb = set(a_entities), set(b_entities)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def compute_novelty(candidate: Chunk, selected_chunks: list[Chunk], config) -> float:
    """Higher is better novelty contribution."""
    if not selected_chunks:
        return 1.0
    overlap_scores = [
        0.7 * jaccard_token_overlap(candidate.normalized_text, c.normalized_text) + 0.3 * entity_overlap_score(candidate.entities, c.entities)
        for c in selected_chunks
    ]
    max_overlap = max(overlap_scores) if overlap_scores else 0.0
    return max(0.0, 1.0 - max_overlap)
