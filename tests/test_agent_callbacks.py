from tracegraph.agent.tracegraph_agent import TraceGraphAgent
from tracegraph.config.schema import TraceGraphConfig
from tracegraph.indexing.bm25_index import BM25Index
from tracegraph.indexing.entity_index import EntityIndex
from tracegraph.indexing.seed_retriever import SeedRetriever
from tracegraph.llm.mock_llm import MockLLM
from tracegraph.retrieval.retriever import TraceGraphRetriever


def test_callback_loop_runs(built_graph):
    graph, chunks, _ = built_graph
    cfg = TraceGraphConfig()
    cfg.callbacks.enabled = True
    bm25 = BM25Index()
    bm25.build(chunks)
    ent = EntityIndex()
    ent.build(chunks)
    retr = TraceGraphRetriever(SeedRetriever(bm25, ent))
    agent = TraceGraphAgent(retr, MockLLM())
    result = agent.answer("What decision and which clause justified it?", {"graph": graph, "chunks": chunks}, cfg)
    assert result.answer.answer_text
    assert result.answer.sources is not None
