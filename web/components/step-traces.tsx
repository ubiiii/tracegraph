"use client";

import type { StepTrace } from "@/lib/types";

interface Props {
  steps: StepTrace[];
  active: number;
  onSelect: (n: number) => void;
}

export function StepTraces({ steps, active, onSelect }: Props) {
  if (steps.length === 0) return null;

  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Callback Trace
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70">
          {steps.length} cycle{steps.length === 1 ? "" : "s"}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-ink-3/30">
        {steps.map((s) => {
          const isActive = active === s.step_number;
          const conclusive = !s.missing_evidence_decision.needs_callback;
          return (
            <button
              key={s.step_number}
              onClick={() => onSelect(s.step_number)}
              className={`text-left p-3.5 transition-colors ${
                isActive ? "bg-paper" : "bg-paper-2/60 hover:bg-paper"
              }`}
            >
              <div className="flex items-baseline justify-between gap-3 mb-1.5">
                <div className="flex items-baseline gap-2">
                  <span
                    className="font-display text-xl text-signal leading-none"
                    style={{ fontVariationSettings: "'opsz' 22, 'wght' 480" }}
                  >
                    §{String(s.step_number + 1).padStart(2, "0")}
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3">
                    {conclusive ? "final" : "draft · callback"}
                  </span>
                </div>
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] tabular text-ink-3">
                  {(s.latency_seconds * 1000).toFixed(0)}ms · ~{s.token_estimate}tk
                </span>
              </div>

              <div className="font-mono text-[11px] leading-snug text-ink-2 line-clamp-2 mb-2">
                {s.refined_query && s.refined_query !== s.query
                  ? s.refined_query
                  : s.query}
              </div>

              <div className="grid grid-cols-2 gap-2 mb-2">
                <Pill label="seeds" items={s.seeds} accent />
                <Pill label="reached" items={s.traversal_nodes} />
              </div>

              <div className="flex items-baseline justify-between gap-2 border-t border-rule pt-1.5 font-mono text-[10px]">
                <span className="text-ink-2">
                  draft <span className="italic text-ink">“{s.draft_answer}”</span>
                </span>
                <span
                  className={
                    s.missing_evidence_decision.needs_callback
                      ? "text-signal-2"
                      : "text-ink"
                  }
                >
                  {s.missing_evidence_decision.needs_callback
                    ? "refine ↺"
                    : "halt ✓"}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function Pill({ label, items, accent }: { label: string; items: string[]; accent?: boolean }) {
  return (
    <div className="min-w-0">
      <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-ink-3 mb-1">
        {label}
      </div>
      <div className="flex flex-wrap gap-1">
        {items.slice(0, 6).map((id) => (
          <span
            key={id}
            className={`font-mono text-[9px] uppercase tracking-[0.1em] px-1 py-0.5 border ${
              accent
                ? "border-signal text-signal"
                : "border-ink-3/50 text-ink-2"
            }`}
          >
            {id.split("::")[0]}
          </span>
        ))}
        {items.length > 6 && (
          <span className="font-mono text-[9px] text-ink-3">+{items.length - 6}</span>
        )}
      </div>
    </div>
  );
}
