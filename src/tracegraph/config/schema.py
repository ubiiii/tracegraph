"""Pydantic configuration schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class PathsConfig(BaseModel):
    """Filesystem locations."""

    demo_dir: str = "data/demo"
    prepared_examples: str = "data/processed/prepared_examples.jsonl"
    outputs_root: str = "data/outputs"
    runs_dir: str = "data/outputs/runs"


class ChunkingConfig(BaseModel):
    """Chunking controls."""

    chunk_size: int = 180
    chunk_overlap: int = 40
    preserve_paragraphs: bool = True

    @model_validator(mode="after")
    def validate_chunking(self) -> "ChunkingConfig":
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")
        return self


class RetrievalConfig(BaseModel):
    """Seed retrieval options."""

    use_bm25: bool = True
    use_entities: bool = True
    use_embeddings: bool = False
    bm25_weight: float = 0.6
    entity_weight: float = 0.2
    embedding_weight: float = 0.2
    seed_top_k: int = 6

    @model_validator(mode="after")
    def validate_sources(self) -> "RetrievalConfig":
        if not (self.use_bm25 or self.use_entities or self.use_embeddings):
            raise ValueError("At least one retrieval source must be enabled")
        return self


class GraphConfig(BaseModel):
    """Graph edge controls."""

    enabled: bool = True
    edge_types: list[str] = Field(default_factory=lambda: ["NEXT", "SHARED_ENTITY", "LEXICAL_SIM"])
    next_weight: float = 0.8
    shared_entity_min: int = 1
    shared_entity_max_neighbors: int = 8
    lexical_min_similarity: float = 0.2
    lexical_max_neighbors: int = 5
    relation_enabled: bool = False


class TraversalConfig(BaseModel):
    """Graph traversal controls."""

    enabled: bool = True
    max_depth: int = 3
    beam_width: int = 6
    max_nodes: int = 12
    relevance_weight: float = 0.5
    edge_weight: float = 0.3
    novelty_weight: float = 0.15
    depth_penalty_weight: float = 0.05

    @model_validator(mode="after")
    def validate_limits(self) -> "TraversalConfig":
        if self.max_depth <= 0 or self.beam_width <= 0 or self.max_nodes <= 0:
            raise ValueError("Traversal limits must be > 0")
        return self


class ContextConfig(BaseModel):
    """Context assembly configuration."""

    max_tokens: int = 450
    diversity_by_doc: bool = True


class CallbackConfig(BaseModel):
    """Callback behavior."""

    enabled: bool = False
    max_rounds: int = 2


class LLMConfig(BaseModel):
    """LLM mode configuration."""

    mode: str = "mock"
    openai_model: str = "gpt-4o-mini"


class EvaluationConfig(BaseModel):
    """Evaluation options."""

    save_per_example: bool = True
    continue_on_error: bool = True


class PersistenceConfig(BaseModel):
    """Artifact reuse and write safety options."""

    reuse_artifacts: bool = True
    rebuild_on_mismatch: bool = True
    atomic_writes: bool = True


class TraceGraphConfig(BaseModel):
    """Root application configuration."""

    project: dict[str, Any] = Field(default_factory=lambda: {"name": "tracegraph"})
    random_seed: int = 42
    paths: PathsConfig = Field(default_factory=PathsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    preprocessing: dict[str, Any] = Field(default_factory=dict)
    entity_extraction: dict[str, Any] = Field(default_factory=dict)
    keyword_extraction: dict[str, Any] = Field(default_factory=lambda: {"top_k": 8})
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    traversal: TraversalConfig = Field(default_factory=TraversalConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    callbacks: CallbackConfig = Field(default_factory=CallbackConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    persistence: PersistenceConfig = Field(default_factory=PersistenceConfig)
    debug: bool = False
