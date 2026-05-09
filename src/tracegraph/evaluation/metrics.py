"""Answer metrics."""

from __future__ import annotations

import re
from collections import Counter


def normalize_answer(s: str) -> str:
    """Normalize for EM/F1 comparisons."""
    s = (s or "").lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def exact_match_score(pred: str, gold: str | list[str]) -> float:
    """Exact match across possible gold answers."""
    p = normalize_answer(pred)
    golds = gold if isinstance(gold, list) else [gold]
    return float(any(p == normalize_answer(g) for g in golds))


def f1_score(pred: str, gold: str | list[str]) -> float:
    """Token-level F1 against best gold."""
    p_tokens = normalize_answer(pred).split()
    golds = gold if isinstance(gold, list) else [gold]
    best = 0.0
    for g in golds:
        g_tokens = normalize_answer(g).split()
        if not p_tokens and not g_tokens:
            best = max(best, 1.0)
            continue
        common = Counter(p_tokens) & Counter(g_tokens)
        num_same = sum(common.values())
        if num_same == 0:
            continue
        precision = num_same / max(1, len(p_tokens))
        recall = num_same / max(1, len(g_tokens))
        best = max(best, 2 * precision * recall / (precision + recall))
    return float(best)


def compute_metrics(pred: str, gold: str | list[str]) -> dict[str, float]:
    """Compute EM/F1 dictionary."""
    return {"em": exact_match_score(pred, gold), "f1": f1_score(pred, gold)}
