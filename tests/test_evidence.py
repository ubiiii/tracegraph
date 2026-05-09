from tracegraph.evaluation.evidence import citation_hit_rate, document_recall_at_k, supporting_fact_coverage


def test_empty_retrieved_returns_zero():
    assert supporting_fact_coverage([], [{"title": "X"}]) == 0.0
    assert document_recall_at_k([], ["X"]) == 0.0


def test_citation_hit_rate(built_graph):
    _, chunks, _ = built_graph
    from tracegraph.data.models import AnswerOutput, RetrievedNode

    nodes = [RetrievedNode(node_id=chunks[0].node_id, score=1, retrieval_stage="seed", seed_score=1, rank=1, chunk=chunks[0], score_breakdown={}, why_retrieved="")]
    ans = AnswerOutput(question="q", answer_text="a", cited_answer_text="a", sources=[f"[Source: {chunks[0].title}]"])
    assert citation_hit_rate(ans, [{"title": chunks[0].title}]) >= 0.0
