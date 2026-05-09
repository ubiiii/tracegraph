from tracegraph.indexing.bm25_index import BM25Index


def test_build_and_search(sample_chunks):
    idx = BM25Index()
    idx.build(sample_chunks)
    out = idx.search("alpha", 3)
    assert len(out) >= 1


def test_search_before_build_raises():
    idx = BM25Index()
    try:
        idx.search("x", 3)
        assert False
    except RuntimeError:
        assert True


def test_empty_query_safe(sample_chunks):
    idx = BM25Index()
    idx.build(sample_chunks)
    assert idx.search("", 3) == []
