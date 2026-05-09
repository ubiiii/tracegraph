from tracegraph.data.chunking import chunk_document
from tracegraph.data.models import Document
from tracegraph.data.preprocess import extract_keywords_tfidf
from tracegraph.utils.text import clean_whitespace, lowercase_for_index, normalize_text, safe_sentence_split


def test_whitespace_cleanup():
    assert clean_whitespace("a   b\n\nc") == "a b c"


def test_normalization_keeps_content():
    assert "policy" in normalize_text("Policy\ntext").lower()


def test_lowercase_behavior():
    assert lowercase_for_index("AbC") == "abc"


def test_sentence_split_safe():
    out = safe_sentence_split("Hi!!! Is this ok?? Yes.")
    assert len(out) >= 1


def test_keywords_tiny_corpus():
    d = Document(doc_id="d", title="d", text="policy clause retention")
    chunks = chunk_document(d, 10, 1)
    kw = extract_keywords_tfidf(chunks, top_k=3)
    assert chunks[0].node_id in kw
