from tracegraph.data.chunking import chunk_document
from tracegraph.data.models import Document
from tracegraph.data.preprocess import enrich_chunks, extract_entities_text
from tracegraph.indexing.entity_index import EntityIndex


def test_entity_extraction_returns_list():
    ents = extract_entities_text("Alice met Bob in Paris.")
    assert isinstance(ents, list)


def test_entity_index_search():
    doc = Document(doc_id="d1", title="d1", text="Alice met Bob.")
    chunks = chunk_document(doc, 20, 5)
    enrich_chunks(chunks)
    idx = EntityIndex()
    idx.build(chunks)
    res = idx.search("Where is Alice?", 3)
    assert isinstance(res, list)


def test_no_entities_query_returns_empty():
    idx = EntityIndex()
    idx.build([])
    assert idx.search("the and of", 3) == []
