"""Report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from tracegraph.utils.io import atomic_write_text, read_json, read_jsonl


def generate_markdown_report(results_dir: str) -> str:
    """Generate report markdown from metrics artifacts."""
    root = Path(results_dir)
    summary_path = root / "evaluation" / "metrics_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing metrics summary: {summary_path}")
    summary = read_json(str(summary_path))
    report = ["# TraceGraph Report", ""]
    if "variants" in summary:
        report.extend(["## Matrix Summary", "", f"- Best Variant: {summary.get('best_variant')}"])
        df = pd.DataFrame(summary.get("variants", []))
        if not df.empty:
            report.extend(["", df.to_string(index=False)])
            if {"variant", "f1", "avg_latency"}.issubset(df.columns):
                no_cb = df[df["variant"] == "bm25_graph"]
                cb = df[df["variant"] == "bm25_graph_callbacks"]
                if not no_cb.empty and not cb.empty:
                    f1_delta = float(cb.iloc[0]["f1"] - no_cb.iloc[0]["f1"])
                    lat_delta = float(cb.iloc[0]["avg_latency"] - no_cb.iloc[0]["avg_latency"])
                    interpretation = (
                        "callbacks improved quality with acceptable cost."
                        if f1_delta > 0 and lat_delta < 0.5
                        else "callbacks currently add cost without measurable quality gain on this slice."
                    )
                    report.extend(
                        [
                            "",
                            "## Callback Utility Audit",
                            "",
                            f"- F1 delta (callbacks - no-callback): {f1_delta:+.3f}",
                            f"- Latency delta (callbacks - no-callback): {lat_delta:+.3f}",
                            f"- Interpretation: {interpretation}",
                        ]
                    )
    else:
        report.extend(
            [
                "## Aggregate Metrics",
                "",
                f"- Count: {summary.get('count', 0)}",
                f"- EM: {summary.get('em', 0):.3f}",
                f"- F1: {summary.get('f1', 0):.3f}",
                f"- Evidence Coverage: {summary.get('evidence_coverage', 0):.3f}",
                f"- Avg Latency: {summary.get('avg_latency', 0):.3f}",
                f"- Avg Tokens: {summary.get('avg_tokens', 0):.1f}",
                f"- Callback Trigger Rate: {summary.get('callback_trigger_rate', 0):.3f}",
                f"- Callback New Evidence Rate: {summary.get('callback_new_evidence_rate', 0):.3f}",
            ]
        )
    variant_csv = root / "evaluation" / "variant_comparison.csv"
    if variant_csv.exists():
        report.extend(["", "## Variant Comparison", ""])
        report.append(pd.read_csv(variant_csv).to_string(index=False))
    text = "\n".join(report)
    atomic_write_text(str(root / "reports" / "report.md"), text)
    return text


def generate_case_studies(results_dir: str) -> str:
    """Generate simple case studies markdown."""
    root = Path(results_dir)
    matrix_path = root / "evaluation" / "all_predictions.jsonl"
    if matrix_path.exists():
        rows = read_jsonl(str(matrix_path))
        df = pd.DataFrame(rows)
        lines = ["# Case Studies", ""]
        # Compare bm25_only vs bm25_graph_callbacks per example.
        pivot = (
            df.pivot_table(
                index=["example_id", "question"],
                columns="variant",
                values=["f1", "evidence_coverage", "callback_count", "path_explanation", "predicted_answer", "sources"],
                aggfunc="first",
            )
            .reset_index()
        )
        top_examples = pivot.head(5)
        for _, row in top_examples.iterrows():
            example_id = row[("example_id", "")]
            question = row[("question", "")]
            f1_flat = row.get(("f1", "bm25_only"), 0.0)
            f1_graph = row.get(("f1", "bm25_graph"), 0.0)
            f1_cb = row.get(("f1", "bm25_graph_callbacks"), 0.0)
            cov_flat = row.get(("evidence_coverage", "bm25_only"), 0.0)
            cov_graph = row.get(("evidence_coverage", "bm25_graph"), 0.0)
            cb_count = row.get(("callback_count", "bm25_graph_callbacks"), 0.0)
            path = row.get(("path_explanation", "bm25_graph_callbacks"), "")
            pred = row.get(("predicted_answer", "bm25_graph_callbacks"), "")
            lines.extend(
                [
                    f"## {example_id}",
                    f"- Question: {question}",
                    f"- F1 (flat/graph/graph+cb): {f1_flat:.2f}/{f1_graph:.2f}/{f1_cb:.2f}",
                    f"- Evidence coverage (flat vs graph): {cov_flat:.2f} -> {cov_graph:.2f}",
                    f"- Callback count (graph+cb): {int(cb_count)}",
                    f"- Final answer (graph+cb): {pred}",
                    f"- Path: {path}",
                    "",
                ]
            )
        text = "\n".join(lines)
        atomic_write_text(str(root / "reports" / "case_studies.md"), text)
        return text

    pred_csv = root / "evaluation" / "metrics.csv"
    if not pred_csv.exists():
        raise FileNotFoundError(f"Missing metrics CSV: {pred_csv}")
    df = pd.read_csv(pred_csv)
    lines = ["# Case Studies", ""]
    ranked = df.sort_values(["f1", "evidence_coverage"], ascending=[False, False])
    selected = pd.concat([ranked.head(3), ranked.tail(2)]).drop_duplicates(subset=["example_id"])
    for _, row in selected.iterrows():
        lines.extend(
            [
                f"## {row['example_id']}",
                f"- Question: {row['question']}",
                f"- Gold: {row['gold_answer']}",
                f"- Predicted: {row['predicted_answer']}",
                f"- EM/F1: {row['em']:.2f}/{row['f1']:.2f}",
                f"- Evidence Coverage: {row['evidence_coverage']:.2f}",
                f"- Callback Count: {int(row.get('callback_count', 0))}",
                f"- Path: {row['path_explanation']}",
                "",
            ]
        )
    text = "\n".join(lines)
    atomic_write_text(str(root / "reports" / "case_studies.md"), text)
    return text
