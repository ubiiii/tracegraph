"""Agent interfaces."""

from __future__ import annotations

from typing import Protocol

from tracegraph.data.models import AnswerOutput, RetrievalBundle


class Answerer(Protocol):
    """Answer synthesizer protocol."""

    def draft_answer(self, question: str, context_bundle: RetrievalBundle, llm) -> str:
        """Create draft answer."""

    def finalize_answer(self, question: str, context_bundle: RetrievalBundle, llm) -> AnswerOutput:
        """Create final answer output."""
