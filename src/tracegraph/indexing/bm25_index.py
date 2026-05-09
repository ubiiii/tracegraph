"""BM25 index wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from tracegraph.data.models import Chunk, RetrievedNode
from tracegraph.utils.io import read_pickle, write_pickle


@dataclass
class BM25Index:
    """BM25 index with persistence."""

    chunks: list[Chunk] | None = None
    tokenized: list[list[str]] | None = None
    bm25: BM25Okapi | None = None
    corpus_hash: str | None = None

    def build(self, chunks: list[Chunk], corpus_hash: str | None = None) -> None:
        """Build BM25 index over chunks."""
        self.chunks = chunks
        self.tokenized = [c.normalized_text.split() for c in chunks]
        self.bm25 = BM25Okapi(self.tokenized)
        self.corpus_hash = corpus_hash

    def is_built(self) -> bool:
        """Return whether index is ready."""
        return self.bm25 is not None and self.chunks is not None

    def search(self, query: str, top_k: int) -> list[RetrievedNode]:
        """Search index and return top retrieved nodes."""
        if not self.is_built():
            raise RuntimeError("BM25 index must be built before search")
        if not query.strip() or top_k <= 0:
            return []
        assert self.bm25 is not None
        assert self.chunks is not None
        scores = self.bm25.get_scores(query.lower().split())
        pairs = sorted(enumerate(scores), key=lambda x: (x[1], self.chunks[x[0]].node_id), reverse=True)[:top_k]
        out: list[RetrievedNode] = []
        for rank, (idx, score) in enumerate(pairs, start=1):
            chunk = self.chunks[idx]
            out.append(
                RetrievedNode(
                    node_id=chunk.node_id,
                    score=float(score),
                    retrieval_stage="seed",
                    seed_score=float(score),
                    rank=rank,
                    chunk=chunk,
                    score_breakdown={"bm25": float(score)},
                    why_retrieved="High BM25 relevance",
                )
            )
        return out

    def save(self, path: str) -> None:
        """Persist index state."""
        payload: dict[str, Any] = {"chunks": [c.model_dump(mode="python") for c in self.chunks or []], "corpus_hash": self.corpus_hash}
        write_pickle(path, payload)

    @classmethod
    def load(cls, path: str) -> "BM25Index":
        """Load index from disk and rebuild in-memory BM25 object."""
        payload = read_pickle(path)
        chunks = [Chunk.model_validate(c) for c in payload.get("chunks", [])]
        idx = cls()
        idx.build(chunks, corpus_hash=payload.get("corpus_hash"))
        return idx
