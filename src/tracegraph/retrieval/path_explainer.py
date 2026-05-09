"""Retrieval path explanation."""

from __future__ import annotations

from tracegraph.data.models import RetrievedNode, TraversalPath


def format_single_path(path: TraversalPath) -> str:
    """Format one traversal path as natural-language explanation."""
    if not path.edge_sequence:
        return f"Started and stayed at seed node {path.start_node_id}."
    hops = " -> ".join(f"{edge}" for edge in path.edge_sequence[:5])
    return f"Started at {path.start_node_id}, traversed via {hops}, reached {path.end_node_id}."


def explain_retrieval_paths(retrieved_nodes: list[RetrievedNode], max_paths: int = 3) -> str:
    """Explain top retrieval paths."""
    paths = [r.path for r in retrieved_nodes if r.path is not None]
    if not paths:
        return "No traversal path available; retrieval was seed-only or empty."
    lines = [format_single_path(p) for p in paths[:max_paths]]
    return "\n".join(lines)
