"""Configuration package."""

from tracegraph.config.loader import load_config
from tracegraph.config.schema import TraceGraphConfig

__all__ = ["load_config", "TraceGraphConfig"]
