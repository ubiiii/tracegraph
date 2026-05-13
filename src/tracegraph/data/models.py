"""Core data and run models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Document(BaseModel):
    """A source document in corpus memory."""

    doc_id: str
    title: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_path: str | None = None
    section_names: list[str] | None = None
    timestamp: str | None = None


class Chunk(BaseModel):
    """Chunk node used for indexing and graph memory."""

    node_id: str
    doc_id: str
    chunk_id: int
    title: str
    text: str
    normalized_text: str
    token_count: int
    start_char: int | None = None
    end_char: int | None = None
    section_name: str | None = None
    page_number: int | None = None
    entities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QAExample(BaseModel):
    """Question-answer example with optional support refs."""

    example_id: str
    question: str
    answer: str | list[str]
    supporting_facts: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TraversalPath(BaseModel):
    """Traversal path from seed to discovered node."""

    start_node_id: str
    end_node_id: str
    node_sequence: list[str]
    edge_sequence: list[str]
    hop_descriptions: list[str] = Field(default_factory=list)
    cumulative_score: float
    depth: int


class RetrievedNode(BaseModel):
    """Retrieved node with scores and explanation metadata."""

    node_id: str
    score: float
    retrieval_stage: Literal["seed", "traversal", "flat"]
    seed_score: float = 0.0
    traversal_score: float = 0.0
    rank: int = 0
    chunk: Chunk
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    path: TraversalPath | None = None
    why_retrieved: str = ""


class RetrievalBundle(BaseModel):
    """Top-level retrieval output."""

    question: str
    normalized_query: str
    seeds: list[RetrievedNode] = Field(default_factory=list)
    traversal_results: list[RetrievedNode] = Field(default_factory=list)
    assembled_context: list[RetrievedNode] = Field(default_factory=list)
    path_explanation: str = ""
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    estimated_token_usage: int = 0


class MissingEvidenceDecision(BaseModel):
    """Decision from missing evidence detector."""

    needs_callback: bool
    reason: str
    missing_concepts: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class AnswerOutput(BaseModel):
    """Final answer with citations and provenance."""

    question: str
    answer_text: str
    cited_answer_text: str
    sources: list[str] = Field(default_factory=list)
    retrieval_path_explanation: str = ""
    retrieval_path_hops: list[list[str]] = Field(default_factory=list)
    completeness_note: str = ""
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentStepTrace(BaseModel):
    """One callback loop step trace."""

    step_number: int
    query: str
    seeds: list[str] = Field(default_factory=list)
    traversal_nodes: list[str] = Field(default_factory=list)
    draft_answer: str = ""
    missing_evidence_decision: MissingEvidenceDecision
    refined_query: str = ""
    stop_reason: str | None = None
    latency_seconds: float = 0.0
    token_estimate: int = 0


class AgentRunResult(BaseModel):
    """Result of full agent run."""

    question: str
    final_query_used: str
    answer: AnswerOutput
    callback_count: int
    overall_latency: float
    token_estimates: int
    mode_used: str
    step_traces: list[AgentStepTrace] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    """Evaluation summary + per-example outputs."""

    metrics: dict[str, float]
    per_example: list[dict[str, Any]]
    config_used: dict[str, Any]
    timestamp: str


class CorpusState(BaseModel):
    """Persisted end-to-end retrieval state."""

    documents: list[Document]
    chunks: list[Chunk]
    graph_path: str
    graph_stats: dict[str, Any]
    index_metadata: dict[str, Any]
    config_hash: str
    corpus_hash: str
