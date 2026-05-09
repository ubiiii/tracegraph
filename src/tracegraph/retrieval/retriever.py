"""Top-level TraceGraph retriever."""

from __future__ import annotations

import time

from tracegraph.data.models import RetrievalBundle
from tracegraph.indexing.seed_retriever import SeedRetriever
from tracegraph.retrieval.context_assembly import assemble_context
from tracegraph.retrieval.path_explainer import explain_retrieval_paths
from tracegraph.retrieval.traversal import GraphTraversalRetriever
from tracegraph.utils.text import lowercase_for_index


class TraceGraphRetriever:
    """Orchestrates seed retrieval + traversal + context assembly."""

    def __init__(self, seed_retriever: SeedRetriever, traversal: GraphTraversalRetriever | None = None) -> None:
        self.seed_retriever = seed_retriever
        self.traversal = traversal or GraphTraversalRetriever()

    def retrieve(self, query: str, corpus_state, config) -> RetrievalBundle:
        """Run configured retrieval pipeline."""
        start = time.perf_counter()
        if not query.strip():
            raise ValueError("Question query cannot be empty")
        seeds = self.seed_retriever.retrieve(
            query,
            top_k=config.retrieval.seed_top_k,
            use_bm25=config.retrieval.use_bm25,
            use_entities=config.retrieval.use_entities,
            use_embeddings=config.retrieval.use_embeddings,
        )
        if config.traversal.enabled and config.graph.enabled:
            traversed = self.traversal.traverse(query, seeds, corpus_state["graph"], config)
        else:
            traversed = seeds
        context = assemble_context(traversed, max_tokens=config.context.max_tokens)
        explanation = explain_retrieval_paths(traversed)
        elapsed = time.perf_counter() - start
        return RetrievalBundle(
            question=query,
            normalized_query=lowercase_for_index(query),
            seeds=seeds,
            traversal_results=traversed,
            assembled_context=context,
            path_explanation=explanation,
            diagnostics={"latency_seconds": elapsed, "seed_count": len(seeds), "result_count": len(traversed)},
            estimated_token_usage=sum(n.chunk.token_count for n in context),
        )
