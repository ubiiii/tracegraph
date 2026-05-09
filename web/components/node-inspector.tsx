"use client";

import type { Chunk, RunResult } from "@/lib/types";

interface Props {
  chunk: Chunk | null;
  result: RunResult | null;
  contextNodes: Set<string>;
  source: "live" | "mock";
  onClose: () => void;
}

export function NodeInspector({ chunk, result, contextNodes, source, onClose }: Props) {
  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Node Inspector
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70 flex items-center gap-1.5">
            <span
              className={`inline-block w-1.5 h-1.5 ${
                source === "live" ? "bg-signal" : "bg-mute"
              }`}
            />
            {source}
          </span>
          {chunk && (
            <button
              onClick={onClose}
              className="font-mono text-[10px] uppercase tracking-[0.22em] text-paper/70 hover:text-signal transition-colors"
            >
              ✕ close
            </button>
          )}
        </div>
      </div>

      {!chunk ? (
        <div className="p-5 font-mono text-[11px] uppercase tracking-[0.18em] text-ink-3">
          Click any node in Plate II — or any row in the corpus ledger — to load
          its chunk text, entities, keywords, and roles in the latest run.
        </div>
      ) : (
        <div className="p-5 space-y-4">
          {/* Title row */}
          <div className="flex items-baseline gap-3 flex-wrap">
            <span
              className="font-display text-2xl"
              style={{ fontVariationSettings: "'opsz' 24, 'wght' 480" }}
            >
              {chunk.doc_title}
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-3">
              {chunk.id} · chunk {chunk.position}
            </span>
            <RoleBadges chunk={chunk} result={result} contextNodes={contextNodes} />
          </div>

          {/* Body */}
          <p
            className="font-display text-base leading-relaxed text-ink-2"
            style={{ fontVariationSettings: "'opsz' 16, 'wght' 400" }}
          >
            {highlight(chunk.text)}
          </p>

          {/* Tag rails */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-ink-3/30">
            <TagRail
              label="entities"
              items={chunk.entities}
              accent="signal"
              empty="— none extracted —"
            />
            <TagRail
              label="keywords"
              items={chunk.keywords}
              accent="ink"
              empty="— none extracted —"
            />
          </div>

          {/* Run roles */}
          {result && (
            <RunRoles chunk={chunk} result={result} />
          )}
        </div>
      )}
    </section>
  );
}

function RoleBadges({
  chunk,
  result,
  contextNodes,
}: {
  chunk: Chunk;
  result: RunResult | null;
  contextNodes: Set<string>;
}) {
  const isContext = contextNodes.has(chunk.id);
  const lastSeeds = new Set(result?.step_traces.at(-1)?.seeds ?? []);
  const lastReached = new Set(result?.step_traces.at(-1)?.traversal_nodes ?? []);
  return (
    <div className="ml-auto flex flex-wrap gap-1.5 font-mono text-[9px] uppercase tracking-[0.2em]">
      {isContext && <Badge color="ink">in context</Badge>}
      {lastSeeds.has(chunk.id) && <Badge color="signal">seed</Badge>}
      {lastReached.has(chunk.id) && <Badge color="ink-3">reached</Badge>}
      {!isContext && !lastSeeds.has(chunk.id) && !lastReached.has(chunk.id) && (
        <Badge color="ink-3">candidate</Badge>
      )}
    </div>
  );
}

function Badge({
  children,
  color,
}: {
  children: React.ReactNode;
  color: "ink" | "signal" | "ink-3";
}) {
  const cls =
    color === "ink"
      ? "bg-ink text-paper"
      : color === "signal"
      ? "bg-signal text-paper"
      : "border border-ink-3/50 text-ink-2";
  return <span className={`px-1.5 py-0.5 ${cls}`}>{children}</span>;
}

function TagRail({
  label,
  items,
  accent,
  empty,
}: {
  label: string;
  items: string[];
  accent: "signal" | "ink";
  empty: string;
}) {
  return (
    <div>
      <div className="font-mono text-[9px] uppercase tracking-[0.22em] text-ink-3 mb-1.5">
        {label}
      </div>
      {items.length === 0 ? (
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-mute">
          {empty}
        </div>
      ) : (
        <div className="flex flex-wrap gap-1">
          {items.map((it) => (
            <span
              key={it}
              className={`font-mono text-[10px] px-1.5 py-0.5 border ${
                accent === "signal"
                  ? "border-signal/70 text-signal-2"
                  : "border-ink-3/50 text-ink-2"
              }`}
            >
              ·{it}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function RunRoles({ chunk, result }: { chunk: Chunk; result: RunResult }) {
  const roles = result.step_traces.map((s) => {
    const seeded = s.seeds.includes(chunk.id);
    const reached = s.traversal_nodes.includes(chunk.id);
    return { step: s.step_number, seeded, reached };
  });
  return (
    <div className="pt-2 border-t border-ink-3/30">
      <div className="font-mono text-[9px] uppercase tracking-[0.22em] text-ink-3 mb-1.5">
        role per cycle
      </div>
      <div className="flex flex-wrap gap-1.5 font-mono text-[10px]">
        {roles.map((r) => (
          <span
            key={r.step}
            className="flex items-center gap-1.5 px-1.5 py-0.5 border border-ink-3/40"
          >
            <span className="text-ink-3">§{String(r.step + 1).padStart(2, "0")}</span>
            <span className={r.seeded ? "text-signal" : "text-ink-3/60"}>
              seed
            </span>
            <span className={r.reached ? "text-ink" : "text-ink-3/60"}>
              reach
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

function highlight(text: string) {
  const terms = ["C-12", "RP-17", "24 months", "Compliance", "clause", "RP-17", "E-9"];
  const re = new RegExp(`(${terms.join("|")})`, "gi");
  const parts = text.split(re);
  return parts.map((p, i) =>
    re.test(p) ? (
      <mark
        key={i}
        className="bg-transparent border-b border-signal text-ink px-0"
      >
        {p}
      </mark>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}
