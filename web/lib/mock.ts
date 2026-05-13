import type {
  Document,
  Chunk,
  GraphNode,
  GraphEdge,
  RunResult,
  Variant,
  MetricRow,
} from "./types";

// ---- Demo corpus (mirrors data/demo/demo_documents.jsonl) -----------------

export const documents: Document[] = [
  { id: "policy", title: "Policy Manual", source: "INT-POL-002" },
  { id: "memo", title: "Decision Memo", source: "DEC-MEMO-2024-Q3" },
  { id: "audit", title: "Audit Note", source: "AUD-NOTE-117" },
  { id: "glossary", title: "Glossary", source: "GLOSS-DR-09" },
  { id: "sop", title: "Implementation SOP", source: "SOP-RP-17" },
  { id: "appendix", title: "Policy Appendix", source: "POL-APX-C" },
];

export const chunks: Chunk[] = [
  {
    id: "policy::c0",
    doc_id: "policy",
    doc_title: "Policy Manual",
    position: 0,
    text: "Section 4.2 — Operational logs are retained for a default of 24 months. Retention beyond this default requires written approval from the Compliance Officer and a documented justification under clause C-12.",
    entities: ["Compliance Officer", "C-12", "24 months"],
    keywords: ["retention", "logs", "compliance", "clause", "approval"],
  },
  {
    id: "memo::c0",
    doc_id: "memo",
    doc_title: "Decision Memo",
    position: 0,
    text: "On 2024-08-12 the working group decided to retain operational logs for 24 months for the next fiscal cycle, justified by clause C-12 of the data retention policy.",
    entities: ["working group", "C-12", "24 months"],
    keywords: ["decided", "retention", "fiscal", "memo", "clause"],
  },
  {
    id: "audit::c0",
    doc_id: "audit",
    doc_title: "Audit Note",
    position: 0,
    text: "Audit confirms records are kept 24 months in line with retention policy RP-17. Cross-reference: see clause C-12 and the Implementation SOP.",
    entities: ["RP-17", "C-12", "24 months"],
    keywords: ["audit", "confirms", "kept", "policy", "rp-17"],
  },
  {
    id: "glossary::c0",
    doc_id: "glossary",
    doc_title: "Glossary",
    position: 0,
    text: "Clause C-12: a compliance clause that authorizes retention of operational records when justified by audit or regulatory mandate.",
    entities: ["C-12", "compliance"],
    keywords: ["clause", "compliance", "definition", "retention"],
  },
  {
    id: "sop::c0",
    doc_id: "sop",
    doc_title: "Implementation SOP",
    position: 0,
    text: "Procedure RP-17 states that data shall be kept for 24 months unless a documented exception under clause C-12 is filed with Compliance.",
    entities: ["RP-17", "C-12", "24 months", "Compliance"],
    keywords: ["procedure", "kept", "states", "exception", "rp-17"],
  },
  {
    id: "appendix::c0",
    doc_id: "appendix",
    doc_title: "Policy Appendix",
    position: 0,
    text: "Appendix C: Lists all justifications under clause C-12 currently in force, including a 24-month retention exception logged 2024-08-12.",
    entities: ["C-12", "24 months", "Appendix C"],
    keywords: ["appendix", "list", "clause", "force", "justification"],
  },
];

// ---- Graph layout (deterministic) -----------------------------------------
// Hand-tuned positions for an instrument-panel feel rather than random force-layout chaos.

export const graphNodes: GraphNode[] = [
  { id: "policy::c0",   doc_title: "Policy Manual",    position: 0, x: 220, y: 140 },
  { id: "memo::c0",         doc_title: "Decision Memo",    position: 0, x: 460, y:  90 },
  { id: "audit::c0",    doc_title: "Audit Note",       position: 0, x: 700, y: 160 },
  { id: "glossary::c0", doc_title: "Glossary",         position: 0, x: 760, y: 360 },
  { id: "sop::c0",      doc_title: "Implementation SOP", position: 0, x: 460, y: 410 },
  { id: "appendix::c0", doc_title: "Policy Appendix",  position: 0, x: 180, y: 360 },
];

export const graphEdges: GraphEdge[] = [
  // SHARED_ENTITY - C-12 / 24 months / RP-17 conceptual links (orange spine)
  { source: "memo::c0", target: "policy::c0", type: "SHARED_ENTITY", weight: 0.92 },
  { source: "policy::c0", target: "appendix::c0", type: "SHARED_ENTITY", weight: 0.78 },
  { source: "audit::c0", target: "glossary::c0", type: "SHARED_ENTITY", weight: 0.81 },
  { source: "audit::c0", target: "sop::c0", type: "SHARED_ENTITY", weight: 0.74 },
  { source: "memo::c0", target: "appendix::c0", type: "SHARED_ENTITY", weight: 0.66 },
  // LEXICAL_SIM - wording overlap
  { source: "sop::c0", target: "policy::c0", type: "LEXICAL_SIM", weight: 0.61 },
  { source: "glossary::c0", target: "policy::c0", type: "LEXICAL_SIM", weight: 0.53 },
  { source: "audit::c0", target: "memo::c0", type: "LEXICAL_SIM", weight: 0.58 },
  // NEXT - sequential adjacency within a document (here represented as appendix -> sop conceptually)
  { source: "appendix::c0", target: "sop::c0", type: "NEXT", weight: 0.4 },
  // RELATION - lightweight justified-by link
  { source: "memo::c0", target: "glossary::c0", type: "RELATION", weight: 0.45 },
];

// ---- Canonical run result (matches data/outputs/final_demo_answer.json) ---

export const demoRun: RunResult = {
  question:
    "What retention decision was made for operational logs, and which compliance clause justified deviations?",
  answer: {
    question:
      "What retention decision was made for operational logs, and which compliance clause justified deviations?",
    answer_text:
      "Operational logs are retained for 24 months by default, and deviations are justified under C-12.",
    cited_answer_text:
      "Operational logs are retained for 24 months by default, and deviations are justified under C-12 [Source: Policy Manual · policy::c0] [Source: Decision Memo · memo::c0].",
    completeness_note: "best effort from retrieved evidence",
    confidence: 0.7,
    metadata: {
      context_nodes: [
        "policy::c0",
        "memo::c0",
        "audit::c0",
        "glossary::c0",
        "sop::c0",
        "appendix::c0",
      ],
    },
    retrieval_path_explanation:
      "Started at memo::c0, traversed via SHARED_ENTITY (C-12, RP-17) -> SHARED_ENTITY (E-9, legal hold), reached policy::c0.\nStarted at policy::c0, traversed via SHARED_ENTITY (C-12, retention), reached memo::c0.\nStarted at audit::c0, traversed via SHARED_ENTITY (C-12, audit), reached glossary::c0.",
    retrieval_path_hops: [
      [
        "SHARED_ENTITY (C-12, RP-17)",
        "SHARED_ENTITY (E-9, legal hold)",
      ],
      ["SHARED_ENTITY (C-12, retention)"],
      ["SHARED_ENTITY (C-12, audit)"],
    ],
    sources: [
      "[Source: Policy Manual · policy::c0]",
      "[Source: Decision Memo · memo::c0]",
      "[Source: Audit Note · audit::c0]",
      "[Source: Glossary · glossary::c0]",
      "[Source: Implementation SOP · sop::c0]",
      "[Source: Policy Appendix · appendix::c0]",
    ],
  },
  callback_count: 2,
  diagnostics: { final_context_nodes: 6, seed_count: 4 },
  final_query_used:
    "What retention decision was made for operational logs, and which compliance clause justified deviations? compliance clause c-12 rp-17 audit confirms 24 months states kept",
  mode_used: "mock",
  overall_latency: 0.984,
  step_traces: [
    {
      step_number: 0,
      query:
        "What retention decision was made for operational logs, and which compliance clause justified deviations?",
      refined_query:
        "What retention decision was made for operational logs, and which compliance clause justified deviations? compliance clause 24 months c-12 states kept rp-17 audit confirms",
      seeds: ["audit::c0", "memo::c0", "appendix::c0", "sop::c0"],
      traversal_nodes: [
        "policy::c0",
        "audit::c0",
        "memo::c0",
        "glossary::c0",
        "appendix::c0",
        "sop::c0",
      ],
      draft_answer: "C-12",
      token_estimate: 80,
      latency_seconds: 0.597,
      missing_evidence_decision: {
        confidence: 0.7,
        needs_callback: true,
        reason: "insufficient evidence breadth/facet coverage",
        missing_concepts: ["compliance clause"],
      },
      stop_reason: null,
    },
    {
      step_number: 1,
      query:
        "What retention decision was made for operational logs, and which compliance clause justified deviations? compliance clause 24 months c-12 states kept rp-17 audit confirms",
      refined_query:
        "What retention decision was made for operational logs, and which compliance clause justified deviations? compliance clause c-12 rp-17 audit confirms 24 months states kept",
      seeds: ["audit::c0", "policy::c0", "memo::c0", "appendix::c0"],
      traversal_nodes: [
        "audit::c0",
        "policy::c0",
        "memo::c0",
        "glossary::c0",
        "sop::c0",
        "appendix::c0",
      ],
      draft_answer:
        "Operational logs are retained for 24 months by default, and deviations are justified under C-12.",
      token_estimate: 88,
      latency_seconds: 0.226,
      missing_evidence_decision: {
        confidence: 0.92,
        needs_callback: false,
        reason: "evidence sufficient — answer grounded by ≥2 sources",
        missing_concepts: [],
      },
      stop_reason: "sufficient",
    },
  ],
};

// ---- Variant comparison (matches configs/retrieval/*.yaml) ----------------

export const variants: Variant[] = [
  {
    key: "bm25_only",
    label: "BM25 top-k",
    edges: [],
    callbacks: false,
    description: "Flat lexical retrieval baseline. No graph, no callbacks.",
  },
  {
    key: "embedding_graph",
    label: "Embedding + Graph",
    edges: ["NEXT", "SHARED_ENTITY", "LEXICAL_SIM"],
    callbacks: false,
    description: "Dense retrieval seeds with single-pass graph traversal.",
  },
  {
    key: "bm25_graph",
    label: "BM25 + Graph",
    edges: ["NEXT", "SHARED_ENTITY", "LEXICAL_SIM"],
    callbacks: false,
    description: "Primary system. Single-pass traversal over a sparse multi-edge graph.",
  },
  {
    key: "bm25_graph_callbacks",
    label: "BM25 + Graph + Callbacks",
    edges: ["NEXT", "SHARED_ENTITY", "LEXICAL_SIM", "RELATION"],
    callbacks: true,
    description: "Revisitable agent loop: draft → detect missing → refine → re-traverse.",
  },
];

export const metricsTable: MetricRow[] = [
  { variant: "bm25_only",            em: 0.41, f1: 0.59, evidence_coverage: 0.46, latency_ms:  340, callbacks_avg: 0.0 },
  { variant: "embedding_graph",      em: 0.55, f1: 0.71, evidence_coverage: 0.74, latency_ms:  720, callbacks_avg: 0.0 },
  { variant: "bm25_graph",           em: 0.62, f1: 0.78, evidence_coverage: 0.81, latency_ms:  610, callbacks_avg: 0.0 },
  { variant: "bm25_graph_callbacks", em: 0.62, f1: 0.78, evidence_coverage: 0.86, latency_ms: 1010, callbacks_avg: 1.7 },
];

// ---- Curated example questions --------------------------------------------

export const exampleQuestions = [
  "What retention decision was made for operational logs, and which compliance clause justified deviations?",
  "Which procedure governs the 24-month retention rule, and what exceptions are listed?",
  "Who must approve a retention extension beyond the default, and under which clause?",
  "When was the retention exception filed, and where is it logged?",
];
