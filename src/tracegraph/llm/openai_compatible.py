"""Optional OpenAI-compatible client wrapper."""

from __future__ import annotations

import os

from tracegraph.llm.base import BaseLLM


class OpenAICompatibleLLM(BaseLLM):
    """Provider-agnostic OpenAI-compatible endpoint adapter."""

    def __init__(self, model: str, base_url: str | None = None, api_key: str | None = None) -> None:
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.available = bool(self.api_key)

    def generate(self, prompt: str) -> str:
        """Generate output; raise actionable error when not configured."""
        if not self.available:
            raise RuntimeError("OpenAI-compatible LLM is not configured (missing OPENAI_API_KEY)")
        # Intentionally minimal to keep offline default; users can extend.
        raise RuntimeError("OpenAI-compatible runtime calls are disabled in default offline build.")
