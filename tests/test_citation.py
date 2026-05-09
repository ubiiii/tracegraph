from tracegraph.retrieval.citation import attach_inline_citations, make_citation, render_source_list


def test_make_citation(sample_chunks):
    c = make_citation(sample_chunks[0])
    assert "chunk" in c.lower()


def test_render_source_list(sample_chunks):
    from tracegraph.data.models import RetrievedNode

    nodes = [RetrievedNode(node_id=c.node_id, score=1, retrieval_stage="seed", seed_score=1, rank=1, chunk=c, score_breakdown={}, why_retrieved="") for c in sample_chunks]
    text = render_source_list(nodes)
    assert isinstance(text, str)
    assert text
    assert attach_inline_citations("answer", nodes).startswith("answer")
