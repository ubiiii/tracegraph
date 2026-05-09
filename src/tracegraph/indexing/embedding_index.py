"""Optional embedding index."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from tracegraph.data.models import Chunk, RetrievedNode
from tracegraph.utils.io import read_pickle, write_pickle


class EmbeddingIndex:
    """Sentence-transformers backed dense retrieval with graceful fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = None
        self.matrix: np.ndarray | None = None
        self.chunks: list[Chunk] = []
        self.available = False
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
            self.available = True
        except Exception:  # noqa: BLE001
            self.available = False

    def build(self, chunks: list[Chunk], corpus_hash: str | None = None) -> None:
        """Build embedding matrix if dependency is available."""
        self.chunks = chunks
        if not self.available or self.model is None:
            self.matrix = None
            return
        self.matrix = self.model.encode([c.text for c in chunks], convert_to_numpy=True)

    def search(self, query: str, top_k: int) -> list[RetrievedNode]:
        """Search by cosine similarity; return [] when unavailable."""
        if not query.strip() or top_k <= 0 or self.matrix is None or self.model is None:
            return []
        q = self.model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(q, self.matrix)[0]
        idxs = np.argsort(sims)[::-1][:top_k]
        out: list[RetrievedNode] = []
        for rank, idx in enumerate(idxs, start=1):
            chunk = self.chunks[int(idx)]
            score = float(sims[int(idx)])
            out.append(
                RetrievedNode(
                    node_id=chunk.node_id,
                    score=score,
                    retrieval_stage="seed",
                    seed_score=score,
                    rank=rank,
                    chunk=chunk,
                    score_breakdown={"embedding": score},
                    why_retrieved="Embedding similarity",
                )
            )
        return out

    def save(self, path: str) -> None:
        """Persist chunks and dense matrix."""
        payload = {
            "model_name": self.model_name,
            "chunks": [c.model_dump(mode="python") for c in self.chunks],
            "matrix": self.matrix,
        }
        write_pickle(path, payload)

    @classmethod
    def load(cls, path: str) -> "EmbeddingIndex":
        """Load saved dense index."""
        payload = read_pickle(path)
        inst = cls(model_name=payload["model_name"])
        inst.chunks = [Chunk.model_validate(c) for c in payload["chunks"]]
        inst.matrix = payload["matrix"]
        return inst
