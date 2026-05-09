from tracegraph.data.models import TraversalPath
from tracegraph.retrieval.path_explainer import explain_retrieval_paths, format_single_path


def test_seed_only_path_explanation():
    p = TraversalPath(start_node_id="a", end_node_id="a", node_sequence=["a"], edge_sequence=[], cumulative_score=1.0, depth=0)
    assert "seed" in format_single_path(p).lower()


def test_multi_hop_path_explanation():
    p = TraversalPath(start_node_id="a", end_node_id="c", node_sequence=["a", "b", "c"], edge_sequence=["SHARED_ENTITY", "NEXT"], cumulative_score=1.0, depth=2)
    text = format_single_path(p)
    assert "SHARED_ENTITY" in text
    assert "NEXT" in text


def test_explain_handles_empty():
    assert "No traversal path" in explain_retrieval_paths([])
