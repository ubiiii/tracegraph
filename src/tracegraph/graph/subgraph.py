"""Subgraph extraction helpers."""

from __future__ import annotations

import networkx as nx


def induced_subgraph(graph: nx.MultiDiGraph, node_ids: list[str]) -> nx.MultiDiGraph:
    """Return induced subgraph for selected nodes."""
    return graph.subgraph(node_ids).copy()
