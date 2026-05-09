"""Graph schema helpers."""

from __future__ import annotations

from enum import Enum


class EdgeType(str, Enum):
    """Supported edge types."""

    NEXT = "NEXT"
    SHARED_ENTITY = "SHARED_ENTITY"
    LEXICAL_SIM = "LEXICAL_SIM"
    RELATION = "RELATION"
