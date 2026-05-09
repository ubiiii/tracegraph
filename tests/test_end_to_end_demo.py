from tracegraph.agent.tracegraph_agent import TraceGraphAgent
from tracegraph.config.schema import TraceGraphConfig
from tracegraph.data.dataset_demo import build_demo_documents
from tracegraph.graph.builder import TraceGraphBuilder
from tracegraph.indexing.bm25_index import BM25Index
from tracegraph.indexing.entity_index import EntityIndex
from tracegraph.indexing.seed_retriever import SeedRetriever
from tracegraph.llm.mock_llm import MockLLM
from tracegraph.retrieval.retriever import TraceGraphRetriever


def test_end_to_end_demo():
    cfg = TraceGraphConfig()
    cfg.callbacks.enabled = True
    docs = build_demo_documents()
    graph, chunks, _ = TraceGraphBuilder().build(docs, cfg)
    bm25 = BM25Index()
    bm25.build(chunks)
    ent = EntityIndex()
    ent.build(chunks)
    retriever = TraceGraphRetriever(SeedRetriever(bm25, ent))
    agent = TraceGraphAgent(retriever, MockLLM())
    result = agent.answer(
        "What decision did we make about data retention, and which compliance clause justified it?",
        {"graph": graph, "chunks": chunks},
        cfg,
    )
    assert result.answer.answer_text
    assert result.answer.sources is not None
    assert result.answer.retrieval_path_explanation is not None
