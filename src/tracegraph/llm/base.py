"""Base LLM interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract text generation interface."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate model output from prompt."""
