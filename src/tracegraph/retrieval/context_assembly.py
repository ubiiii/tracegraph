"""Context assembly from retrieved nodes."""

from __future__ import annotations

from tracegraph.data.models import RetrievedNode


def assemble_context(retrieved_nodes: list[RetrievedNode], max_tokens: int, include_path_hints: bool = False) -> list[RetrievedNode]:
    """Select context nodes under token budget with simple diversity."""
    if max_tokens <= 0 or not retrieved_nodes:
        return []
    selected: list[RetrievedNode] = []
    used_tokens = 0
    used_docs: set[str] = set()
    for node in sorted(retrieved_nodes, key=lambda n: (n.score, n.node_id), reverse=True):
        tok = node.chunk.token_count or max(1, len(node.chunk.text.split()))
        if tok > max_tokens and not selected:
            selected.append(node)
            break
        if used_tokens + tok > max_tokens:
            continue
        # Prefer doc diversity in early picks.
        if len(selected) < 3 and node.chunk.doc_id in used_docs:
            continue
        selected.append(node)
        used_docs.add(node.chunk.doc_id)
        used_tokens += tok
    return selected


def format_context_for_prompt(nodes: list[RetrievedNode]) -> str:
    """Render context for prompt consumption."""
    lines: list[str] = []
    for i, node in enumerate(nodes, start=1):
        lines.append(f"[{i}] {node.chunk.title} (chunk {node.chunk.chunk_id}): {node.chunk.text}")
    return "\n".join(lines)
