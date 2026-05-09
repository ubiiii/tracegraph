"""Evaluation runner."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from tracegraph.evaluation.evidence import citation_hit_rate, document_recall_at_k
from tracegraph.evaluation.metrics import compute_metrics
from tracegraph.utils.io import write_json, write_jsonl


class EvaluationRunner:
    """Run evaluation over QA examples."""

    def __init__(self, agent) -> None:
        self.agent = agent

    @staticmethod
    def _extract_titles_from_sources(sources: list[str]) -> list[str]:
        titles: list[str] = []
        for src in sources:
            # Expected format: [Source: Title, chunk N]
            marker = "Source:"
            if marker not in src:
                continue
            part = src.split(marker, 1)[1].strip()
            title = part.split(", chunk", 1)[0].strip().strip("[]")
            if title:
                titles.append(title)
        return titles

    def run_single_example(self, example, corpus_state, config) -> dict[str, Any]:
        """Evaluate one example."""
        start = time.perf_counter()
        result = self.agent.answer(example.question, corpus_state, config)
        m = compute_metrics(result.answer.answer_text, example.answer)
        gold_titles = [fact.get("title", "") for fact in example.supporting_facts if fact.get("title")]
        retrieved_titles = self._extract_titles_from_sources(result.answer.sources)
        cov = document_recall_at_k(
            [
                type("Obj", (), {"chunk": type("Chunk", (), {"title": title})()})()  # tiny adapter for metric helper signature
                for title in retrieved_titles
            ],
            gold_titles,
        )
        callback_triggered = 1 if result.callback_count > 0 else 0
        first_nodes = set(result.step_traces[0].traversal_nodes) if result.step_traces else set()
        last_nodes = set(result.step_traces[-1].traversal_nodes) if result.step_traces else set()
        new_evidence_nodes = len(last_nodes - first_nodes) if result.step_traces else 0
        callback_added_new_evidence = 1 if new_evidence_nodes > 0 else 0
        return {
            "example_id": example.example_id,
            "question": example.question,
            "gold_answer": example.answer,
            "predicted_answer": result.answer.answer_text,
            "em": m["em"],
            "f1": m["f1"],
            "evidence_coverage": cov,
            "citation_hit_rate": citation_hit_rate(result.answer, example.supporting_facts),
            "callback_count": result.callback_count,
            "callback_triggered": callback_triggered,
            "callback_added_new_evidence": callback_added_new_evidence,
            "new_evidence_nodes": new_evidence_nodes,
            "latency": time.perf_counter() - start,
            "token_estimate": result.token_estimates,
            "path_explanation": result.answer.retrieval_path_explanation,
            "retrieved_titles": "|".join(retrieved_titles),
            "sources": "|".join(result.answer.sources),
        }

    def run_dataset(self, examples, corpus_state, config) -> pd.DataFrame:
        """Evaluate full dataset."""
        rows = [self.run_single_example(ex, corpus_state, config) for ex in examples]
        return pd.DataFrame(rows)

    def summarize_results(self, df: pd.DataFrame) -> dict[str, float]:
        """Aggregate evaluation summary."""
        if df.empty:
            return {"count": 0, "em": 0.0, "f1": 0.0}
        return {
            "count": float(len(df)),
            "em": float(df["em"].mean()),
            "f1": float(df["f1"].mean()),
            "evidence_coverage": float(df["evidence_coverage"].mean()),
            "avg_latency": float(df["latency"].mean()),
            "avg_callbacks": float(df["callback_count"].mean()),
            "avg_tokens": float(df["token_estimate"].mean()),
            "callback_trigger_rate": float(df["callback_triggered"].mean()),
            "callback_new_evidence_rate": float(df["callback_added_new_evidence"].mean()),
        }

    def save_outputs(self, df: pd.DataFrame, summary: dict[str, float], out_dir: str) -> None:
        """Persist evaluation outputs."""
        from pathlib import Path

        p = Path(out_dir)
        p.mkdir(parents=True, exist_ok=True)
        write_jsonl(str(p / "predictions.jsonl"), df.to_dict(orient="records"))
        df.to_csv(p / "metrics.csv", index=False)
        write_json(str(p / "metrics_summary.json"), summary)
        write_json(
            str(p / "evidence_metrics.json"),
            {
                "mean_evidence_coverage": summary.get("evidence_coverage", 0.0),
                "mean_citation_hit_rate": float(df["citation_hit_rate"].mean()) if not df.empty else 0.0,
            },
        )
        error_rows = df[(df["em"] == 0.0) | (df["f1"] < 0.5)]
        write_jsonl(str(p / "error_cases.jsonl"), error_rows.to_dict(orient="records"))
