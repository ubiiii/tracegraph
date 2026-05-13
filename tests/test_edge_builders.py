from tracegraph.graph.edge_builders import build_lexical_edges, build_next_edges, build_relation_edges, build_shared_entity_edges


def test_next_edges(sample_chunks):
    edges = build_next_edges(sample_chunks)
    assert len(edges) >= 2


def test_shared_entity_edges(sample_chunks):
    sample_chunks[0].entities = ["alice"]
    sample_chunks[-1].entities = ["alice"]
    edges = build_shared_entity_edges(sample_chunks, min_shared=1)
    shared = [e for e in edges if e["edge_type"] == "SHARED_ENTITY"]
    assert shared
    assert "alice" in shared[0]["metadata"]["shared_entities"]


def test_lexical_edges(sample_chunks):
    edges = build_lexical_edges(sample_chunks, max_neighbors_per_node=2, min_similarity=0.0)
    assert all(e["source"] != e["target"] for e in edges)


def test_relation_edges_no_crash(sample_chunks):
    _ = build_relation_edges(sample_chunks)
