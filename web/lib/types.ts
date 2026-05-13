// Mirrors the actual TraceGraph data models (data/models.py + final_demo_answer.json schema).

export type EdgeType = "NEXT" | "SHARED_ENTITY" | "LEXICAL_SIM" | "RELATION";

export interface Document {
  id: string;
  title: string;
  source: string;
}

export interface Chunk {
  id: string;
  doc_id: string;
  doc_title: string;
  position: number;
  text: string;
  entities: string[];
  keywords: string[];
}

export interface GraphNode {
  id: string;
  doc_title: string;
  position: number;
  // Layout
  x: number;
  y: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: EdgeType;
  weight: number;
}

export interface MissingEvidenceDecision {
  confidence: number;
  needs_callback: boolean;
  reason: string;
  missing_concepts: string[];
}

export interface StepTrace {
  step_number: number;
  query: string;
  refined_query: string | null;
  seeds: string[];
  traversal_nodes: string[];
  draft_answer: string;
  token_estimate: number;
  latency_seconds: number;
  missing_evidence_decision: MissingEvidenceDecision;
  stop_reason: string | null;
}

export interface AnswerOutput {
  answer_text: string;
  cited_answer_text: string;
  completeness_note: string;
  confidence: number;
  question: string;
  retrieval_path_explanation: string;
  /** One array per top path; each entry is one hop label (e.g. SHARED_ENTITY (C-12, …)). */
  retrieval_path_hops?: string[][];
  sources: string[];
  metadata: { context_nodes: string[] };
}

export interface RunResult {
  answer: AnswerOutput;
  callback_count: number;
  diagnostics: { final_context_nodes: number; seed_count: number };
  final_query_used: string;
  mode_used: "mock" | "openai" | "heuristic";
  overall_latency: number;
  question: string;
  step_traces: StepTrace[];
}

export interface Variant {
  key: string;
  label: string;
  edges: EdgeType[];
  callbacks: boolean;
  description: string;
}

export interface MetricRow {
  variant: string;
  em: number;
  f1: number;
  evidence_coverage: number;
  latency_ms: number;
  callbacks_avg: number;
}
