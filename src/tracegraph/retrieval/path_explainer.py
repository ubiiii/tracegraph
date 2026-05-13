"""Retrieval path explanation."""

from __future__ import annotations

from tracegraph.data.models import RetrievedNode, TraversalPath


def collect_path_hops(retrieved_nodes: list[RetrievedNode], max_paths: int = 3) -> list[list[str]]:
    """Per-path hop labels for UI (shared entities, edge types, etc.)."""
    out: list[list[str]] = []
    for r in retrieved_nodes:
        p = r.path
        if p is None or not p.edge_sequence:
            continue
        if p.hop_descriptions and len(p.hop_descriptions) == len(p.edge_sequence):
            out.append(list(p.hop_descriptions[:5]))
        else:
            out.append(list(p.edge_sequence[:5]))
        if len(out) >= max_paths:
            break
    return out


def format_single_path(path: TraversalPath) -> str:
    """Format one traversal path as natural-language explanation."""
    if not path.edge_sequence:
        return f"Started and stayed at seed node {path.start_node_id}."
    if path.hop_descriptions and len(path.hop_descriptions) == len(path.edge_sequence):
        hops = " -> ".join(path.hop_descriptions[:5])
    else:
        hops = " -> ".join(path.edge_sequence[:5])
    return f"Started at {path.start_node_id}, traversed via {hops}, reached {path.end_node_id}."


def explain_retrieval_paths(retrieved_nodes: list[RetrievedNode], max_paths: int = 3) -> str:
    """Explain top retrieval paths."""
    paths = [r.path for r in retrieved_nodes if r.path is not None]
    if not paths:
        return "No traversal path available; retrieval was seed-only or empty."
    lines = [format_single_path(p) for p in paths[:max_paths]]
    return "\n".join(lines)
