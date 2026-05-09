"""Filesystem serialization helpers with atomic write support."""

from __future__ import annotations

import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any, Iterable

import yaml


def ensure_dir(path: str) -> Path:
    """Create directory and parents if missing."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _atomic_write(path: str, content: bytes) -> None:
    parent = Path(path).parent
    ensure_dir(str(parent))
    with tempfile.NamedTemporaryFile(delete=False, dir=parent) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    os.replace(tmp_path, path)


def atomic_write_text(path: str, text: str) -> None:
    """Atomically write text file."""
    _atomic_write(path, text.encode("utf-8"))


def atomic_write_bytes(path: str, data: bytes) -> None:
    """Atomically write bytes file."""
    _atomic_write(path, data)


def write_json(path: str, data: Any) -> None:
    """Write JSON with deterministic key ordering."""
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def read_json(path: str) -> Any:
    """Read JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: str, rows: Iterable[dict[str, Any]]) -> None:
    """Write JSONL records atomically."""
    payload = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    atomic_write_text(path, payload)


def read_jsonl(path: str) -> list[dict[str, Any]]:
    """Read JSONL with line-level error context."""
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}, line {idx}: {exc}") from exc
    return out


def write_pickle(path: str, obj: Any) -> None:
    """Write pickle atomically."""
    atomic_write_bytes(path, pickle.dumps(obj))


def read_pickle(path: str) -> Any:
    """Read pickle safely."""
    try:
        return pickle.loads(Path(path).read_bytes())
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Failed to read pickle: {path}") from exc


def write_yaml(path: str, data: Any) -> None:
    """Write YAML deterministically."""
    atomic_write_text(path, yaml.safe_dump(data, sort_keys=True))


def read_yaml(path: str) -> dict[str, Any]:
    """Read YAML file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data
