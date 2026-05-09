"""Sparse lexical similarity helpers."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from tracegraph.data.models import Chunk


def compute_tfidf_matrix(chunks: list[Chunk]):
    """Compute TF-IDF matrix for chunks."""
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([c.normalized_text for c in chunks]) if chunks else None
    return vectorizer, matrix


def build_lexical_similarity_edges(chunks: list[Chunk], max_neighbors: int, min_similarity: float) -> list[dict]:
    """Create sparse lexical similarity edges."""
    if not chunks:
        return []
    _, matrix = compute_tfidf_matrix(chunks)
    if matrix is None:
        return []
    sims = cosine_similarity(matrix, matrix)
    edges: list[dict] = []
    for i, src in enumerate(chunks):
        neigh = sorted([(j, sims[i, j]) for j in range(len(chunks)) if j != i and sims[i, j] >= min_similarity], key=lambda x: x[1], reverse=True)
        for j, score in neigh[:max_neighbors]:
            edges.append(
                {
                    "source": src.node_id,
                    "target": chunks[j].node_id,
                    "edge_type": "LEXICAL_SIM",
                    "weight": float(score),
                    "metadata": {"similarity": float(score)},
                }
            )
    return edges
