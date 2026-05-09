"""Top-level TraceGraph agent."""

from __future__ import annotations

from tracegraph.agent.answer_synthesizer import AnswerSynthesizer
from tracegraph.agent.callbacks import run_revisitable_loop
from tracegraph.data.models import AgentRunResult


class TraceGraphAgent:
    """Main agent facade for answering questions."""

    def __init__(self, retriever, llm) -> None:
        self.retriever = retriever
        self.llm = llm
        self.answerer = AnswerSynthesizer()

    def answer(self, question: str, corpus_state, config) -> AgentRunResult:
        """Answer with or without callback loop based on config."""
        if config.callbacks.enabled:
            return run_revisitable_loop(question, self.retriever, self.llm, corpus_state, config)
        bundle = self.retriever.retrieve(question, corpus_state, config)
        answer = self.answerer.finalize_answer(question, bundle, self.llm)
        from tracegraph.data.models import AgentRunResult

        return AgentRunResult(
            question=question,
            final_query_used=question,
            answer=answer,
            callback_count=0,
            overall_latency=bundle.diagnostics.get("latency_seconds", 0.0),
            token_estimates=bundle.estimated_token_usage,
            mode_used=config.llm.mode,
            step_traces=[],
            diagnostics=bundle.diagnostics,
        )
