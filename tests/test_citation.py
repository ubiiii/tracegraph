from tracegraph.evaluation.runner import EvaluationRunner
from tracegraph.retrieval.citation import attach_inline_citations, make_citation, render_source_list


def test_make_citation(sample_chunks):
    c = make_citation(sample_chunks[0])
    assert "Source:" in c
    assert sample_chunks[0].node_id in c


def test_extract_titles_from_sources_node_id_format():
    src = [
        "[Source: Policy Manual · policy::c0]",
        "[Source: Decision Memo · memo::c0]",
    ]
    assert EvaluationRunner._extract_titles_from_sources(src) == ["Policy Manual", "Decision Memo"]


def test_extract_titles_from_sources_legacy_chunk_format():
    assert EvaluationRunner._extract_titles_from_sources(
        ["[Source: Policy Manual, chunk 0]"]
    ) == ["Policy Manual"]


def test_render_source_list(sample_chunks):
    from tracegraph.data.models import RetrievedNode

    nodes = [RetrievedNode(node_id=c.node_id, score=1, retrieval_stage="seed", seed_score=1, rank=1, chunk=c, score_breakdown={}, why_retrieved="") for c in sample_chunks]
    text = render_source_list(nodes)
    assert isinstance(text, str)
    assert text
    assert attach_inline_citations("answer", nodes).startswith("answer")
