"""TraceGraph builder."""

from __future__ import annotations

import time
from collections import Counter
from typing import Any

import networkx as nx

from tracegraph.data.chunking import chunk_document
from tracegraph.data.models import Chunk, Document
from tracegraph.data.preprocess import enrich_chunks
from tracegraph.graph.edge_builders import build_lexical_edges, build_next_edges, build_relation_edges, build_shared_entity_edges


class TraceGraphBuilder:
    """Build graph from documents/chunks."""

    def build(self, documents: list[Document], config: Any) -> tuple[nx.MultiDiGraph, list[Chunk], dict[str, Any]]:
        """Build graph from documents via chunking and enrichment."""
        chunks: list[Chunk] = []
        for doc in documents:
            chunks.extend(
                chunk_document(
                    doc,
                    chunk_size=config.chunking.chunk_size,
                    chunk_overlap=config.chunking.chunk_overlap,
                    preserve_paragraphs=config.chunking.preserve_paragraphs,
                )
            )
        enrich_chunks(chunks, top_k_keywords=config.keyword_extraction.get("top_k", 8))
        return self.build_from_chunks(chunks, config), chunks, self._stats_from_graph(self.build_from_chunks(chunks, config), len(documents), len(chunks), 0.0, config)

    def build_from_chunks(self, chunks: list[Chunk], config: Any) -> nx.MultiDiGraph:
        """Build graph directly from chunks."""
        graph = nx.MultiDiGraph()
        seen: set[str] = set()
        for chunk in chunks:
            if chunk.node_id in seen:
                raise ValueError(f"Duplicate chunk node_id: {chunk.node_id}")
            seen.add(chunk.node_id)
            graph.add_node(chunk.node_id, **chunk.model_dump(mode="python"))
        edge_types = set(config.graph.edge_types)
        edges: list[dict] = []
        if "NEXT" in edge_types:
            edges.extend(build_next_edges(chunks, weight=config.graph.next_weight))
        if "SHARED_ENTITY" in edge_types:
            edges.extend(
                build_shared_entity_edges(
                    chunks,
                    min_shared=config.graph.shared_entity_min,
                    max_neighbors_per_node=config.graph.shared_entity_max_neighbors,
                )
            )
        if "LEXICAL_SIM" in edge_types:
            edges.extend(
                build_lexical_edges(
                    chunks,
                    max_neighbors_per_node=config.graph.lexical_max_neighbors,
                    min_similarity=config.graph.lexical_min_similarity,
                )
            )
        if "RELATION" in edge_types and config.graph.relation_enabled:
            edges.extend(build_relation_edges(chunks))

        for edge in edges:
            if edge["source"] == edge["target"]:
                continue
            graph.add_edge(edge["source"], edge["target"], key=edge["edge_type"], **edge)
        graph.graph["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        return graph

    def _stats_from_graph(self, graph: nx.MultiDiGraph, n_docs: int, n_chunks: int, build_seconds: float, config: Any) -> dict[str, Any]:
        counts = Counter()
        for _, _, data in graph.edges(data=True):
            counts[data.get("edge_type", "unknown")] += 1
        return {
            "documents": n_docs,
            "chunks": n_chunks,
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "edge_counts": dict(counts),
            "isolated_nodes": len(list(nx.isolates(graph))),
            "avg_degree": float(sum(dict(graph.degree()).values()) / max(1, graph.number_of_nodes())),
            "max_degree": max(dict(graph.degree()).values()) if graph.number_of_nodes() else 0,
            "build_seconds": build_seconds,
            "edge_params": config.graph.model_dump(mode="python"),
        }
