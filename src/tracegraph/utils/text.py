"""Text processing utilities."""

from __future__ import annotations

import re


def clean_whitespace(text: str) -> str:
    """Collapse repeated whitespace while preserving single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    """Normalize text for indexing while preserving core symbols."""
    return clean_whitespace(text.replace("\u00a0", " "))


def lowercase_for_index(text: str) -> str:
    """Lowercase text for token matching."""
    return normalize_text(text).lower()


def safe_sentence_split(text: str) -> list[str]:
    """Split into sentences using conservative regex fallback."""
    cleaned = normalize_text(text)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [p.strip() for p in parts if p.strip()]
