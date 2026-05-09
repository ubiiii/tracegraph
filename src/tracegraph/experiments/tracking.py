"""Run tracking and artifact directory helpers."""

from __future__ import annotations

import platform
import subprocess
import sys
import time
from pathlib import Path

from tracegraph.utils.io import ensure_dir, write_json, write_yaml


def create_run_dir(outputs_root: str, dataset: str, variant: str) -> Path:
    """Create run directory and update latest pointer."""
    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
    run_name = f"{ts}_{dataset}_{variant}"
    run_dir = Path(outputs_root) / "runs" / run_name
    ensure_dir(str(run_dir))
    for sub in ["artifacts", "retrieval", "agent", "evaluation", "ablations", "reports"]:
        ensure_dir(str(run_dir / sub))
    ensure_dir(str(Path(outputs_root) / "runs"))
    (Path(outputs_root) / "runs" / "latest_run.txt").write_text(str(run_dir), encoding="utf-8")
    latest_alias = Path(outputs_root) / "runs" / "latest"
    if latest_alias.exists() and latest_alias.is_symlink():
        latest_alias.unlink()
    if not latest_alias.exists():
        latest_alias.write_text(str(run_dir), encoding="utf-8")
    return run_dir


def build_run_metadata(run_name: str, dataset: str, variant: str, random_seed: int, config_hash: str, corpus_hash: str) -> dict:
    """Build standard run metadata payload."""
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:  # noqa: BLE001
        git_hash = None
    return {
        "run_name": run_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit_hash": git_hash,
        "python_version": sys.version,
        "platform": platform.platform(),
        "random_seed": random_seed,
        "config_hash": config_hash,
        "corpus_hash": corpus_hash,
        "dataset": dataset,
        "variant": variant,
    }


def persist_run_headers(run_dir: str, resolved_config: dict, run_metadata: dict) -> None:
    """Persist config and run metadata files."""
    write_yaml(str(Path(run_dir) / "config_resolved.yaml"), resolved_config)
    write_json(str(Path(run_dir) / "run_metadata.json"), run_metadata)
