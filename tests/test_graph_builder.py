from tracegraph.config.schema import TraceGraphConfig
from tracegraph.graph.builder import TraceGraphBuilder
from tracegraph.graph.storage import load_graph, save_graph


def test_graph_builds_from_docs(demo_documents, tmp_path):
    cfg = TraceGraphConfig()
    builder = TraceGraphBuilder()
    graph, chunks, stats = builder.build(demo_documents, cfg)
    assert graph.number_of_nodes() == len(chunks)
    assert "edge_counts" in stats
    path = tmp_path / "g.pkl"
    save_graph(graph, str(path))
    loaded = load_graph(str(path))
    assert loaded.number_of_nodes() == graph.number_of_nodes()
