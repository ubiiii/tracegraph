"""Document chunking logic."""

from __future__ import annotations

import re

from tracegraph.data.models import Chunk, Document
from tracegraph.utils.text import clean_whitespace, normalize_text, safe_sentence_split


def estimate_token_count(text: str) -> int:
    """Estimate token count with whitespace heuristic."""
    return max(1, len(text.split())) if text.strip() else 0


def split_text_into_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: list[str] | None = None,
) -> list[tuple[str, int, int]]:
    """Split text into overlapping chunks and return text + char offsets."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >=0 and < chunk_size")
    text = text or ""
    if not text.strip():
        return []

    separators = separators or ["\n\n", ". "]
    words = text.split()
    step = chunk_size - chunk_overlap
    spans: list[tuple[str, int, int]] = []
    idx = 0
    while idx < len(words):
        window_words = words[idx : idx + chunk_size]
        chunk_text = " ".join(window_words).strip()
        if chunk_text:
            start_char = text.find(window_words[0]) if window_words else 0
            if start_char < 0:
                start_char = 0
            end_char = start_char + len(chunk_text)
            spans.append((chunk_text, start_char, end_char))
        idx += step
    return spans


def chunk_document(
    document: Document,
    chunk_size: int,
    chunk_overlap: int,
    preserve_paragraphs: bool = True,
) -> list[Chunk]:
    """Chunk a document into deterministic chunk nodes."""
    raw = document.text or ""
    if not raw.strip():
        return []
    text = clean_whitespace(raw) if not preserve_paragraphs else re.sub(r"\n{3,}", "\n\n", raw).strip()
    pieces = split_text_into_chunks(text, chunk_size, chunk_overlap)
    chunks: list[Chunk] = []
    for i, (chunk_text, start, end) in enumerate(pieces):
        if not chunk_text.strip():
            continue
        chunks.append(
            Chunk(
                node_id=f"{document.doc_id}::c{i}",
                doc_id=document.doc_id,
                chunk_id=i,
                title=document.title,
                text=chunk_text,
                normalized_text=normalize_text(chunk_text).lower(),
                token_count=estimate_token_count(chunk_text),
                start_char=start,
                end_char=end,
                entities=[],
                keywords=[],
                summary=safe_sentence_split(chunk_text)[0] if safe_sentence_split(chunk_text) else None,
                metadata=document.metadata.copy(),
            )
        )
    return chunks
