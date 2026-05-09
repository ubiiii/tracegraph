"""Typer CLI for TraceGraph workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from tracegraph.agent.tracegraph_agent import TraceGraphAgent
from tracegraph.config.loader import load_config
from tracegraph.data.chunking import chunk_document
from tracegraph.data.corpus_loader import load_documents_from_directory, load_jsonl_corpus, save_documents_jsonl
from tracegraph.data.dataset_demo import build_demo_documents, build_demo_qa
from tracegraph.data.dataset_hotpotqa import load_hotpotqa
from tracegraph.data.models import Chunk, Document, QAExample
from tracegraph.data.preprocess import enrich_chunks
from tracegraph.evaluation.ablations import (
    run_budget_ablation,
    run_callback_ablation,
    run_edge_ablation,
    run_seed_method_ablation,
    write_ablation_summary,
)
from tracegraph.evaluation.reports import generate_case_studies, generate_markdown_report
from tracegraph.evaluation.runner import EvaluationRunner
from tracegraph.experiments.tracking import build_run_metadata, create_run_dir, persist_run_headers
from tracegraph.graph.builder import TraceGraphBuilder
from tracegraph.graph.storage import load_graph, save_graph
from tracegraph.indexing.bm25_index import BM25Index
from tracegraph.indexing.embedding_index import EmbeddingIndex
from tracegraph.indexing.entity_index import EntityIndex
from tracegraph.indexing.seed_retriever import SeedRetriever
from tracegraph.llm.mock_llm import MockLLM
from tracegraph.llm.openai_compatible import OpenAICompatibleLLM
from tracegraph.retrieval.context_assembly import format_context_for_prompt
from tracegraph.retrieval.retriever import TraceGraphRetriever
from tracegraph.utils.hashing import hash_chunks
from tracegraph.utils.io import ensure_dir, read_jsonl, read_yaml, write_json, write_jsonl
from tracegraph.utils.logging_utils import configure_logging
from tracegraph.utils.random_seed import set_random_seed

app = typer.Typer(help="TraceGraph CLI")


def _load_corpus_state(config):
    runs_root = Path(config.paths.outputs_root) / "runs"
    latest_txt = runs_root / "latest_run.txt"
    if latest_txt.exists():
        run_dir = Path(latest_txt.read_text(encoding="utf-8").strip())
    else:
        run_dir = runs_root / "latest"
    out = run_dir / "artifacts"
    graph_path = out / "graph.pkl"
    chunks_path = out / "chunks.jsonl"
    if not graph_path.exists() or not chunks_path.exists():
        # Fallback: find newest run with required artifacts.
        candidates = sorted([p for p in runs_root.iterdir() if p.is_dir()], reverse=True) if runs_root.exists() else []
        for cand in candidates:
            g = cand / "artifacts" / "graph.pkl"
            c = cand / "artifacts" / "chunks.jsonl"
            if g.exists() and c.exists():
                graph_path = g
                chunks_path = c
                break
    if not graph_path.exists() or not chunks_path.exists():
        raise FileNotFoundError("Corpus state not found. Run build-graph first.")
    chunks = [Chunk.model_validate(r) for r in read_jsonl(str(chunks_path))]
    graph = load_graph(str(graph_path))
    return {"chunks": chunks, "graph": graph}


def _build_retriever(corpus_state, config):
    bm25 = BM25Index()
    bm25.build(corpus_state["chunks"], corpus_hash=hash_chunks([c.model_dump(mode="python") for c in corpus_state["chunks"]]))
    ent = EntityIndex()
    ent.build(corpus_state["chunks"])
    emb = EmbeddingIndex()
    emb.build(corpus_state["chunks"])
    seed = SeedRetriever(
        bm25,
        ent,
        emb,
        weights={"bm25": config.retrieval.bm25_weight, "entity": config.retrieval.entity_weight, "embedding": config.retrieval.embedding_weight},
    )
    return TraceGraphRetriever(seed)


def _apply_variant_settings(cfg, variant: str):
    """Apply retrieval mode variant flags to config."""
    if variant == "bm25_only":
        cfg.retrieval.use_bm25 = True
        cfg.retrieval.use_entities = False
        cfg.retrieval.use_embeddings = False
        cfg.retrieval.seed_top_k = 2
        cfg.graph.enabled = False
        cfg.traversal.enabled = False
        cfg.callbacks.enabled = False
        cfg.context.max_tokens = 120
    elif variant == "bm25_graph":
        cfg.retrieval.use_bm25 = True
        cfg.retrieval.use_entities = True
        cfg.retrieval.use_embeddings = False
        cfg.retrieval.seed_top_k = 4
        cfg.graph.enabled = True
        cfg.traversal.enabled = True
        cfg.callbacks.enabled = False
        cfg.context.max_tokens = 220
    elif variant == "bm25_graph_callbacks":
        cfg.retrieval.use_bm25 = True
        cfg.retrieval.use_entities = True
        cfg.retrieval.use_embeddings = False
        cfg.retrieval.seed_top_k = 4
        cfg.graph.enabled = True
        cfg.traversal.enabled = True
        cfg.callbacks.enabled = True
        cfg.context.max_tokens = 260
    elif variant == "embedding_graph":
        cfg.retrieval.use_bm25 = True
        cfg.retrieval.use_entities = True
        cfg.retrieval.use_embeddings = True
        cfg.graph.enabled = True
        cfg.traversal.enabled = True
        cfg.callbacks.enabled = True
    else:
        raise typer.BadParameter(f"Unknown variant: {variant}")
    return cfg


def _load_eval_examples(eval_config_path: str, limit: int | None = None) -> tuple[str, list[QAExample]]:
    eval_cfg = read_yaml(eval_config_path)
    dataset = eval_cfg.get("dataset", {}).get("name", "demo")
    prepared_path = eval_cfg.get("dataset", {}).get("prepared_path")
    if prepared_path and Path(prepared_path).exists():
        rows = read_jsonl(prepared_path)
    else:
        rows = read_jsonl("data/demo/demo_qa.jsonl")
    examples = [QAExample.model_validate(r) for r in rows]
    if limit is not None:
        examples = examples[:limit]
    elif eval_cfg.get("dataset", {}).get("limit") is not None:
        examples = examples[: int(eval_cfg["dataset"]["limit"])]
    return dataset, examples


@app.command("prepare-demo")
def prepare_demo(output_dir: str = "data/demo", force: bool = False, seed: int = 42) -> None:
    """Generate deterministic synthetic demo corpus and QA examples."""
    set_random_seed(seed)
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise typer.BadParameter(f"Output directory is non-empty: {output_dir}. Use --force to overwrite.")
    ensure_dir(output_dir)
    docs = build_demo_documents()
    qas = build_demo_qa()
    save_documents_jsonl(str(out / "demo_documents.jsonl"), docs)
    write_jsonl(str(out / "demo_qa.jsonl"), [q.model_dump(mode="python") for q in qas])
    typer.echo(f"Prepared demo corpus: {len(docs)} documents, {len(qas)} QA examples at {out}")


@app.command("prepare-hotpotqa")
def prepare_hotpotqa(input: str, output: str, limit: int | None = None, seed: int = 42) -> None:
    """Convert raw HotpotQA JSON into prepared internal JSONL format."""
    examples = load_hotpotqa(input, limit=limit, seed=seed)
    write_jsonl(output, [e.model_dump(mode="python") for e in examples])
    typer.echo(f"Loaded and saved {len(examples)} examples -> {output}")


@app.command("build-graph")
def build_graph(
    config: str = "configs/default.yaml",
    input_dir: str = "data/demo",
    output_dir: str = "data/outputs",
    rebuild: bool = False,
    debug: bool = False,
) -> None:
    """Build chunks, graph, and indices from corpus."""
    cfg, cfg_hash = load_config(config)
    configure_logging(debug or cfg.debug)
    docs_path = Path(input_dir) / "demo_documents.jsonl"
    if docs_path.exists():
        docs = load_jsonl_corpus(str(docs_path))
    else:
        docs = load_documents_from_directory(input_dir)
    if not docs:
        raise typer.BadParameter("Corpus is empty; cannot build graph.")

    run_dir = create_run_dir(output_dir, "demo", "build_graph")
    builder = TraceGraphBuilder()
    graph, chunks, stats = builder.build(docs, cfg)
    save_graph(graph, str(run_dir / "artifacts" / "graph.pkl"))
    write_json(str(run_dir / "artifacts" / "graph_stats.json"), stats)
    write_jsonl(str(run_dir / "artifacts" / "documents.jsonl"), [d.model_dump(mode="python") for d in docs])
    write_jsonl(str(run_dir / "artifacts" / "chunks.jsonl"), [c.model_dump(mode="python") for c in chunks])

    corpus_hash = hash_chunks([c.model_dump(mode="python") for c in chunks])
    bm25 = BM25Index()
    bm25.build(chunks, corpus_hash)
    bm25.save(str(run_dir / "artifacts" / "bm25_index.pkl"))
    ent = EntityIndex()
    ent.build(chunks, corpus_hash)
    ent.save(str(run_dir / "artifacts" / "entity_index.pkl"))
    emb = EmbeddingIndex()
    emb.build(chunks, corpus_hash)
    emb.save(str(run_dir / "artifacts" / "embedding_index.pkl"))

    run_meta = build_run_metadata(run_dir.name, "demo", "bm25_graph", cfg.random_seed, cfg_hash, corpus_hash)
    persist_run_headers(str(run_dir), cfg.model_dump(mode="python"), run_meta)
    typer.echo(f"Built graph with {len(docs)} docs, {len(chunks)} chunks, {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    typer.echo(f"Artifacts: {run_dir}")


@app.command("retrieve")
def retrieve(
    question: Annotated[str, typer.Option("--question", help="Question to retrieve evidence for.")],
    config: str = "configs/retrieval/bm25_graph.yaml",
    top_k: int = 6,
    max_tokens: int = 450,
    output_path: str | None = None,
) -> None:
    """Run retrieval-only pipeline and print diagnostics."""
    if not question.strip():
        raise typer.BadParameter("Question cannot be empty")
    cfg, _ = load_config("configs/default.yaml", [config])
    corpus_state = _load_corpus_state(cfg)
    cfg.retrieval.seed_top_k = top_k
    cfg.context.max_tokens = max_tokens
    retriever = _build_retriever(corpus_state, cfg)
    bundle = retriever.retrieve(question, corpus_state, cfg)
    typer.echo(f"Question: {question}")
    typer.echo(f"Top seeds: {[s.node_id for s in bundle.seeds[:3]]}")
    typer.echo(f"Top traversal nodes: {[n.node_id for n in bundle.traversal_results[:5]]}")
    typer.echo(f"Estimated tokens: {bundle.estimated_token_usage}")
    typer.echo("Path explanation:")
    typer.echo(bundle.path_explanation)
    if output_path:
        write_json(output_path, bundle.model_dump(mode="python"))


@app.command("answer")
def answer(
    question: Annotated[str, typer.Option("--question", help="Question to answer.")],
    config: str = "configs/retrieval/bm25_graph_callbacks.yaml",
    output_path: str | None = None,
    llm_mode: Annotated[str, typer.Option(help="mock|openai-compatible|auto")] = "mock",
) -> None:
    """Run full answering pipeline including callbacks."""
    cfg, _ = load_config("configs/default.yaml", [config])
    cfg.llm.mode = llm_mode
    corpus_state = _load_corpus_state(cfg)
    retriever = _build_retriever(corpus_state, cfg)
    llm = MockLLM()
    if llm_mode in {"openai-compatible", "auto"}:
        try:
            llm = OpenAICompatibleLLM(cfg.llm.openai_model)
            _ = llm.generate("healthcheck")
        except Exception:
            typer.echo("Warning: OpenAI-compatible LLM unavailable, falling back to MockLLM.")
            llm = MockLLM()
    agent = TraceGraphAgent(retriever, llm)
    result = agent.answer(question, corpus_state, cfg)
    typer.echo(f"Question: {question}")
    typer.echo(f"Answer: {result.answer.answer_text}")
    typer.echo("Sources:")
    typer.echo("\n".join(result.answer.sources))
    typer.echo("Path explanation:")
    typer.echo(result.answer.retrieval_path_explanation)
    typer.echo(f"Completeness: {result.answer.completeness_note}")
    if output_path:
        write_json(output_path, result.model_dump(mode="python"))


@app.command("evaluate")
def evaluate(config: str = "configs/evaluation/demo.yaml", limit: int | None = None, output_dir: str = "data/outputs", variant: str = "bm25_graph_callbacks") -> None:
    """Run evaluation and save metrics outputs."""
    dataset, examples = _load_eval_examples(config, limit=limit)
    if not examples:
        raise typer.BadParameter("Evaluation dataset is empty.")
    eval_cfg = read_yaml(config)
    variants = [variant] if variant != "all" else eval_cfg.get("variants", ["bm25_only", "bm25_graph", "bm25_graph_callbacks"])
    run_dir = create_run_dir(output_dir, dataset, "matrix_eval")
    comparison_rows: list[dict] = []
    all_predictions: list[dict] = []
    for v in variants:
        cfg, _ = load_config("configs/default.yaml", [])
        cfg = _apply_variant_settings(cfg, v)
        corpus_state = _load_corpus_state(cfg)
        retriever = _build_retriever(corpus_state, cfg)
        agent = TraceGraphAgent(retriever, MockLLM())
        runner = EvaluationRunner(agent)
        df = runner.run_dataset(examples, corpus_state, cfg)
        summary = runner.summarize_results(df)
        variant_dir = run_dir / "evaluation" / v
        runner.save_outputs(df, summary, str(variant_dir))
        row = {
            "variant": v,
            "count": summary.get("count", 0.0),
            "em": summary.get("em", 0.0),
            "f1": summary.get("f1", 0.0),
            "evidence_coverage": summary.get("evidence_coverage", 0.0),
            "avg_latency": summary.get("avg_latency", 0.0),
            "avg_tokens": summary.get("avg_tokens", 0.0),
            "avg_callbacks": summary.get("avg_callbacks", 0.0),
            "callback_trigger_rate": summary.get("callback_trigger_rate", 0.0),
            "callback_new_evidence_rate": summary.get("callback_new_evidence_rate", 0.0),
        }
        comparison_rows.append(row)
        for rec in df.to_dict(orient="records"):
            rec["variant"] = v
            all_predictions.append(rec)
        typer.echo(f"[{v}] EM={row['em']:.3f} F1={row['f1']:.3f} Cov={row['evidence_coverage']:.3f}")

    import pandas as pd

    comp_df = pd.DataFrame(comparison_rows).sort_values(
        by=["f1", "evidence_coverage", "avg_latency"],
        ascending=[False, False, True],
    )
    comp_path = run_dir / "evaluation" / "variant_comparison.csv"
    comp_df.to_csv(comp_path, index=False)
    write_json(str(run_dir / "evaluation" / "variant_comparison.json"), comparison_rows)
    write_jsonl(str(run_dir / "evaluation" / "all_predictions.jsonl"), all_predictions)
    write_json(
        str(run_dir / "evaluation" / "metrics_summary.json"),
        {
            "best_variant": comp_df.iloc[0]["variant"] if not comp_df.empty else None,
            "variants": comparison_rows,
        },
    )
    summary_lines = ["# Variant Comparison", "", comp_df.to_string(index=False) if not comp_df.empty else "No rows"]
    (run_dir / "evaluation" / "variant_comparison.md").write_text("\n".join(summary_lines), encoding="utf-8")
    typer.echo(f"Saved matrix comparison to {comp_path}")
    typer.echo(f"Evaluation run dir: {run_dir}")


@app.command("ablations")
def ablations(config: str = "configs/evaluation/demo.yaml", output_dir: str = "data/outputs", limit: int | None = None) -> None:
    """Run real ablation experiments on configured dataset subset."""
    dataset, examples = _load_eval_examples(config, limit=limit if limit is not None else 6)
    if not examples:
        raise typer.BadParameter("No examples available for ablation run.")
    run_dir = create_run_dir(output_dir, dataset, "ablations")

    def eval_variant(vname: str, mutator):
        cfg, _ = load_config("configs/default.yaml", [])
        cfg = _apply_variant_settings(cfg, "bm25_graph_callbacks")
        mutator(cfg)
        corpus_state = _load_corpus_state(cfg)
        retriever = _build_retriever(corpus_state, cfg)
        agent = TraceGraphAgent(retriever, MockLLM())
        runner = EvaluationRunner(agent)
        df = runner.run_dataset(examples, corpus_state, cfg)
        s = runner.summarize_results(df)
        return {
            "variant": vname,
            "em": s.get("em", 0.0),
            "f1": s.get("f1", 0.0),
            "evidence_coverage": s.get("evidence_coverage", 0.0),
            "avg_latency": s.get("avg_latency", 0.0),
            "avg_tokens": s.get("avg_tokens", 0.0),
            "avg_callbacks": s.get("avg_callbacks", 0.0),
            "sample_size": s.get("count", 0.0),
        }

    edge_rows = [
        eval_variant("edge_next_only", lambda c: setattr(c.graph, "edge_types", ["NEXT"])),
        eval_variant("edge_entity_only", lambda c: setattr(c.graph, "edge_types", ["SHARED_ENTITY"])),
        eval_variant("edge_lexical_only", lambda c: setattr(c.graph, "edge_types", ["LEXICAL_SIM"])),
        eval_variant("edge_all", lambda c: setattr(c.graph, "edge_types", ["NEXT", "SHARED_ENTITY", "LEXICAL_SIM", "RELATION"])),
    ]
    budget_rows = [
        eval_variant("budget_low", lambda c: (setattr(c.traversal, "max_depth", 1), setattr(c.traversal, "beam_width", 3), setattr(c.traversal, "max_nodes", 6))),
        eval_variant("budget_medium", lambda c: (setattr(c.traversal, "max_depth", 2), setattr(c.traversal, "beam_width", 5), setattr(c.traversal, "max_nodes", 10))),
        eval_variant("budget_high", lambda c: (setattr(c.traversal, "max_depth", 4), setattr(c.traversal, "beam_width", 8), setattr(c.traversal, "max_nodes", 16))),
    ]
    callback_rows = [
        eval_variant("callbacks_off", lambda c: setattr(c.callbacks, "enabled", False)),
        eval_variant("callbacks_on", lambda c: setattr(c.callbacks, "enabled", True)),
    ]
    seed_rows = [
        eval_variant("seed_bm25_only", lambda c: (setattr(c.retrieval, "use_bm25", True), setattr(c.retrieval, "use_entities", False), setattr(c.retrieval, "use_embeddings", False))),
        eval_variant("seed_bm25_entity", lambda c: (setattr(c.retrieval, "use_bm25", True), setattr(c.retrieval, "use_entities", True), setattr(c.retrieval, "use_embeddings", False))),
    ]

    edge_df = run_edge_ablation(edge_rows, str(run_dir / "ablations" / "edge_ablation.csv"))
    budget_df = run_budget_ablation(budget_rows, str(run_dir / "ablations" / "budget_ablation.csv"))
    callback_df = run_callback_ablation(callback_rows, str(run_dir / "ablations" / "callback_ablation.csv"))
    seed_df = run_seed_method_ablation(seed_rows, str(run_dir / "ablations" / "seed_method_ablation.csv"))
    write_ablation_summary(str(run_dir / "ablations" / "ablation_summary.md"), {"edge": edge_df, "budget": budget_df, "callback": callback_df, "seed": seed_df})
    typer.echo(f"Ablations written to {run_dir / 'ablations'}")


@app.command("report")
def report(
    results_dir: Annotated[str, typer.Option("--results-dir", help="Results directory containing evaluation artifacts.")],
    output_path: str | None = None,
) -> None:
    """Generate markdown report from saved results."""
    report_dir = Path(results_dir)
    summary_path = report_dir / "evaluation" / "metrics_summary.json"
    if not summary_path.exists():
        runs_root = report_dir.parent if report_dir.parent.name == "runs" else None
        fallback_dir: Path | None = None
        if runs_root and runs_root.exists():
            candidates = sorted([p for p in runs_root.iterdir() if p.is_dir()], reverse=True)
            for cand in candidates:
                if (cand / "evaluation" / "metrics_summary.json").exists():
                    fallback_dir = cand
                    break
        if fallback_dir is None:
            raise FileNotFoundError(
                f"Missing metrics summary in {report_dir}. "
                "Provide a run directory that contains evaluation outputs."
            )
        typer.echo(f"Warning: {report_dir} has no evaluation summary; using latest evaluation run {fallback_dir}.")
        report_dir = fallback_dir
    text = generate_markdown_report(str(report_dir))
    _ = generate_case_studies(str(report_dir))
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    typer.echo(f"Report generated in {report_dir}/reports")


def main() -> None:
    """CLI module entrypoint."""
    app()


if __name__ == "__main__":
    main()
