"""Stable hashing utilities."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_text(text: str) -> str:
    """Hash plain text using SHA256."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_document(doc: dict[str, Any]) -> str:
    """Hash a document mapping deterministically."""
    return hash_config_dict(doc)


def hash_chunks(chunks: list[dict[str, Any]]) -> str:
    """Hash chunk list by node id and normalized text."""
    signature = [{"node_id": c.get("node_id"), "normalized_text": c.get("normalized_text", "")} for c in chunks]
    return hash_config_dict(signature)


def hash_config_dict(data: Any) -> str:
    """Hash nested structures with sorted JSON serialization."""
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
