"""HotpotQA adapter."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from tracegraph.data.models import Document, QAExample


def supporting_facts_to_gold_refs(example: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert supporting facts to normalized refs."""
    facts = example.get("supporting_facts", []) or []
    return [{"title": f[0], "sent_id": f[1]} for f in facts if isinstance(f, list) and len(f) >= 2]


def convert_hotpot_example_to_documents(example: dict[str, Any]) -> list[Document]:
    """Convert one Hotpot example context list to documents."""
    context = example.get("context", []) or []
    docs: list[Document] = []
    for idx, entry in enumerate(context):
        if not isinstance(entry, list) or len(entry) != 2:
            continue
        title, sents = entry
        text = " ".join(sents) if isinstance(sents, list) else str(sents)
        docs.append(Document(doc_id=f"{example.get('_id', 'ex')}_{idx}", title=str(title), text=text))
    return docs


def load_hotpotqa(path: str, limit: int | None = None, seed: int = 42) -> list[QAExample]:
    """Load HotpotQA-style JSON as QAExample records."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Hotpot file not found: {path}")
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("HotpotQA file must be a JSON list")
    records = payload
    if limit is not None:
        if limit <= 0:
            raise ValueError("limit must be > 0")
        rng = random.Random(seed)
        records = records if limit >= len(records) else rng.sample(records, limit)
    out: list[QAExample] = []
    for ex in records:
        out.append(
            QAExample(
                example_id=str(ex.get("_id", "")),
                question=str(ex.get("question", "")),
                answer=ex.get("answer", ""),
                supporting_facts=supporting_facts_to_gold_refs(ex),
                metadata={"type": ex.get("type", "unknown")},
            )
        )
    return out
