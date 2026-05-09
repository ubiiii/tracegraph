"use client";

import type { StepTrace } from "@/lib/types";

interface Props {
  steps: StepTrace[];
  active: number;
}

const phases = [
  { key: "seed",     label: "seed",     w: 0.18 },
  { key: "traverse", label: "traverse", w: 0.30 },
  { key: "draft",    label: "draft",    w: 0.22 },
  { key: "detect",   label: "detect",   w: 0.10 },
  { key: "refine",   label: "refine",   w: 0.10 },
  { key: "finalize", label: "finalize", w: 0.10 },
];

export function Timeline({ steps, active }: Props) {
  if (steps.length === 0) {
    return (
      <div className="border border-ink/90 bg-paper px-5 py-3 flex items-center gap-3">
        <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-3">
          Timeline ⏵
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-mute">
          idle — awaiting trace
        </span>
      </div>
    );
  }

  const totalLatency = steps.reduce((s, x) => s + x.latency_seconds, 0);

  return (
    <div className="border border-ink/90 bg-paper">
      <div className="flex items-center gap-4 border-b border-ink-3/30 px-5 py-2">
        <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-3">
          Timeline
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-2 ml-auto tabular">
          Σ {(totalLatency * 1000).toFixed(0)}ms · {steps.length} cycle{steps.length === 1 ? "" : "s"}
        </span>
      </div>

      <div className="px-5 py-4 space-y-3">
        {steps.map((s) => {
          const pct = s.latency_seconds / totalLatency;
          return (
            <div key={s.step_number} className="grid grid-cols-[60px_1fr_80px] gap-3 items-center">
              <div className="font-mono text-[11px] uppercase tracking-[0.18em]">
                <span className="text-signal">§{String(s.step_number + 1).padStart(2, "0")}</span>
              </div>
              <div className="flex h-3 border border-ink overflow-hidden">
                {phases.map((p, i) => (
                  <div
                    key={p.key}
                    className={`h-full border-r last:border-r-0 border-ink-3/40 ${
                      active === s.step_number
                        ? i % 2 === 0
                          ? "bg-ink"
                          : "bg-signal"
                        : i % 2 === 0
                        ? "bg-ink-3/60"
                        : "bg-paper-3"
                    }`}
                    style={{ width: `${p.w * 100}%` }}
                    title={p.label}
                  />
                ))}
              </div>
              <div className="font-mono text-[11px] tabular text-right text-ink-2">
                {(pct * 100).toFixed(0)}%
              </div>
            </div>
          );
        })}
        <div className="flex justify-between font-mono text-[9px] uppercase tracking-[0.22em] text-ink-3 mt-1 pl-[60px] pr-[80px]">
          {phases.map((p) => (
            <span key={p.key}>{p.label}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
