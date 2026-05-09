"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Masthead } from "@/components/masthead";
import { Console } from "@/components/console";
import { GraphCanvas } from "@/components/graph-canvas";
import { AnswerPanel } from "@/components/answer-panel";
import { StepTraces } from "@/components/step-traces";
import { Corpus } from "@/components/corpus";
import { Bench } from "@/components/bench";
import { NodeInspector } from "@/components/node-inspector";
import {
  chunks as mockChunks,
  documents as mockDocuments,
  graphEdges as mockEdges,
  graphNodes as mockNodes,
  demoRun,
} from "@/lib/mock";
import type {
  Chunk,
  Document,
  GraphEdge,
  GraphNode,
  RunResult,
  StepTrace,
} from "@/lib/types";

type Phase =
  | "idle"
  | "seeding"
  | "traversing"
  | "drafting"
  | "detecting"
  | "refining"
  | "callback"
  | "finalizing"
  | "done";

interface BackendStatus {
  source: "live" | "mock";
  message: string;
  ok: boolean;
}

export default function Page() {
  const [result, setResult] = useState<RunResult | null>(null);
  const [activeStepIdx, setActiveStepIdx] = useState<number>(0);
  const [phase, setPhase] = useState<Phase>("idle");
  const [running, setRunning] = useState(false);
  const [variantKey, setVariantKey] = useState("bm25_graph_callbacks");
  const [hoverNode, setHoverNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [typing, setTyping] = useState(false);

  // Backend-hydrated state
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>(mockNodes);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>(mockEdges);
  const [docs, setDocs] = useState<Document[]>(mockDocuments);
  const [chunks, setChunks] = useState<Chunk[]>(mockChunks);
  const [status, setStatus] = useState<BackendStatus>({
    source: "mock",
    ok: false,
    message: "probing backend…",
  });

  const timeoutsRef = useRef<number[]>([]);
  const clearTimers = () => {
    timeoutsRef.current.forEach((id) => clearTimeout(id));
    timeoutsRef.current = [];
  };
  useEffect(() => clearTimers, []);

  // Esc deselects pinned node
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelectedNode(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Hydrate graph from /api/graph on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/graph", { cache: "no-store" });
        const data = await res.json();
        if (cancelled) return;
        if (res.ok && data.ok) {
          setGraphNodes(data.nodes);
          setGraphEdges(data.edges);
          setDocs(data.documents);
          setChunks(data.chunks);
          setStatus({
            source: "live",
            ok: true,
            message: `live · ${data.run_dir}`,
          });
        } else {
          setStatus({
            source: "mock",
            ok: false,
            message: data.error ?? "graph endpoint unavailable",
          });
        }
      } catch (e) {
        if (cancelled) return;
        setStatus({
          source: "mock",
          ok: false,
          message: (e as Error).message,
        });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Stage the visual pipeline against a real or mock RunResult.
  const stageRun = (full: RunResult) => {
    clearTimers();
    setResult(null);
    setActiveStepIdx(0);
    setTyping(false);

    const schedule = (delay: number, fn: () => void) => {
      const id = window.setTimeout(fn, delay);
      timeoutsRef.current.push(id);
    };

    let t = 0;
    const partials: StepTrace[] = [];

    full.step_traces.forEach((step, idx) => {
      // 1) seeding — show seeds, no traversal yet
      const seeding: RunResult = {
        ...full,
        step_traces: [...partials, { ...step, traversal_nodes: [] }],
      };
      schedule(t, () => {
        setPhase("seeding");
        setResult(seeding);
        setActiveStepIdx(idx);
      });
      t += 850;

      // 2) traversing
      const reaching: RunResult = {
        ...full,
        step_traces: [...partials, step],
      };
      schedule(t, () => {
        setPhase("traversing");
        setResult(reaching);
      });
      t += 1100;

      // 3) drafting
      schedule(t, () => setPhase("drafting"));
      t += 700;

      // 4) detect
      schedule(t, () => setPhase("detecting"));
      t += 600;

      partials.push(step);

      if (step.missing_evidence_decision.needs_callback) {
        schedule(t, () => setPhase("refining"));
        t += 700;
        schedule(t, () => setPhase("callback"));
        t += 500;
      }
    });

    // finalize
    schedule(t, () => {
      setPhase("finalizing");
      setResult(full);
      setActiveStepIdx(full.step_traces.length - 1);
    });
    t += 600;
    schedule(t, () => {
      setPhase("done");
      setRunning(false);
      setTyping(true);
    });
    schedule(t + 1200, () => setTyping(false));
  };

  const runTrace = async (question: string, variant: string) => {
    setRunning(true);

    // Try live backend first
    try {
      const res = await fetch("/api/answer", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question, variant }),
      });
      const data = await res.json();
      if (res.ok && data.ok && data.run) {
        setStatus((prev) => ({ ...prev, source: "live", ok: true }));
        stageRun(data.run as RunResult);
        return;
      }
      setStatus({
        source: "mock",
        ok: false,
        message: data.error ?? `HTTP ${res.status}`,
      });
    } catch (e) {
      setStatus({
        source: "mock",
        ok: false,
        message: (e as Error).message,
      });
    }

    // Fallback to mock so the demo still plays without a backend
    const fallback: RunResult = {
      ...demoRun,
      question,
      answer: { ...demoRun.answer, question },
    };
    stageRun(fallback);
  };

  const activeStep: StepTrace | null = useMemo(() => {
    if (!result || result.step_traces.length === 0) return null;
    const idx = Math.min(activeStepIdx, result.step_traces.length - 1);
    return result.step_traces[idx];
  }, [result, activeStepIdx]);

  const contextNodes = useMemo(
    () => new Set(result?.answer.metadata.context_nodes ?? []),
    [result]
  );

  return (
    <main className="min-h-screen pb-24">
      <Masthead />

      <div className="mx-auto max-w-[1480px] px-6 mt-2">
        <PhaseStrip phase={phase} variantKey={variantKey} status={status} />
      </div>

      <div className="mx-auto max-w-[1480px] px-6 mt-6 grid grid-cols-1 gap-6">
        <Console
          onSubmit={runTrace}
          running={running}
          selectedVariant={variantKey}
          onVariant={setVariantKey}
        />

        <div className="grid grid-cols-1 xl:grid-cols-[1.4fr_1fr] gap-6">
          <GraphCanvas
            nodes={graphNodes}
            edges={graphEdges}
            activeStep={activeStep}
            contextNodes={contextNodes}
            phase={phase}
            hoverNode={hoverNode}
            onHover={setHoverNode}
            selectedNode={selectedNode}
            onSelect={setSelectedNode}
            source={status.source}
          />
          <div className="grid grid-cols-1 gap-6">
            <AnswerPanel result={phase === "done" ? result : null} typing={typing} />
            <NodeInspector
              chunk={chunks.find((c) => c.id === selectedNode) ?? null}
              result={result}
              contextNodes={contextNodes}
              source={status.source}
              onClose={() => setSelectedNode(null)}
            />
          </div>
        </div>

        <StepTraces
          steps={result?.step_traces ?? []}
          active={activeStepIdx}
          onSelect={setActiveStepIdx}
        />

        <div className="grid grid-cols-1 xl:grid-cols-[1.6fr_1fr] gap-6">
          <Corpus
            documents={docs}
            chunks={chunks}
            contextNodes={contextNodes}
            hoverNode={hoverNode}
            onHover={setHoverNode}
            selectedNode={selectedNode}
            onSelect={setSelectedNode}
          />
          <Bench />
        </div>

        <Colophon />
      </div>
    </main>
  );
}

function PhaseStrip({
  phase,
  variantKey,
  status,
}: {
  phase: Phase;
  variantKey: string;
  status: BackendStatus;
}) {
  const phases: { key: Phase; label: string }[] = [
    { key: "idle", label: "idle" },
    { key: "seeding", label: "seed retrieval" },
    { key: "traversing", label: "graph traversal" },
    { key: "drafting", label: "context · draft" },
    { key: "detecting", label: "missing-evidence detect" },
    { key: "refining", label: "query refine" },
    { key: "callback", label: "callback ↺" },
    { key: "finalizing", label: "synthesize · cite" },
    { key: "done", label: "done" },
  ];
  const idx = phases.findIndex((p) => p.key === phase);

  return (
    <div className="flex items-center gap-3 flex-wrap font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3">
      <span className="text-ink-2">stage</span>
      {phases.map((p, i) => {
        const isActive = i === idx;
        const isPast = i < idx;
        return (
          <span
            key={p.key}
            className={`flex items-center gap-2 ${
              isActive ? "text-signal" : isPast ? "text-ink-2" : "text-ink-3/60"
            }`}
          >
            <span
              className={`inline-block w-1.5 h-1.5 ${
                isActive
                  ? "bg-signal animate-pulse"
                  : isPast
                  ? "bg-ink"
                  : "bg-ink-3/40"
              }`}
            />
            {p.label}
            {i < phases.length - 1 && <span className="text-ink-3/40">·</span>}
          </span>
        );
      })}
      <span className="ml-auto flex items-center gap-2">
        <span
          className={`inline-block w-1.5 h-1.5 ${
            status.source === "live" ? "bg-signal" : "bg-mute"
          }`}
        />
        <span
          className={status.source === "live" ? "text-signal" : "text-mute"}
        >
          backend {status.source}
        </span>
        <span className="text-ink-3">· variant</span>
        <span className="text-ink">{variantKey}</span>
      </span>
    </div>
  );
}

function Colophon() {
  return (
    <footer className="mt-6 border-t border-ink-3/30 pt-3 pb-1 flex items-center gap-4 flex-wrap font-mono text-[10px] uppercase tracking-[0.18em] text-ink-3">
      <span>tracegraph</span>
      <span className="text-ink-3/40">·</span>
      <span>GET <span className="text-signal">/api/graph</span></span>
      <span>POST <span className="text-signal">/api/answer</span></span>
      <span className="ml-auto">team 8 · cecs-551</span>
    </footer>
  );
}
