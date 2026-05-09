from tracegraph.indexing.entity_index import EntityIndex
from tracegraph.indexing.seed_retriever import SeedRetriever


def test_bm25_only_retrieval(built_bm25):
    seed = SeedRetriever(built_bm25)
    out = seed.retrieve("alpha", top_k=3, use_entities=False)
    assert len(out) >= 1


def test_bm25_entity_fused(sample_chunks, built_bm25):
    ent = EntityIndex()
    ent.build(sample_chunks)
    seed = SeedRetriever(built_bm25, ent)
    out = seed.retrieve("alpha", top_k=3, use_entities=True)
    assert all(o.why_retrieved for o in out)


def test_all_sources_disabled_error(built_bm25):
    seed = SeedRetriever(built_bm25)
    try:
        seed.retrieve("alpha", 3, False, False, False)
        assert False
    except ValueError:
        assert True
