"""Corpus preprocessing: entities and keywords."""

from __future__ import annotations

import logging
import re
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer

from tracegraph.data.models import Chunk

LOGGER = logging.getLogger(__name__)


def extract_entities_text(text: str) -> list[str]:
    """Extract entities using spaCy with regex fallback."""
    if not text.strip():
        return []
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        entities = {ent.text.strip().lower() for ent in doc.ents if ent.text.strip()}
        return sorted(entities)
    except Exception:  # noqa: BLE001
        # Fallback: title-cased token groups
        cand = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        return sorted({c.lower() for c in cand})


def extract_keywords_tfidf(chunks: list[Chunk], top_k: int) -> dict[str, list[str]]:
    """Extract top-k keywords per chunk from corpus-level TF-IDF."""
    if not chunks:
        return {}
    if top_k <= 0:
        return {c.node_id: [] for c in chunks}
    docs = [c.normalized_text for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(docs)
    vocab = vectorizer.get_feature_names_out()
    out: dict[str, list[str]] = {}
    for row_idx, chunk in enumerate(chunks):
        row = matrix.getrow(row_idx)
        if row.nnz == 0:
            out[chunk.node_id] = []
            continue
        pairs = sorted(zip(row.indices, row.data), key=lambda x: x[1], reverse=True)[:top_k]
        out[chunk.node_id] = [vocab[idx] for idx, _ in pairs]
    return out


def enrich_chunks(chunks: list[Chunk], top_k_keywords: int = 8) -> list[Chunk]:
    """Add entities and keywords in place and return chunks."""
    kw_map = extract_keywords_tfidf(chunks, top_k_keywords)
    for chunk in chunks:
        chunk.entities = extract_entities_text(chunk.text)
        chunk.keywords = kw_map.get(chunk.node_id, [])
        if chunk.summary is None:
            words = chunk.text.split()
            chunk.summary = " ".join(words[: min(20, len(words))])
    return chunks


def top_terms(texts: list[str], top_k: int = 10) -> list[str]:
    """Return token-frequency top terms for diagnostics."""
    counts: Counter[str] = Counter()
    for t in texts:
        counts.update(re.findall(r"\b\w+\b", t.lower()))
    return [term for term, _ in counts.most_common(top_k)]
