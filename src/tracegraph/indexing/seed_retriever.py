"""Fused seed retrieval."""

from __future__ import annotations

from collections import defaultdict

from tracegraph.data.models import RetrievedNode


def _minmax(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class SeedRetriever:
    """Fused seed retriever over BM25/entity/embedding sources."""

    def __init__(self, bm25_index, entity_index=None, embedding_index=None, weights: dict[str, float] | None = None) -> None:
        self.bm25_index = bm25_index
        self.entity_index = entity_index
        self.embedding_index = embedding_index
        self.weights = weights or {"bm25": 0.6, "entity": 0.2, "embedding": 0.2}

    def retrieve(
        self,
        query: str,
        top_k: int,
        use_bm25: bool = True,
        use_entities: bool = True,
        use_embeddings: bool = False,
    ) -> list[RetrievedNode]:
        """Retrieve fused seeds with score normalization and dedup."""
        if not (use_bm25 or use_entities or use_embeddings):
            raise ValueError("All retrieval sources disabled")
        sources: dict[str, list[RetrievedNode]] = {}
        if use_bm25 and self.bm25_index is not None:
            sources["bm25"] = self.bm25_index.search(query, top_k=top_k * 2)
        if use_entities and self.entity_index is not None:
            sources["entity"] = self.entity_index.search(query, top_k=top_k * 2)
        if use_embeddings and self.embedding_index is not None:
            sources["embedding"] = self.embedding_index.search(query, top_k=top_k * 2)

        by_source = {name: {n.node_id: n.score for n in nodes} for name, nodes in sources.items()}
        norm = {name: _minmax(scores) for name, scores in by_source.items()}
        merged_scores: dict[str, float] = defaultdict(float)
        exemplar: dict[str, RetrievedNode] = {}
        for name, nodes in sources.items():
            w = self.weights.get(name, 0.0)
            for n in nodes:
                merged_scores[n.node_id] += w * norm[name].get(n.node_id, 0.0)
                exemplar.setdefault(n.node_id, n)
        ranked = sorted(merged_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:top_k]
        results: list[RetrievedNode] = []
        for rank, (node_id, score) in enumerate(ranked, start=1):
            base = exemplar[node_id]
            results.append(
                RetrievedNode(
                    node_id=node_id,
                    score=float(score),
                    retrieval_stage="seed",
                    seed_score=float(score),
                    rank=rank,
                    chunk=base.chunk,
                    score_breakdown={k: norm[k].get(node_id, 0.0) for k in norm},
                    why_retrieved="Fused seed score across enabled retrievers",
                )
            )
        return results
