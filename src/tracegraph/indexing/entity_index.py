"""Entity index over chunk entities."""

from __future__ import annotations

from collections import defaultdict

from tracegraph.data.models import Chunk, RetrievedNode
from tracegraph.data.preprocess import extract_entities_text
from tracegraph.utils.io import read_pickle, write_pickle


class EntityIndex:
    """Entity-to-node index."""

    def __init__(self) -> None:
        self.entity_to_nodes: dict[str, set[str]] = defaultdict(set)
        self.chunk_map: dict[str, Chunk] = {}
        self.corpus_hash: str | None = None

    def build(self, chunks: list[Chunk], corpus_hash: str | None = None) -> None:
        """Build entity lookup map from chunks."""
        self.entity_to_nodes = defaultdict(set)
        self.chunk_map = {c.node_id: c for c in chunks}
        self.corpus_hash = corpus_hash
        for chunk in chunks:
            for ent in set(chunk.entities):
                self.entity_to_nodes[ent.lower()].add(chunk.node_id)

    def extract_entities_from_text(self, text: str) -> list[str]:
        """Extract canonical entities from query text."""
        return extract_entities_text(text)

    def search(self, query_text: str, top_k: int) -> list[RetrievedNode]:
        """Search by entity overlap count."""
        if top_k <= 0:
            return []
        entities = self.extract_entities_from_text(query_text)
        if not entities:
            return []
        scores: dict[str, float] = defaultdict(float)
        for ent in entities:
            for node_id in self.entity_to_nodes.get(ent.lower(), set()):
                scores[node_id] += 1.0
        ranked = sorted(scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:top_k]
        return [
            RetrievedNode(
                node_id=node_id,
                score=score,
                retrieval_stage="seed",
                seed_score=score,
                rank=i + 1,
                chunk=self.chunk_map[node_id],
                score_breakdown={"entity_overlap": score},
                why_retrieved="Shared query entities",
            )
            for i, (node_id, score) in enumerate(ranked)
        ]

    def save(self, path: str) -> None:
        """Persist entity index."""
        payload = {
            "entity_to_nodes": {k: sorted(v) for k, v in self.entity_to_nodes.items()},
            "chunks": {k: v.model_dump(mode="python") for k, v in self.chunk_map.items()},
            "corpus_hash": self.corpus_hash,
        }
        write_pickle(path, payload)

    @classmethod
    def load(cls, path: str) -> "EntityIndex":
        """Load index from disk."""
        payload = read_pickle(path)
        inst = cls()
        inst.entity_to_nodes = defaultdict(set, {k: set(v) for k, v in payload["entity_to_nodes"].items()})
        inst.chunk_map = {k: Chunk.model_validate(v) for k, v in payload["chunks"].items()}
        inst.corpus_hash = payload.get("corpus_hash")
        return inst
