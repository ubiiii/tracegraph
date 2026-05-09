"""Load and save document corpora."""

from __future__ import annotations

import json
from pathlib import Path

from tracegraph.data.models import Document
from tracegraph.utils.hashing import hash_text
from tracegraph.utils.io import read_jsonl, write_jsonl


def load_documents_from_directory(path: str) -> list[Document]:
    """Load .txt/.md/.json/.jsonl files into Document objects."""
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Input directory not found: {path}")
    docs: list[Document] = []
    for file in sorted(root.iterdir()):
        if file.is_dir():
            continue
        suffix = file.suffix.lower()
        if suffix in {".txt", ".md"}:
            text = file.read_text(encoding="utf-8")
            docs.append(Document(doc_id=hash_text(str(file))[:12], title=file.stem, text=text, source_path=str(file)))
        elif suffix == ".json":
            payload = json.loads(file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                docs.append(
                    Document(
                        doc_id=payload.get("doc_id", hash_text(str(file))[:12]),
                        title=payload.get("title", file.stem),
                        text=payload.get("text", ""),
                        metadata=payload.get("metadata", {}),
                        source_path=str(file),
                    )
                )
        elif suffix == ".jsonl":
            for row in read_jsonl(str(file)):
                docs.append(
                    Document(
                        doc_id=row.get("doc_id", hash_text(str(file) + row.get("title", ""))[:12]),
                        title=row.get("title", "untitled"),
                        text=row.get("text", ""),
                        metadata=row.get("metadata", {}),
                        source_path=str(file),
                    )
                )
    return docs


def load_jsonl_corpus(path: str) -> list[Document]:
    """Load document corpus from JSONL."""
    rows = read_jsonl(path)
    return [Document.model_validate(r) for r in rows]


def save_documents_jsonl(path: str, docs: list[Document]) -> None:
    """Save corpus as JSONL."""
    write_jsonl(path, [d.model_dump(mode="python") for d in docs])
