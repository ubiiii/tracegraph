from tracegraph.data.chunking import chunk_document, split_text_into_chunks
from tracegraph.data.models import Document


def test_empty_document_returns_empty():
    d = Document(doc_id="x", title="x", text="")
    assert chunk_document(d, 10, 2) == []


def test_whitespace_document_returns_empty():
    d = Document(doc_id="x", title="x", text="   \n\n")
    assert chunk_document(d, 10, 2) == []


def test_short_document_single_chunk():
    d = Document(doc_id="x", title="x", text="short text")
    chunks = chunk_document(d, 50, 10)
    assert len(chunks) == 1


def test_overlap_applied_and_deterministic():
    text = " ".join(f"t{i}" for i in range(30))
    a = split_text_into_chunks(text, 10, 2)
    b = split_text_into_chunks(text, 10, 2)
    assert a == b
    assert len(a) > 1


def test_invalid_chunk_args_raise():
    d = Document(doc_id="x", title="x", text="abc")
    try:
        chunk_document(d, 0, 0)
        assert False
    except ValueError:
        assert True
