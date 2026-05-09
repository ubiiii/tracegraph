#!/usr/bin/env python3
"""Wrapper for retrieval demo command."""

from tracegraph.cli import app


if __name__ == "__main__":
    app(
        [
            "retrieve",
            "--question",
            "What decision did we make about data retention, and which compliance clause justified it?",
        ]
    )
