"""Citation rendering helpers."""

from __future__ import annotations

from tracegraph.data.models import Chunk, RetrievedNode


def make_citation(chunk: Chunk) -> str:
    """Format a single source citation."""
    page = f", page {chunk.page_number}" if chunk.page_number is not None else ""
    return f"[Source: {chunk.title}, chunk {chunk.chunk_id}{page}]"


def render_source_list(nodes: list[RetrievedNode]) -> str:
    """Render deduplicated source list."""
    seen: set[str] = set()
    lines: list[str] = []
    for node in nodes:
        c = make_citation(node.chunk)
        if c in seen:
            continue
        seen.add(c)
        lines.append(c)
    return "\n".join(lines)


def attach_inline_citations(answer_text: str, nodes: list[RetrievedNode]) -> str:
    """Attach top citations to answer text."""
    if not nodes:
        return answer_text
    cites = " ".join(make_citation(n.chunk) for n in nodes[:2])
    return f"{answer_text} {cites}"
