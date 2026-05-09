"""Revisitable callback loop."""

from __future__ import annotations

import time

from tracegraph.agent.answer_synthesizer import AnswerSynthesizer
from tracegraph.agent.missing_evidence_detector import MissingEvidenceDetector
from tracegraph.agent.query_refiner import QueryRefiner
from tracegraph.data.models import AgentRunResult, AgentStepTrace


def run_revisitable_loop(question: str, retriever, llm, corpus_state, config) -> AgentRunResult:
    """Run retrieve-answer-callback loop."""
    detector = MissingEvidenceDetector()
    refiner = QueryRefiner()
    answerer = AnswerSynthesizer()
    start = time.perf_counter()

    query = question
    traces: list[AgentStepTrace] = []
    seen_queries = {query}
    callback_count = 0
    final_bundle = None
    for step in range(config.callbacks.max_rounds + 1):
        bundle = retriever.retrieve(query, corpus_state, config)
        draft = answerer.draft_answer(question, bundle, llm)
        decision = detector.analyze(question, draft, bundle.assembled_context, llm)
        refined = refiner.refine(question, decision, bundle.assembled_context, llm) if decision.needs_callback else query
        stop_reason = None
        if not decision.needs_callback:
            stop_reason = "evidence_sufficient"
        elif refined in seen_queries:
            stop_reason = "repeated_refinement"
        elif step >= config.callbacks.max_rounds:
            stop_reason = "max_callbacks_reached"
        traces.append(
            AgentStepTrace(
                step_number=step,
                query=query,
                seeds=[s.node_id for s in bundle.seeds],
                traversal_nodes=[n.node_id for n in bundle.traversal_results],
                draft_answer=draft,
                missing_evidence_decision=decision,
                refined_query=refined,
                stop_reason=stop_reason,
                latency_seconds=bundle.diagnostics.get("latency_seconds", 0.0),
                token_estimate=bundle.estimated_token_usage,
            )
        )
        final_bundle = bundle
        if stop_reason is not None:
            break
        callback_count += 1
        query = refined
        seen_queries.add(query)

    assert final_bundle is not None
    answer = answerer.finalize_answer(question, final_bundle, llm)
    return AgentRunResult(
        question=question,
        final_query_used=query,
        answer=answer,
        callback_count=callback_count,
        overall_latency=time.perf_counter() - start,
        token_estimates=final_bundle.estimated_token_usage,
        mode_used=config.llm.mode,
        step_traces=traces,
        diagnostics={"seed_count": len(final_bundle.seeds), "final_context_nodes": len(final_bundle.assembled_context)},
    )
