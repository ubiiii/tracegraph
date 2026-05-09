#!/usr/bin/env python3
"""Wrapper for agent demo command."""

from tracegraph.cli import app


if __name__ == "__main__":
    app(
        [
            "answer",
            "--question",
            "What decision did we make about data retention, and which compliance clause justified it?",
            "--llm-mode",
            "mock",
        ]
    )
