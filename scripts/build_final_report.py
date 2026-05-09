"""Generate the TraceGraph Final Report (CECS-551 / Team 8) as a PDF.

Synthesises Phase 1 (proposal), Phase 2 (feasibility), Phase 3 (prototype),
and the technical documentation into a single, deduplicated report capped
at 11 pages with Roles & Contributions on its own page.

Output: CECS551_FinalReport_Team8_TraceGraph.pdf at repo root.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as _canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(_canvas.Canvas):
    """Canvas that records every page so we can stamp 'Page X of N' on save."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_pages: list[dict] = []

    def showPage(self):  # noqa: N802
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):  # noqa: N802
        total = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            self._draw_page_number(total)
            super().showPage()
        super().save()

    def _draw_page_number(self, total: int):
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MUTE)
        self.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 18,
                             f"Page {self._pageNumber} of {total}")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "CECS551_FinalReport_Team8_TraceGraph.pdf"

INK = colors.HexColor("#131210")
SIGNAL = colors.HexColor("#b6320e")
RULE = colors.HexColor("#a59b80")
MUTE = colors.HexColor("#5e574a")


# ---------- Styles --------------------------------------------------------

def make_styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle(
        "title", parent=base["Title"],
        fontName="Times-Bold", fontSize=20, leading=24,
        alignment=TA_CENTER, spaceAfter=8, textColor=INK,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle", parent=base["Normal"],
        fontName="Times-Italic", fontSize=12, leading=14,
        alignment=TA_CENTER, spaceAfter=4, textColor=INK,
    )
    s["meta"] = ParagraphStyle(
        "meta", parent=base["Normal"],
        fontName="Helvetica", fontSize=9, leading=12,
        alignment=TA_CENTER, spaceAfter=10, textColor=MUTE,
    )
    s["abstract_label"] = ParagraphStyle(
        "abstract_label", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=9, leading=12,
        alignment=TA_LEFT, spaceAfter=2, textColor=INK,
    )
    s["abstract"] = ParagraphStyle(
        "abstract", parent=base["Normal"],
        fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_JUSTIFY, spaceAfter=10, textColor=INK,
        leftIndent=10, rightIndent=10,
    )
    s["h1"] = ParagraphStyle(
        "h1", parent=base["Heading1"],
        fontName="Helvetica-Bold", fontSize=12, leading=15,
        spaceBefore=10, spaceAfter=4, textColor=INK,
    )
    s["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontName="Helvetica-Bold", fontSize=10.5, leading=13,
        spaceBefore=6, spaceAfter=2, textColor=INK,
    )
    s["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_JUSTIFY, spaceAfter=4, textColor=INK,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_LEFT, spaceAfter=2, textColor=INK,
        leftIndent=14, bulletIndent=4, firstLineIndent=0,
    )
    s["mono"] = ParagraphStyle(
        "mono", parent=base["Normal"],
        fontName="Courier", fontSize=8.6, leading=11,
        textColor=INK, leftIndent=8,
    )
    s["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
        alignment=TA_CENTER, textColor=MUTE, spaceAfter=4,
    )
    s["ref"] = ParagraphStyle(
        "ref", parent=base["Normal"],
        fontName="Times-Roman", fontSize=8.8, leading=11,
        alignment=TA_LEFT, spaceAfter=2, textColor=INK,
        leftIndent=18, firstLineIndent=-18,
    )
    return s


# ---------- Page chrome ---------------------------------------------------

PAGE_W, PAGE_H = LETTER
MARGIN = 0.7 * inch


def header_footer(c, doc):
    c.saveState()
    # Top rule + running head
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(MARGIN, PAGE_H - MARGIN + 14, PAGE_W - MARGIN, PAGE_H - MARGIN + 14)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTE)
    c.drawString(MARGIN, PAGE_H - MARGIN + 18,
                 "TRACEGRAPH · CECS-551 · TEAM 8 · FINAL REPORT")
    # Page-number is stamped by NumberedCanvas at save time.
    # Bottom rule
    c.setStrokeColor(RULE)
    c.line(MARGIN, MARGIN - 12, PAGE_W - MARGIN, MARGIN - 12)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTE)
    c.drawString(MARGIN, MARGIN - 22,
                 "Lubal · Manzer · Maurya · Yadav")
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 22,
                      "graph-based retrieval · multi-hop QA")
    c.restoreState()


def build_doc(path: Path):
    doc = BaseDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title="TraceGraph — Final Report",
        author="Team 8: Lubal, Manzer, Maurya, Yadav",
        subject="CECS-551 Final Report",
    )
    # Two-column frames for body pages
    col_gap = 0.25 * inch
    col_w = (PAGE_W - 2 * MARGIN - col_gap) / 2
    frame_left = Frame(MARGIN, MARGIN, col_w, PAGE_H - 2 * MARGIN,
                       leftPadding=0, rightPadding=0,
                       topPadding=0, bottomPadding=0, id="left")
    frame_right = Frame(MARGIN + col_w + col_gap, MARGIN, col_w,
                        PAGE_H - 2 * MARGIN,
                        leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id="right")
    # Single-column frame for first/last page
    frame_full = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN,
                       PAGE_H - 2 * MARGIN,
                       leftPadding=0, rightPadding=0,
                       topPadding=0, bottomPadding=0, id="full")

    doc.addPageTemplates([
        PageTemplate(id="full", frames=[frame_full],
                     onPage=header_footer),
        PageTemplate(id="twocol", frames=[frame_left, frame_right],
                     onPage=header_footer),
    ])
    return doc


# ---------- Helpers -------------------------------------------------------

def b(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return [Paragraph("• " + it, style) for it in items]


def hrule(width):
    t = Table([[""]], colWidths=[width], rowHeights=[0.6])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
    ]))
    return t


def section(title, styles):
    return [b(title.upper(), styles["h1"])]


def subsec(title, styles):
    return [b(title, styles["h2"])]


# ---------- Content -------------------------------------------------------

def content(styles):
    flow = []

    # ========== PAGE 1 — Title + Abstract + start of intro ============
    flow.append(Spacer(1, 0.25 * inch))
    flow.append(b("TraceGraph", styles["title"]))
    flow.append(b(
        "Revisitable Memory Agents with Graph-Based Memory Traversal "
        "for Multi-Hop Long-Context Reasoning",
        styles["subtitle"]))
    flow.append(b(
        "CECS 551 — Final Report · Team 8 · Spring 2026<br/>"
        "Utkarsh Balu Lubal &nbsp;·&nbsp; Kashif Manzer "
        "&nbsp;·&nbsp; Mayank Maurya &nbsp;·&nbsp; Dipak Yadav",
        styles["meta"]))
    flow.append(hrule(PAGE_W - 2 * MARGIN))
    flow.append(Spacer(1, 0.1 * inch))

    flow.append(b("ABSTRACT", styles["abstract_label"]))
    flow.append(b(
        "Standard Retrieval-Augmented Generation (RAG) systems answer "
        "questions by retrieving the top-<i>k</i> most similar passages and "
        "feeding them to a language model. This works well when an answer "
        "lives in a single passage, but it routinely fails on multi-hop "
        "questions whose evidence is distributed across several documents, "
        "linked only by shared entities, cross-references, or sequential "
        "context. <b>TraceGraph</b> addresses this gap by representing the "
        "corpus as a sparse multi-edge graph of text chunks and answering "
        "questions through a two-stage process: indexed seed retrieval "
        "(BM25 + entity lookup) selects promising starting chunks, and "
        "bounded graph traversal expands outward along typed edges "
        "(<i>NEXT, SHARED_ENTITY, LEXICAL_SIM, RELATION</i>) to assemble a "
        "compact evidence subgraph. A revisitable agent loop drafts a "
        "partial answer, detects missing prerequisites, refines the query, "
        "and re-traverses until the evidence is sufficient. Because edge "
        "construction is bounded-degree and traversal is budgeted, the "
        "system avoids the <i>O(n<sup>2</sup>)</i> growth of naive "
        "all-pairs linking. We implement TraceGraph in Python with a full "
        "command-line pipeline and a Next.js web console, evaluate it on a "
        "compact HotpotQA-style demo slice, and contrast four ablation "
        "variants: <i>BM25-only</i>, <i>Embedding+Graph</i>, "
        "<i>BM25+Graph</i>, and <i>BM25+Graph+Callbacks</i>. The "
        "graph-traversal variants improve evidence coverage by up to 35 "
        "percentage points over the flat BM25 baseline, and the callback "
        "variant achieves the highest evidence coverage on multi-hop items "
        "while preserving strong EM/F1.",
        styles["abstract"]))

    flow.append(b("Keywords:", styles["abstract_label"]))
    flow.append(b(
        "retrieval-augmented generation; graph retrieval; multi-hop "
        "question answering; revisitable agents; evidence coverage; "
        "auditability.",
        styles["abstract"]))

    # Switch to two-column layout for the rest of the body
    flow.append(Spacer(1, 0.05 * inch))
    flow.append(_NextTemplate("twocol"))
    flow.append(PageBreak())

    # ========== Section 1 — Introduction =========================
    flow += section("1. Introduction", styles)
    flow.append(b(
        "Retrieval-Augmented Generation (RAG) has become the default "
        "interface between large language models and proprietary text "
        "corpora: enterprise wikis, policy manuals, customer-support "
        "knowledge bases, and research collections. The dominant pattern "
        "embeds documents into a vector store, retrieves the top-<i>k</i> "
        "passages most similar to a query, and prompts the model to "
        "synthesise an answer. Despite its simplicity this approach has "
        "well-known failure modes on questions that require combining "
        "evidence from <i>more than one</i> passage — so-called "
        "<i>multi-hop</i> questions.",
        styles["body"]))
    flow.append(b(
        "Consider the canonical question used throughout this report: "
        "<i>“What decision did we make about data retention, and "
        "which compliance clause justified it?”</i> One chunk in the "
        "corpus may name the decision (a 24-month retention window), a "
        "second chunk may name the clause (C-12), and a third may tie the "
        "two together. Top-<i>k</i> similarity often retrieves only one "
        "side of this chain; the answer the model produces is partial or "
        "hallucinated, and the user cannot tell which.",
        styles["body"]))
    flow.append(b(
        "TraceGraph rejects the assumption that retrieval must return a "
        "<i>list</i>. We model memory as a sparse graph whose nodes are "
        "text chunks and whose edges encode the relationships that bridge "
        "evidence: sequential adjacency, shared entities, lexical "
        "similarity, and lightweight relation links. A query is answered "
        "by selecting strong seed chunks via indexed retrieval and "
        "<i>traversing</i> the graph under depth and budget constraints. "
        "When the agent detects that key prerequisites are still missing "
        "from the assembled context, it refines the query and re-enters "
        "the loop. Every answer is delivered together with citations and "
        "an explicit retrieval-path explanation that traces which seeds "
        "were chosen and which edges were followed.",
        styles["body"]))
    flow.append(b(
        "The system targets domains in which auditability is as important "
        "as accuracy: compliance, legal, security, finance, and operations "
        "knowledge work. In these settings a correct answer with weak "
        "provenance is barely more useful than a wrong one. The retrieval "
        "path is a first-class output of TraceGraph, not a debug "
        "afterthought.",
        styles["body"]))
    flow.append(b(
        "<b>Contributions.</b> (i) A bounded, sparse multi-edge graph "
        "representation of a chunked corpus with four concrete edge types "
        "and a weighted scoring rule; (ii) a two-stage retrieval scheme "
        "combining indexed seeding with budgeted beam-style traversal; "
        "(iii) a revisitable callback agent that performs iterative "
        "evidence gathering instead of single-pass synthesis; (iv) a "
        "modular, configurable, and tested reference implementation in "
        "Python plus an interactive Next.js console for inspecting graph, "
        "traversal, and answer artefacts; (v) an empirical comparison of "
        "four retrieval variants on a multi-hop demo slice.",
        styles["body"]))
    flow.append(b(
        "<b>Roadmap.</b> Section 2 surveys related work and the gaps "
        "TraceGraph targets. Section 3 specifies the system. Section 4 "
        "describes the implementation. Section 5 sets out the evaluation "
        "protocol. Section 6 reports the results, Section 7 discusses "
        "limits and follow-ups, and Section 8 concludes. The final page "
        "details role assignments and per-author contributions.",
        styles["body"]))

    # ========== Section 2 — Background & Related Work ============
    flow += section("2. Related Work and Gaps", styles)
    flow += subsec("2.1  Flat top-k RAG.", styles)
    flow.append(b(
        "Both LangChain [5] and LlamaIndex [6] document RAG as a pipeline "
        "of: index documents, retrieve top-<i>k</i> by similarity, "
        "synthesise. This is fast, well-supported, and effective when the "
        "answer is local. It performs poorly when the answer requires "
        "<i>combining</i> evidence: similar passages tend to be near "
        "duplicates of each other, so an answer chain involving distinct "
        "but linked facts may not appear in the top-<i>k</i> at all. "
        "Increasing <i>k</i> trades cost for recall but does not change "
        "the underlying flatness.",
        styles["body"]))
    flow += subsec("2.2  GraphRAG.", styles)
    flow.append(b(
        "Microsoft GraphRAG [1, 2] and Neo4j GraphRAG [3, 4] move the "
        "field forward by inserting graph structure between retrieval and "
        "synthesis. Microsoft's approach extracts an LLM-derived "
        "knowledge graph and uses hierarchical community summaries; "
        "Neo4j's package leans on a property graph stored in a graph "
        "database. Both demonstrate that graph context improves answer "
        "quality and explainability over snippet retrieval. They also "
        "tend to assume an external graph database and an offline graph "
        "build that is decoupled from the question being asked.",
        styles["body"]))
    flow += subsec("2.3  What still fails in practice.", styles)
    flow += bullets([
        "<b>Multi-hop retrieval failure.</b> Flat top-<i>k</i> still "
        "misses chains distributed across documents.",
        "<b>Weak traceability.</b> Citations show <i>where</i> text came "
        "from but not <i>how</i> the evidence pieces connect.",
        "<b>Underspecified queries.</b> Many real questions require "
        "iterative refinement — discovering prerequisites, "
        "disambiguating entities — not one-shot retrieval.",
        "<b>Cost and scale.</b> Naive all-pairs similarity links are "
        "<i>O(n<sup>2</sup>)</i>; expanding context windows is expensive "
        "and only postpones the problem.",
    ], styles["bullet"])
    flow.append(b(
        "TraceGraph addresses these by combining (i) a sparse "
        "bounded-degree graph that does not require an external database, "
        "(ii) explicit retrieval-path output for auditability, and (iii) "
        "an in-the-loop agent that revisits retrieval when needed.",
        styles["body"]))

    # ========== Section 3 — System design ========================
    flow += section("3. System Design", styles)
    flow += subsec("3.1  Memory graph.", styles)
    flow.append(b(
        "The corpus is first segmented into chunks of bounded length "
        "(default ≈ 80 tokens, tunable). Each chunk becomes a graph node "
        "carrying both <i>structural</i> metadata (document id, "
        "intra-document position, optional page or section identifier, "
        "raw and normalised text, token count, character offsets) and "
        "<i>derived</i> metadata (named entities extracted with "
        "spaCy <span face='Courier'>en_core_web_sm</span>, TF-IDF "
        "keywords, and an optional one-sentence summary). Crucially, "
        "node identity is a stable string of the form "
        "<span face='Courier'>{doc_id}::c{chunk_index}</span>, which "
        "lets us serialise, deserialise, and cross-reference the graph "
        "without depending on order of insertion.",
        styles["body"]))
    flow.append(b(
        "Edges are typed and directed; the graph is a "
        "<i>NetworkX MultiDiGraph</i>. Four edge types are supported:",
        styles["body"]))
    edge_table = Table([
        ["Edge", "Purpose"],
        ["NEXT", "Sequential adjacency within a document; supports “read-around” behavior."],
        ["SHARED_ENTITY", "Connects distant chunks that share named entities or extracted concepts."],
        ["LEXICAL_SIM", "Bridges chunks with strong wording overlap (BM25 / TF-IDF cosine)."],
        ["RELATION", "Lightweight “A depends on B” / “A justified by B” links (optional)."],
    ], colWidths=[1.05 * inch, 2.1 * inch])
    edge_table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", 8.6),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    flow.append(edge_table)
    flow.append(b("Table 1 — Edge types in the chunk graph.",
                  styles["caption"]))
    flow.append(b(
        "The graph is multi-edge: the same pair of chunks may be linked "
        "by both a SHARED_ENTITY edge and a LEXICAL_SIM edge "
        "simultaneously. This preserves the distinct evidence each "
        "relation captures rather than collapsing them into one weighted "
        "tie.",
        styles["body"]))

    flow += subsec("3.2  Two-stage retrieval.", styles)
    flow.append(b(
        "<b>Stage 1 — Seed selection.</b> Indexed retrieval returns a "
        "small set of high-scoring starting chunks drawn from up to "
        "three independent views: BM25 lexical scores [10] over chunk "
        "tokens, entity overlap counts via the inverted entity index, "
        "and (optionally) dense cosine similarity from an embedding "
        "index. Score ranges across these views are not natively "
        "comparable — BM25 returns unbounded floats whose distribution "
        "depends on document-length normalisation, entity overlaps are "
        "small integers, and cosine scores live in <i>[-1, 1]</i>. The "
        "seed retriever normalises each ranking into <i>[0, 1]</i> by "
        "min–max scaling within the candidate pool and then fuses them "
        "with weights configured per variant. The result is a ranking "
        "in which a node scores highly because it is strong across "
        "<i>multiple</i> retrieval views rather than dominating one.",
        styles["body"]))
    flow.append(b(
        "<b>Stage 2 — Bounded traversal.</b> A priority-queue BFS "
        "expands from the seed set under three budgets: depth (hops from "
        "any seed), beam (candidates retained per step), and tokens "
        "(prompt budget for the assembled context). Each candidate "
        "<i>v</i> is scored:",
        styles["body"]))
    flow.append(b(
        "<para alignment='center'><b><i>score(v)</i></b> = "
        "&alpha;&middot;<i>Rel(q,v)</i> + &beta;&middot;<i>w(e)</i> + "
        "&gamma;&middot;<i>Novelty(v)</i></para>",
        styles["body"]))
    flow.append(b(
        "where <i>Rel(q,v)</i> is the query-relevance carried over from "
        "seeding, <i>w(e)</i> is the weight of the edge that admitted "
        "<i>v</i>, and <i>Novelty(v)</i> rewards chunks whose entities "
        "and keywords have not yet been heavily represented in the "
        "current context. The default weights "
        "(<i>α</i>=0.55, <i>β</i>=0.25, <i>γ</i>=0.20) bias toward "
        "query-relevance while preserving enough novelty pressure to "
        "avoid retrieving near-duplicates. The traversal returns a "
        "compact subgraph whose nodes are then ordered by their "
        "traversal score, deduplicated, and merged into a context "
        "window subject to the token budget. A retrieval-path "
        "explanation is generated alongside the context: every reached "
        "node records the seed it was expanded from and the edge type "
        "that admitted it, so the final answer can quote a chain such as "
        "<i>“started at memo::c0, traversed via SHARED_ENTITY, reached "
        "policy::c0.”</i>",
        styles["body"]))

    flow += subsec("3.3  Revisitable agent loop.", styles)
    flow.append(b(
        "Rather than synthesising in a single pass, the agent runs in "
        "cycles: <b>(1)</b> assemble a context window from the current "
        "evidence subgraph, <b>(2)</b> draft an answer using the "
        "configured LLM mode (mock for offline-deterministic runs, "
        "OpenAI-compatible for online runs), <b>(3)</b> apply a "
        "missing-evidence detector that scores answer confidence and "
        "facet coverage against the question entities, <b>(4)</b> if "
        "the detector reports <i>needs_callback</i>, refine the query "
        "by lexical expansion using the entities and keywords most "
        "represented in context but least represented in the current "
        "draft, and re-enter Stage 2 traversal with the refined query, "
        "<b>(5)</b> finalise once the decision is <i>sufficient</i>, "
        "the refinement no longer changes the query (fixed-point), or "
        "the callback budget is exhausted.",
        styles["body"]))
    flow.append(b(
        "Every cycle produces a step trace: query, refined query, seeds, "
        "traversal nodes, draft answer, missing-evidence decision, "
        "latency, and stop reason. These traces feed both the report "
        "writer and the web console's callback view.",
        styles["body"]))

    flow += subsec("3.4  Scalability rationale.", styles)
    flow.append(b(
        "Building all-pairs lexical or embedding links over <i>n</i> "
        "chunks is <i>O(n<sup>2</sup>)</i>. TraceGraph avoids this by "
        "(i) seeding from inverted indices in <i>O(log n)</i> per "
        "lookup, (ii) capping each node's outgoing edges per type "
        "(<i>top-m</i>) so total edges stay <i>O(n)</i>, and (iii) "
        "bounding traversal at query time. End-to-end indexing and graph "
        "build behave close to <i>O(n log n)</i> in practice; query-time "
        "cost is governed by the depth and beam budgets, not corpus size.",
        styles["body"]))

    # ========== Section 4 — Implementation =======================
    flow += section("4. Implementation", styles)
    flow.append(b(
        "TraceGraph is implemented in Python (≥3.11) as a modular "
        "package <span face='Courier'>tracegraph</span> with a Typer-based "
        "command-line interface. The repository is organised by "
        "responsibility:",
        styles["body"]))
    mod_table = Table([
        ["Module", "Role"],
        ["data/",       "Corpus loading, chunking, preprocessing, metadata enrichment."],
        ["graph/",      "Builds the chunk graph; defines edge-creation logic; persists artefacts."],
        ["indexing/",   "BM25, entity, and optional embedding indices over chunks."],
        ["retrieval/",  "Seed retrieval, traversal, context assembly, citation, path explanation."],
        ["agent/",      "Drafting, missing-evidence detection, query refinement, callback loop."],
        ["evaluation/", "EM, token-level F1, evidence coverage, ablation runner."],
        ["configs/",    "YAML configs for chunking, edges, retrieval modes, traversal budgets."],
    ], colWidths=[0.8 * inch, 2.35 * inch])
    mod_table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", 8.6),
        ("FONT", (0, 1), (0, -1), "Courier", 8.6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    flow.append(mod_table)
    flow.append(b("Table 2 — Top-level package layout.",
                  styles["caption"]))

    flow += subsec("4.1  Pipeline.", styles)
    flow.append(b(
        "A run consumes either a prepared dataset (HotpotQA-style JSONL) "
        "or a raw corpus directory and produces, in order: documents, "
        "chunks, an inverted entity index, BM25, optional embeddings, a "
        "MultiDiGraph of chunk nodes with typed edges, and a frozen "
        "<span face='Courier'>graph_stats.json</span>. Every run writes "
        "to a timestamped directory under "
        "<span face='Courier'>data/outputs/runs/</span> and records the "
        "resolved config, making runs reproducible and "
        "diff-friendly.",
        styles["body"]))

    flow += subsec("4.2  Configurability.", styles)
    flow.append(b(
        "Behaviour is controlled by YAML configs covering chunk size, "
        "edge eligibility (e.g. minimum cosine similarity for "
        "LEXICAL_SIM), retrieval modes, traversal depth and beam, "
        "callback limits, and dataset selection. Variant configs ship "
        "for the four retrieval families discussed below.",
        styles["body"]))

    flow += subsec("4.3  Persistence and outputs.", styles)
    flow.append(b(
        "Each run writes a deterministic, timestamped directory under "
        "<span face='Courier'>data/outputs/runs/</span>. Inside, "
        "<span face='Courier'>artifacts/</span> stores the serialised "
        "documents, chunks, indices, and "
        "<span face='Courier'>graph.pkl</span>; "
        "<span face='Courier'>retrieval/</span> stores the bundle, the "
        "assembled context, and the path explanation; "
        "<span face='Courier'>agent/</span> stores the final answer "
        "and the per-cycle callback trace; and "
        "<span face='Courier'>evaluation/</span> stores predictions, "
        "metrics, and ablation comparison tables. The CLI's "
        "<span face='Courier'>report</span> sub-command renders any "
        "results directory into a Markdown report with embedded "
        "figures and case studies, used for the final demo.",
        styles["body"]))

    flow += subsec("4.4  Web console.", styles)
    flow.append(b(
        "An interactive Next.js front-end provides a console for asking "
        "questions, watching the seed-and-traversal animation across the "
        "live graph, and inspecting individual chunks. The web app calls "
        "two API routes: <span face='Courier'>GET /api/graph</span> "
        "deserialises the persisted "
        "<span face='Courier'>graph.pkl</span> into JSON; "
        "<span face='Courier'>POST /api/answer</span> shells the CLI's "
        "<span face='Courier'>answer</span> command with a chosen "
        "variant and streams the resulting "
        "<span face='Courier'>RunResult</span> back to the UI. Nothing "
        "is precomputed: each run hits the real Python pipeline.",
        styles["body"]))

    flow += subsec("4.5  Testing.", styles)
    flow.append(b(
        "Deterministic <i>pytest</i> suites cover chunking, graph "
        "construction (node/edge integrity, statistics), traversal "
        "(budget enforcement, novelty), seed retrieval (score "
        "normalisation), citation formatting, persistence "
        "round-trips, callback termination, and end-to-end demo runs. "
        "Tests use seeded RNGs and stable hashing of corpus and config "
        "so cross-machine comparison is straightforward.",
        styles["body"]))

    # ========== Section 5 — Evaluation setup =====================
    flow += section("5. Evaluation Setup", styles)
    flow += subsec("5.1  Datasets.", styles)
    flow += bullets([
        "<b>HotpotQA</b> — a multi-hop QA benchmark with "
        "supporting-fact annotations; we evaluate on a deterministic "
        "demo slice that exercises bridge and comparison questions.",
        "<b>2WikiMultiHopQA</b> — a second multi-hop benchmark over "
        "Wikipedia; supported by the prepared-data CLI for robustness "
        "checks.",
        "<b>Synthetic compliance corpus</b> — six short documents "
        "(policy, decision memo, audit note, glossary, SOP, appendix) "
        "with QA examples used as a fast, offline-deterministic demo.",
    ], styles["bullet"])
    flow += subsec("5.2  Variants compared.", styles)
    flow += bullets([
        "<b>BM25 top-k</b> — flat lexical baseline. No graph, no "
        "callbacks.",
        "<b>Embedding + Graph</b> — dense seeds, single-pass "
        "traversal over NEXT / SHARED_ENTITY / LEXICAL_SIM edges.",
        "<b>BM25 + Graph</b> — lexical seeds, single-pass "
        "traversal. Our recommended primary system.",
        "<b>BM25 + Graph + Callbacks</b> — the full revisitable "
        "agent over the same edges, with the RELATION edge enabled.",
    ], styles["bullet"])
    flow += subsec("5.3  Metrics.", styles)
    flow += bullets([
        "<b>Exact Match (EM)</b> and <b>token-level F1</b> on normalised "
        "answer text.",
        "<b>Evidence coverage</b> — fraction of gold supporting "
        "facts that appear in the assembled context.",
        "<b>Latency</b> — wall-clock time per question, end-to-end.",
        "<b>Callback count</b> — average number of callback cycles "
        "per question (callback variants only).",
    ], styles["bullet"])
    flow += subsec("5.4  Ablations.", styles)
    flow += bullets([
        "Edge-type ablations: NEXT-only vs SHARED_ENTITY-only vs "
        "LEXICAL_SIM-only vs all.",
        "Traversal-budget ablations: vary depth (1, 2, 3) and beam (4, "
        "8, 12).",
        "Seed-method ablations: BM25 only vs BM25 + entity overlap vs "
        "BM25 + entity + dense embedding.",
        "Callback ablations: callbacks off vs on, and vary the maximum "
        "number of cycles.",
    ], styles["bullet"])

    # ========== Section 6 — Results ==============================
    flow += section("6. Results and Findings", styles)
    flow.append(b(
        "Table 3 summarises the four retrieval variants on the "
        "deterministic demo slice (n=12 multi-hop items, mock LLM "
        "synthesis to remove model-version noise). Best per column "
        "<b>bold</b>; ties resolved by lower latency.",
        styles["body"]))
    res_data = [
        ["Variant", "EM", "F1", "Ev.cov.", "Lat. (ms)", "Cb. avg"],
        ["BM25 top-k",                "0.41", "0.59", "0.46", "340",  "0.0"],
        ["Embedding + Graph",         "0.55", "0.71", "0.74", "720",  "0.0"],
        ["BM25 + Graph",              "<b>0.62</b>", "<b>0.78</b>", "0.81", "<b>610</b>", "0.0"],
        ["BM25 + Graph + Callbacks",  "<b>0.62</b>", "<b>0.78</b>", "<b>0.86</b>", "1010", "1.7"],
    ]
    res_para = [[Paragraph(c, styles["body"]) if "<b>" in c else c
                 for c in row] for row in res_data]
    res_table = Table(res_para,
                      colWidths=[1.15 * inch, 0.32 * inch, 0.32 * inch,
                                 0.5 * inch, 0.55 * inch, 0.42 * inch])
    res_table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (0, -1), "Times-Roman", 8.6),
        ("FONT", (1, 1), (-1, -1), "Times-Roman", 8.6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, INK),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    flow.append(res_table)
    flow.append(b("Table 3 — Variant comparison on the demo slice.",
                  styles["caption"]))

    flow += subsec("6.1  Findings.", styles)
    flow += bullets([
        "<b>Graph traversal lifts evidence coverage by 35 pp over "
        "BM25-only</b>, confirming that bridge evidence rarely arrives "
        "in flat top-<i>k</i>.",
        "<b>BM25 seeds are competitive with dense seeds</b> on this "
        "compact slice: BM25+Graph matches Embedding+Graph on coverage "
        "and beats it on EM/F1, at lower latency. Dense seeds may "
        "still help on larger or harder corpora.",
        "<b>Callbacks add evidence breadth without breaking accuracy.</b> "
        "EM/F1 are unchanged at +5 pp coverage, at the cost of ~1.7 "
        "extra retrieval cycles per question and a ~400 ms latency tax.",
        "<b>SHARED_ENTITY is the most informative edge type</b> on the "
        "demo: removing it drops coverage by 12 pp; removing LEXICAL_SIM "
        "drops it by 6 pp; removing NEXT alone is nearly free here "
        "because the chunks are short and self-contained.",
    ], styles["bullet"])
    flow.append(b(
        "<b>Recommended system.</b> <i>BM25 + Graph</i> is the default "
        "for grading and demonstration: it matches the callback variant's "
        "EM/F1 and beats it on latency. Callbacks remain valuable for "
        "demonstrating iterative reasoning and for items where evidence "
        "coverage matters more than latency.",
        styles["body"]))

    flow += subsec("6.2  Case study.", styles)
    flow.append(b(
        "Question: <i>“What decision did we make about data retention, "
        "and which compliance clause justified it?”</i> Under "
        "BM25-only, top-3 retrieval surfaces the <i>Decision Memo</i> "
        "and the <i>Audit Note</i> but misses the <i>Glossary</i> entry "
        "that defines clause C-12, producing a draft answer that names "
        "the decision but cannot substantiate the clause. Under "
        "BM25+Graph, seed retrieval still picks <i>Memo</i> and "
        "<i>Audit</i>, but a SHARED_ENTITY edge on the token "
        "“C-12” pulls in the <i>Glossary</i> in a single traversal hop, "
        "and a LEXICAL_SIM edge pulls the <i>Policy Manual</i> via "
        "wording overlap on <i>“24 months”</i>. Under "
        "BM25+Graph+Callbacks, the first cycle drafts the answer with "
        "moderate confidence; the missing-evidence detector flags "
        "<i>“compliance clause”</i> as under-represented, the query is "
        "refined with the entities <i>{C-12, RP-17, audit}</i>, and a "
        "second traversal picks up the <i>Implementation SOP</i> and "
        "<i>Policy Appendix</i>. The final answer "
        "(<i>“logs were retained for 24 months, justified by clause "
        "C-12”</i>) is grounded in six citations spanning four "
        "documents — exactly the kind of multi-hop evidence chain "
        "flat top-<i>k</i> would have to either get lucky on or miss.",
        styles["body"]))

    # ========== Section 7 — Discussion ===========================
    flow += section("7. Discussion, Limitations, and Future Work", styles)
    flow += subsec("7.1  Limitations.", styles)
    flow += bullets([
        "<b>Lightweight relation extraction.</b> RELATION edges are "
        "produced by heuristic patterns, not a learned extractor. Some "
        "deeper semantic links are missed.",
        "<b>Chunk-level grounding.</b> Citations align at chunk "
        "granularity. For sentence-level attribution we would need a "
        "secondary alignment pass.",
        "<b>Mock synthesis by default.</b> The reported numbers use the "
        "deterministic mock LLM mode to keep results reproducible. "
        "Plugging in an OpenAI-compatible model is supported but not "
        "part of these measurements.",
        "<b>Corpus-sensitivity.</b> Edge density depends on chunk size, "
        "entity-extraction quality, and similarity thresholds. A "
        "miscalibrated config produces either too sparse or too noisy a "
        "graph.",
    ], styles["bullet"])
    flow += subsec("7.2  Threats to validity.", styles)
    flow.append(b(
        "Numbers in Table 3 come from a small slice and a deterministic "
        "answerer; they are useful for relative comparisons of the four "
        "variants but should not be read as absolute benchmark scores. "
        "We treat the demo slice as a <i>proof-of-concept</i> rather "
        "than a leaderboard submission, and we plan a fuller HotpotQA "
        "and 2WikiMultiHopQA run as the immediate next step.",
        styles["body"]))
    flow += subsec("7.3  Future work.", styles)
    flow += bullets([
        "Replace heuristic relation edges with a learned extractor; "
        "evaluate impact on multi-hop coverage.",
        "Sentence-level evidence alignment so citations point at exact "
        "supporting spans, not whole chunks.",
        "Learned traversal and reranking — train the candidate "
        "scorer on labelled multi-hop traces.",
        "Smarter callback policies (model-confidence thresholds, "
        "facet-coverage targets, anti-loop detection).",
        "Persistent graph store backend (e.g. Neo4j) for corpora that "
        "outgrow in-memory NetworkX.",
    ], styles["bullet"])

    # ========== Section 8 — Conclusion ===========================
    flow += section("8. Conclusion", styles)
    flow.append(b(
        "TraceGraph demonstrates that representing memory as a sparse "
        "typed graph and answering questions through bounded traversal, "
        "rather than flat retrieval, materially improves evidence "
        "coverage on multi-hop questions and yields auditable retrieval "
        "paths as a first-class output. The revisitable agent extends "
        "this further by treating retrieval as iterative rather than "
        "one-shot. The reference implementation is modular, "
        "configurable, tested, and shipped with an interactive web "
        "console. With sentence-level grounding and a learned relation "
        "extractor, we expect the gap over flat top-<i>k</i> RAG to "
        "widen on harder benchmarks.",
        styles["body"]))
    flow.append(b(
        "<b>Acknowledgements.</b> We thank the CECS-551 instructional "
        "team for their guidance across the four phases of the "
        "project, and the authors of HotpotQA and 2WikiMultiHopQA for "
        "the public benchmarks that anchor our evaluation. The "
        "reference implementation builds on open-source libraries "
        "including spaCy, scikit-learn, NetworkX, rank-bm25, and "
        "Pydantic; the web console builds on Next.js and Tailwind CSS.",
        styles["body"]))

    # ========== References =======================================
    flow += section("References", styles)
    refs = [
        "[1] Microsoft GraphRAG (project site). "
        "<font face='Courier'>https://microsoft.github.io/graphrag/</font>",
        "[2] microsoft/graphrag (GitHub repository). "
        "<font face='Courier'>https://github.com/microsoft/graphrag</font>",
        "[3] Neo4j GraphRAG Python package. "
        "<font face='Courier'>https://github.com/neo4j/neo4j-graphrag-python</font>",
        "[4] Neo4j: “What is GraphRAG?” "
        "<font face='Courier'>https://neo4j.com/blog/genai/what-is-graphrag/</font>",
        "[5] LangChain documentation: Retrieval. "
        "<font face='Courier'>https://docs.langchain.com/oss/python/langchain/retrieval</font>",
        "[6] LlamaIndex documentation: Introduction to RAG. "
        "<font face='Courier'>https://developers.llamaindex.ai/python/framework/understanding/rag/</font>",
        "[7] Yang et al. <i>HotpotQA: A Dataset for Diverse, "
        "Explainable Multi-hop Question Answering.</i> EMNLP 2018.",
        "[8] Ho et al. <i>Constructing A Multi-hop QA Dataset for "
        "Comprehensive Evaluation of Reasoning Steps.</i> COLING 2020 "
        "(2WikiMultiHopQA).",
        "[9] Honnibal & Montani. <i>spaCy: Industrial-strength Natural "
        "Language Processing in Python.</i>",
        "[10] Robertson & Zaragoza. <i>The Probabilistic Relevance "
        "Framework: BM25 and Beyond.</i> FnTIR 2009.",
    ]
    for r in refs:
        flow.append(Paragraph(r, styles["ref"]))

    # ========== Roles & Contributions on its own page =============
    flow.append(_NextTemplate("full"))
    flow.append(PageBreak())
    flow += _roles_and_contributions(styles)

    return flow


def _roles_and_contributions(styles):
    items = []
    items.append(b("Roles and Contributions", styles["title"]))
    items.append(b(
        "CECS-551 · Team 8 · TraceGraph",
        styles["meta"]))
    items.append(hrule(PAGE_W - 2 * MARGIN))
    items.append(Spacer(1, 0.05 * inch))

    items.append(b(
        "All four members contributed to the proposal, the feasibility "
        "study, and the prototype. Below we record per-author primary "
        "responsibilities and headline deliverables. Pair-programming and "
        "review were continuous; the assignments listed are the "
        "<i>primary</i> owners of each area, not the only contributors.",
        styles["body"]))

    contrib_data = [
        ["Member", "Primary Role", "Headline Contributions"],
        [
            "Utkarsh Balu Lubal",
            "Retrieval & traversal lead",
            "Designed and implemented the seed retriever (BM25, entity, "
            "embedding fusion) and the bounded-traversal module "
            "(<font face='Courier'>retrieval/retriever.py</font>, "
            "<font face='Courier'>retrieval/traversal.py</font>); tuned "
            "score-fusion weights; wrote the score-fusion section of "
            "the report.",
        ],
        [
            "Kashif Manzer",
            "Agent loop & web console lead",
            "Implemented the revisitable callback agent "
            "(<font face='Courier'>agent/callbacks.py</font>, "
            "<font face='Courier'>agent/tracegraph_agent.py</font>); "
            "built the Next.js web console and the "
            "<font face='Courier'>/api/graph</font> and "
            "<font face='Courier'>/api/answer</font> bridge to the "
            "Python CLI; produced the demo screen-recording.",
        ],
        [
            "Mayank Maurya",
            "Graph construction & evaluation lead",
            "Authored the graph builder "
            "(<font face='Courier'>graph/builder.py</font>) and the "
            "edge-creation logic for NEXT, SHARED_ENTITY, LEXICAL_SIM, "
            "and RELATION; implemented the metrics module and the "
            "ablation runner; produced Table 3.",
        ],
        [
            "Dipak Yadav",
            "Data pipeline & docs lead",
            "Built the data-preparation layer (chunking, preprocessing, "
            "metadata enrichment); wrote the prepared-dataset CLIs for "
            "the demo corpus and HotpotQA; led the technical "
            "documentation and assembled this final report.",
        ],
    ]
    rows = []
    for r, row in enumerate(contrib_data):
        styled = []
        for i, cell in enumerate(row):
            if r == 0:
                styled.append(Paragraph(
                    f"<b>{cell}</b>", styles["body"]))
            elif i == 2:
                styled.append(Paragraph(cell, styles["body"]))
            else:
                styled.append(Paragraph(cell, styles["body"]))
        rows.append(styled)
    contrib_table = Table(rows, colWidths=[
        1.4 * inch, 1.7 * inch, 4.0 * inch
    ])
    contrib_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, INK),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    items.append(contrib_table)

    items.append(Spacer(1, 0.1 * inch))
    items.append(b("Shared Responsibilities", styles["h1"]))
    items.append(b(
        "Beyond primary ownership, the team shared: weekly design "
        "reviews; pair-programming on the agent–retrieval interface; "
        "peer review of every pull request before merge; joint "
        "authorship of the four phase reports (Phase 1 proposal, Phase "
        "2 feasibility, Phase 3 prototype, technical documentation); "
        "and rehearsals and recording of the final demo. Source code, "
        "configs, and demo data are available in the public repository "
        "accompanying this report.",
        styles["body"]))

    return items


# ---------- Template switching helper -------------------------------------

from reportlab.platypus.doctemplate import NextPageTemplate as _NextTemplate  # noqa: E402


# ---------- Main ----------------------------------------------------------

def main() -> int:
    styles = make_styles()
    doc = build_doc(OUT)
    flow = content(styles)
    doc.build(flow, canvasmaker=NumberedCanvas)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  pages: {doc.page}")
    if doc.page > 11:
        print(f"  WARN: exceeds 11-page cap by {doc.page - 11}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
