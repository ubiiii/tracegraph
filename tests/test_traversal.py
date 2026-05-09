from tracegraph.config.schema import TraceGraphConfig
from tracegraph.data.models import RetrievedNode
from tracegraph.retrieval.traversal import GraphTraversalRetriever


def test_traversal_returns_ranked(built_graph):
    graph, chunks, _ = built_graph
    cfg = TraceGraphConfig()
    seed = RetrievedNode(node_id=chunks[0].node_id, score=1.0, retrieval_stage="seed", seed_score=1.0, rank=1, chunk=chunks[0], score_breakdown={}, why_retrieved="test")
    retr = GraphTraversalRetriever()
    out = retr.traverse("retention clause", [seed], graph, cfg)
    assert len(out) >= 1
    assert out[0].rank == 1
