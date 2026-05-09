from tracegraph.retrieval.context_assembly import assemble_context, format_context_for_prompt


def test_empty_context():
    assert assemble_context([], 100) == []


def test_budget_respected(built_graph):
    _, chunks, _ = built_graph
    from tracegraph.data.models import RetrievedNode

    nodes = [
        RetrievedNode(node_id=c.node_id, score=1.0, retrieval_stage="traversal", traversal_score=1.0, rank=1, chunk=c, score_breakdown={}, why_retrieved="x")
        for c in chunks
    ]
    selected = assemble_context(nodes, max_tokens=20)
    assert sum(n.chunk.token_count for n in selected) <= 20 or len(selected) == 1
    assert isinstance(format_context_for_prompt(selected), str)
