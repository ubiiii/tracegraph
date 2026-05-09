"""Traversal scoring helpers."""

from __future__ import annotations

import math

from tracegraph.data.models import Chunk
from tracegraph.retrieval.novelty import compute_novelty


def query_relevance_score(query: str, chunk: Chunk, bm25_hint: float | None = None, embedding_hint: float | None = None) -> float:
    """Compute lightweight query relevance with optional hints."""
    q_tokens = set(query.lower().split())
    c_tokens = set(chunk.normalized_text.split())
    overlap = len(q_tokens & c_tokens) / max(1, len(q_tokens))
    return float(overlap + (bm25_hint or 0.0) * 0.2 + (embedding_hint or 0.0) * 0.2)


def edge_weight_score(edge_data: dict) -> float:
    """Return edge weight from metadata."""
    return float(edge_data.get("weight", 0.0))


def compute_depth_penalty(depth: int, coefficient: float) -> float:
    """Depth penalty term."""
    return max(0.0, coefficient * depth)


def novelty_penalty(candidate: Chunk, selected_chunks: list[Chunk], config) -> float:
    """Convert novelty to penalty."""
    nov = compute_novelty(candidate, selected_chunks, config)
    return max(0.0, 1.0 - nov)


def combined_traversal_score(
    query: str,
    chunk: Chunk,
    edge_data: dict,
    depth: int,
    selected_chunks: list[Chunk],
    config,
) -> dict[str, float]:
    """Compute full score and breakdown for traversal candidate."""
    rel = query_relevance_score(query, chunk)
    edge = edge_weight_score(edge_data)
    nov_pen = novelty_penalty(chunk, selected_chunks, config)
    dep_pen = compute_depth_penalty(depth, config.traversal.depth_penalty_weight)
    total = (
        config.traversal.relevance_weight * rel
        + config.traversal.edge_weight * edge
        + config.traversal.novelty_weight * (1.0 - nov_pen)
        - dep_pen
    )
    if math.isnan(total):
        total = -1e9
    return {
        "query_relevance": rel,
        "edge_contribution": edge,
        "novelty_penalty": nov_pen,
        "depth_penalty": dep_pen,
        "total": total,
    }
