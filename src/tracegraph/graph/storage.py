"""Graph persistence utilities."""

from __future__ import annotations

import networkx as nx

from tracegraph.utils.io import read_pickle, write_pickle


def save_graph(graph: nx.MultiDiGraph, path: str) -> None:
    """Persist graph object."""
    write_pickle(path, graph)


def load_graph(path: str) -> nx.MultiDiGraph:
    """Load graph object."""
    graph = read_pickle(path)
    if not isinstance(graph, nx.MultiDiGraph):
        raise ValueError("Loaded graph is not a networkx.MultiDiGraph")
    return graph
