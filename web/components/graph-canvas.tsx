"use client";

import { useMemo, useRef } from "react";
import type { EdgeType, GraphEdge, GraphNode, StepTrace } from "@/lib/types";

const edgeColor: Record<EdgeType, string> = {
  NEXT: "var(--color-edge-next)",
  SHARED_ENTITY: "var(--color-edge-shared)",
  LEXICAL_SIM: "var(--color-edge-lex)",
  RELATION: "var(--color-edge-rel)",
};

const edgeDash: Record<EdgeType, string> = {
  NEXT: "0",
  SHARED_ENTITY: "0",
  LEXICAL_SIM: "4 3",
  RELATION: "1 4",
};

export type GraphPhase =
  | "idle"
  | "seeding"
  | "traversing"
  | "drafting"
  | "detecting"
  | "refining"
  | "callback"
  | "finalizing"
  | "done";

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  activeStep: StepTrace | null;
  contextNodes: Set<string>;
  phase: GraphPhase;
  hoverNode: string | null;
  onHover: (id: string | null) => void;
  selectedNode: string | null;
  onSelect: (id: string | null) => void;
  source: "live" | "mock";
}

type NodeState = "idle" | "seed" | "traversed" | "context" | "candidate";

export function GraphCanvas({
  nodes,
  edges,
  activeStep,
  contextNodes,
  phase,
  hoverNode,
  onHover,
  selectedNode,
  onSelect,
  source,
}: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  const nodeMap = useMemo(
    () => Object.fromEntries(nodes.map((n) => [n.id, n])),
    [nodes]
  );

  const stateFor = (id: string): NodeState => {
    if (phase === "idle" && !activeStep) return "idle";
    if (phase === "done") {
      return contextNodes.has(id) ? "context" : "candidate";
    }
    const seeds = new Set(activeStep?.seeds ?? []);
    const reached = new Set(activeStep?.traversal_nodes ?? []);
    if (phase === "seeding") {
      return seeds.has(id) ? "seed" : "candidate";
    }
    if (reached.has(id)) return "traversed";
    if (seeds.has(id)) return "seed";
    return "candidate";
  };

  const nodeFill = (s: NodeState) =>
    s === "seed"
      ? "var(--color-signal)"
      : s === "traversed" || s === "context"
      ? "var(--color-ink)"
      : "var(--color-paper)";

  const nodeText = (s: NodeState) =>
    s === "seed" || s === "traversed" || s === "context"
      ? "var(--color-paper)"
      : "var(--color-ink)";

  const traversalActive =
    phase === "traversing" ||
    phase === "drafting" ||
    phase === "detecting" ||
    phase === "refining" ||
    phase === "callback";

  const handleBgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (e.target === svgRef.current) onSelect(null);
  };

  return (
    <div className="border border-ink/90 bg-paper relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Plate II — Sparse Chunk Graph
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70 flex items-center gap-2">
          <span
            className={`inline-block w-1.5 h-1.5 ${
              source === "live" ? "bg-signal" : "bg-mute"
            }`}
          />
          {source} · n={nodes.length} · m={edges.length}
        </div>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 border-b border-ink-3/30 px-4 py-1.5 bg-paper-2/40 font-mono text-[10px] uppercase tracking-[0.18em]">
        {Array.from(new Set(edges.map((e) => e.type))).map((t) => (
          <Legend key={t} swatch={edgeColor[t]} label={t} dash={edgeDash[t]} />
        ))}
        <span className="ml-auto text-ink-3">
          ◇ seed · ● traversed · ◼ context · ○ candidate
        </span>
      </div>

      <div className="relative">
        <svg
          ref={svgRef}
          viewBox="0 0 920 500"
          className="block w-full h-[460px]"
          preserveAspectRatio="xMidYMid meet"
          onClick={handleBgClick}
        >
          <defs>
            <pattern
              id="grid"
              x="0"
              y="0"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 24 0 L 0 0 0 24"
                fill="none"
                stroke="rgba(19,18,16,0.06)"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="920" height="500" fill="url(#grid)" />

          <g stroke="rgba(19,18,16,0.7)" strokeWidth="1" fill="none">
            <line x1="20" y1="20" x2="40" y2="20" />
            <line x1="20" y1="20" x2="20" y2="40" />
            <line x1="900" y1="20" x2="880" y2="20" />
            <line x1="900" y1="20" x2="900" y2="40" />
            <line x1="20" y1="480" x2="40" y2="480" />
            <line x1="20" y1="480" x2="20" y2="460" />
            <line x1="900" y1="480" x2="880" y2="480" />
            <line x1="900" y1="480" x2="900" y2="460" />
          </g>

          {/* Edges + particles */}
          <g>
            {edges.map((e, i) => {
              const a = nodeMap[e.source];
              const b = nodeMap[e.target];
              if (!a || !b) return null;
              const sa = stateFor(e.source);
              const sb = stateFor(e.target);
              const seeds = new Set(activeStep?.seeds ?? []);
              const reached = new Set(activeStep?.traversal_nodes ?? []);
              const isTraversing =
                traversalActive &&
                ((seeds.has(e.source) && reached.has(e.target)) ||
                  (seeds.has(e.target) && reached.has(e.source)));
              const inContext =
                phase === "done" && sa === "context" && sb === "context";
              const dimmed =
                hoverNode && hoverNode !== e.source && hoverNode !== e.target;
              const idle = phase === "idle" && !activeStep;

              const mx = (a.x + b.x) / 2;
              const my = (a.y + b.y) / 2;
              const dx = b.x - a.x;
              const dy = b.y - a.y;
              const len = Math.hypot(dx, dy) || 1;
              const offset = 30 * (i % 2 === 0 ? 1 : -1);
              const cx = mx + (-dy / len) * offset;
              const cy = my + (dx / len) * offset;
              const pathId = `tg-edge-${i}`;
              const d = `M ${a.x} ${a.y} Q ${cx} ${cy} ${b.x} ${b.y}`;
              const reverse = seeds.has(e.target) && reached.has(e.source);
              const dr = reverse
                ? `M ${b.x} ${b.y} Q ${cx} ${cy} ${a.x} ${a.y}`
                : d;

              return (
                <g
                  key={i}
                  opacity={
                    dimmed
                      ? 0.12
                      : idle
                      ? 0.5
                      : inContext
                      ? 1
                      : isTraversing
                      ? 1
                      : 0.4
                  }
                  style={{ transition: "opacity 280ms ease" }}
                >
                  <path
                    id={pathId}
                    d={d}
                    stroke={edgeColor[e.type]}
                    strokeWidth={
                      e.type === "SHARED_ENTITY"
                        ? 1.6 + e.weight * 1.2
                        : e.type === "RELATION"
                        ? 1.0
                        : 1.2 + e.weight * 0.6
                    }
                    fill="none"
                    strokeDasharray={edgeDash[e.type]}
                    strokeLinecap="round"
                    className={isTraversing ? "edge-active" : ""}
                  />
                  {isTraversing && (
                    <>
                      {/* a hidden direction-aware path so motion goes seed → reached */}
                      <path id={`${pathId}-mp`} d={dr} fill="none" stroke="none" />
                      <circle r="4" fill="var(--color-signal)" className="particle">
                        <animateMotion
                          dur="1.2s"
                          repeatCount="indefinite"
                          rotate="auto"
                          keyTimes="0;1"
                          keyPoints="0;1"
                        >
                          <mpath href={`#${pathId}-mp`} />
                        </animateMotion>
                      </circle>
                      <circle r="2" fill="var(--color-signal)" opacity="0.55" className="particle">
                        <animateMotion
                          dur="1.2s"
                          begin="0.4s"
                          repeatCount="indefinite"
                          rotate="auto"
                        >
                          <mpath href={`#${pathId}-mp`} />
                        </animateMotion>
                      </circle>
                    </>
                  )}
                </g>
              );
            })}
          </g>

          {/* Nodes */}
          <g>
            {nodes.map((n) => {
              const s = stateFor(n.id);
              const isHover = hoverNode === n.id;
              const isSelected = selectedNode === n.id;

              return (
                <g
                  key={n.id}
                  transform={`translate(${n.x}, ${n.y})`}
                  onMouseEnter={() => onHover(n.id)}
                  onMouseLeave={() => onHover(null)}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(isSelected ? null : n.id);
                  }}
                  style={{ cursor: "pointer" }}
                >
                  {/* outer rings */}
                  {s === "seed" && (
                    <circle
                      r="22"
                      fill="none"
                      stroke="var(--color-signal)"
                      strokeWidth="1"
                      strokeDasharray="2 3"
                      className="node-ring"
                    />
                  )}
                  {s === "context" && (
                    <circle
                      r="22"
                      fill="none"
                      stroke="var(--color-ink)"
                      strokeWidth="0.8"
                      className="node-ring"
                    />
                  )}
                  {/* selected ring sits outermost */}
                  {isSelected && (
                    <circle
                      r="26"
                      fill="none"
                      stroke="var(--color-ink)"
                      strokeWidth="2"
                      className="node-selected-ring"
                    />
                  )}

                  {/* hit area */}
                  <circle r="24" fill="transparent" />

                  <circle
                    r={isHover || isSelected ? 17 : 14}
                    fill={nodeFill(s)}
                    stroke="var(--color-ink)"
                    strokeWidth={s === "candidate" ? 1.2 : 1.5}
                    className={`node-body ${s === "seed" ? "seed-pulse" : ""}`}
                  />
                  <text
                    textAnchor="middle"
                    dy="3.5"
                    fontFamily="var(--font-mono)"
                    fontSize="10"
                    fontWeight="700"
                    fill={nodeText(s)}
                    letterSpacing="0.5"
                    style={{
                      transition: "fill 380ms cubic-bezier(0.2, 0.8, 0.2, 1)",
                      pointerEvents: "none",
                    }}
                  >
                    {n.id.split("::")[0].slice(0, 3).toUpperCase()}
                  </text>
                  <g transform="translate(0, 32)" style={{ pointerEvents: "none" }}>
                    <text
                      textAnchor="middle"
                      fontFamily="var(--font-mono)"
                      fontSize="9"
                      fill={isSelected ? "var(--color-signal)" : "var(--color-ink)"}
                      letterSpacing="1"
                      style={{ transition: "fill 250ms ease" }}
                    >
                      {n.doc_title.toUpperCase()}
                    </text>
                  </g>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      <div className="border-t border-ink-3/30 px-4 py-1.5 flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.18em] text-ink-3 bg-paper-2/40">
        <span>
          {phase === "idle"
            ? "click a node to inspect · run a trace to animate seeds → traversal"
            : phase === "done" && activeStep
            ? `final · ${contextNodes.size} context nodes · click any node to inspect`
            : activeStep
            ? `step ${activeStep.step_number + 1} · ${activeStep.seeds.length} seeds → ${activeStep.traversal_nodes.length} reached`
            : ""}
        </span>
        <span>α·Rel(q,v) + β·w(e) + γ·Novelty(v)</span>
      </div>
    </div>
  );
}

function Legend({
  swatch,
  label,
  dash,
}: {
  swatch: string;
  label: string;
  dash: string;
}) {
  return (
    <span className="flex items-center gap-1.5">
      <svg width="20" height="6" className="block">
        <line
          x1="0"
          y1="3"
          x2="20"
          y2="3"
          stroke={swatch}
          strokeWidth={1.6}
          strokeDasharray={dash}
        />
      </svg>
      {label}
    </span>
  );
}
