"""Configuration loading and merging."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tracegraph.config.schema import TraceGraphConfig
from tracegraph.utils.hashing import hash_config_dict
from tracegraph.utils.io import read_yaml


def _deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in update.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(default_path: str, override_paths: list[str] | None = None) -> tuple[TraceGraphConfig, str]:
    """Load and validate merged YAML config, then return config and hash."""
    default_cfg = read_yaml(default_path)
    merged = default_cfg
    for path in override_paths or []:
        if not Path(path).exists():
            raise FileNotFoundError(f"Config override not found: {path}")
        merged = _deep_merge(merged, read_yaml(path))
    cfg = TraceGraphConfig.model_validate(merged)
    cfg_hash = hash_config_dict(cfg.model_dump(mode="python"))
    return cfg, cfg_hash
