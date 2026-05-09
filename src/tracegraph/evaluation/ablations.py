"""Ablation helpers."""

from __future__ import annotations

import pandas as pd

from tracegraph.utils.io import atomic_write_text


def run_edge_ablation(results: list[dict], out_csv: str) -> pd.DataFrame:
    """Save edge ablation table."""
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    return df


def run_budget_ablation(results: list[dict], out_csv: str) -> pd.DataFrame:
    """Save budget ablation table."""
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    return df


def run_callback_ablation(results: list[dict], out_csv: str) -> pd.DataFrame:
    """Save callback ablation table."""
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    return df


def run_seed_method_ablation(results: list[dict], out_csv: str) -> pd.DataFrame:
    """Save seed method ablation table."""
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    return df


def write_ablation_summary(path: str, sections: dict[str, pd.DataFrame]) -> None:
    """Create markdown summary from ablation frames."""
    lines = ["# Ablation Summary", ""]
    for name, df in sections.items():
        lines.append(f"## {name}")
        if df.empty:
            lines.append("No rows.")
        else:
            lines.append(df.to_csv(index=False))
        lines.append("")
    atomic_write_text(path, "\n".join(lines))
