"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from tracegraph.data.chunking import chunk_document
from tracegraph.data.dataset_demo import build_demo_documents, build_demo_qa
from tracegraph.data.models import Document
from tracegraph.graph.builder import TraceGraphBuilder
from tracegraph.indexing.bm25_index import BM25Index
from tracegraph.llm.mock_llm import MockLLM


@pytest.fixture
def demo_documents():
    return build_demo_documents()


@pytest.fixture
def tiny_question():
    return build_demo_qa()[0]


@pytest.fixture
def sample_doc():
    return Document(doc_id="d1", title="Doc1", text="Alpha beta gamma. Delta epsilon zeta.")


@pytest.fixture
def sample_chunks(sample_doc):
    return chunk_document(sample_doc, chunk_size=4, chunk_overlap=1)


@pytest.fixture
def mock_llm():
    return MockLLM()


@pytest.fixture
def built_bm25(sample_chunks):
    idx = BM25Index()
    idx.build(sample_chunks)
    return idx


@pytest.fixture
def built_graph(demo_documents):
    from tracegraph.config.schema import TraceGraphConfig

    cfg = TraceGraphConfig()
    builder = TraceGraphBuilder()
    g, chunks, stats = builder.build(demo_documents, cfg)
    return g, chunks, stats
