"""Graph edge builders."""

from __future__ import annotations

from collections import defaultdict

from tracegraph.data.models import Chunk
from tracegraph.graph.schema import EdgeType
from tracegraph.indexing.lexical_similarity import build_lexical_similarity_edges


def _shared_entity_display_names(a: Chunk, b: Chunk) -> list[str]:
    """Stable display strings for entities shared between two chunks (case-insensitive match)."""
    lower_to_canon: dict[str, str] = {}
    for c in (a, b):
        for e in c.entities:
            e = (e or "").strip()
            if not e:
                continue
            k = e.lower()
            if k not in lower_to_canon:
                lower_to_canon[k] = e
    a_low = {e.lower() for e in a.entities if (e or "").strip()}
    b_low = {e.lower() for e in b.entities if (e or "").strip()}
    return [lower_to_canon[k] for k in sorted(a_low & b_low)]


def build_next_edges(chunks: list[Chunk], weight: float = 0.8) -> list[dict]:
    """Link adjacent chunks in same document."""
    edges: list[dict] = []
    by_doc: dict[str, list[Chunk]] = defaultdict(list)
    for c in chunks:
        by_doc[c.doc_id].append(c)
    for doc_chunks in by_doc.values():
        doc_chunks = sorted(doc_chunks, key=lambda c: c.chunk_id)
        for i in range(len(doc_chunks) - 1):
            a, b = doc_chunks[i], doc_chunks[i + 1]
            edges.append({"source": a.node_id, "target": b.node_id, "edge_type": EdgeType.NEXT.value, "weight": weight, "metadata": {"reason": "adjacent"}})
            edges.append({"source": b.node_id, "target": a.node_id, "edge_type": EdgeType.NEXT.value, "weight": weight, "metadata": {"reason": "adjacent_reverse"}})
    return edges


def build_shared_entity_edges(chunks: list[Chunk], min_shared: int = 1, max_neighbors_per_node: int = 10) -> list[dict]:
    """Build edges from shared entity overlap."""
    inv: dict[str, set[str]] = defaultdict(set)
    chunk_map = {c.node_id: c for c in chunks}
    for c in chunks:
        for e in set(c.entities):
            inv[e.lower()].add(c.node_id)
    overlaps: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for ent, nodes in inv.items():
        if len(nodes) > 50:
            continue
        nlist = sorted(nodes)
        for i, a in enumerate(nlist):
            for b in nlist[i + 1 :]:
                overlaps[a][b] += 1
                overlaps[b][a] += 1
    edges: list[dict] = []
    for src, neigh in overlaps.items():
        ranked = sorted(neigh.items(), key=lambda x: (x[1], x[0]), reverse=True)
        for tgt, cnt in ranked[:max_neighbors_per_node]:
            if cnt < min_shared:
                continue
            ca, cb = chunk_map[src], chunk_map[tgt]
            shared_names = _shared_entity_display_names(ca, cb)
            edges.append(
                {
                    "source": src,
                    "target": tgt,
                    "edge_type": EdgeType.SHARED_ENTITY.value,
                    "weight": float(cnt),
                    "metadata": {"shared_count": cnt, "shared_entities": shared_names},
                }
            )
    return edges


def build_lexical_edges(chunks: list[Chunk], max_neighbors_per_node: int, min_similarity: float) -> list[dict]:
    """Build lexical similarity edges from sparse cosine neighbors."""
    return build_lexical_similarity_edges(chunks, max_neighbors=max_neighbors_per_node, min_similarity=min_similarity)


def build_relation_edges(chunks: list[Chunk]) -> list[dict]:
    """Build lightweight heuristic relation edges."""
    cues = ("because", "therefore", "depends on", "justified by")
    edges: list[dict] = []
    for src in chunks:
        lower = src.text.lower()
        if any(c in lower for c in cues):
            for tgt in chunks:
                if src.node_id == tgt.node_id:
                    continue
                if any(k in tgt.text.lower() for k in src.keywords[:2]):
                    edges.append(
                        {
                            "source": src.node_id,
                            "target": tgt.node_id,
                            "edge_type": EdgeType.RELATION.value,
                            "weight": 0.4,
                            "metadata": {"reason": "cue_phrase"},
                        }
                    )
                    break
    return edges
