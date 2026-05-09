"""Deterministic mock LLM."""

from __future__ import annotations

from tracegraph.llm.base import BaseLLM


class MockLLM(BaseLLM):
    """Deterministic prompt-pattern mock for tests and offline mode."""

    def generate(self, prompt: str) -> str:
        """Return deterministic canned outputs keyed by prompt markers."""
        p = prompt.lower()
        if "missing evidence" in p:
            return "needs_callback=false; reason=evidence sufficient"
        if "refine query" in p:
            return "refined query: retention policy clause c-12 decision"
        if "final answer" in p:
            return "The decision was to retain logs for 24 months, justified by clause C-12."
        return "Draft: logs retained for 24 months based on clause C-12."
