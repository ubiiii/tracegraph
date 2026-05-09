"use client";

import { metricsTable, variants } from "@/lib/mock";

const headers: { key: keyof (typeof metricsTable)[0]; label: string; suffix?: string; best?: "max" | "min" }[] = [
  { key: "em", label: "Exact Match", best: "max" },
  { key: "f1", label: "Token F1", best: "max" },
  { key: "evidence_coverage", label: "Evidence cov.", best: "max" },
  { key: "latency_ms", label: "Latency", suffix: "ms", best: "min" },
  { key: "callbacks_avg", label: "Callbacks·avg", best: "min" },
];

export function Bench() {
  const labelOf = (key: string) => variants.find((v) => v.key === key)?.label ?? key;

  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-5 py-2 bg-ink text-paper">
        <div className="font-mono text-[11px] uppercase tracking-[0.22em] flex items-center gap-3">
          <span className="inline-block w-2 h-2 rounded-full bg-signal" />
          Plate VI — Benchmark Ledger
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70">
          HotpotQA · demo slice · n=12
        </div>
      </div>

      <div className="overflow-x-auto scroll-thin">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-ink/90 bg-paper-2/50">
              <th className="px-5 py-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3">
                Variant
              </th>
              {headers.map((h) => (
                <th
                  key={h.key as string}
                  className="px-5 py-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3 tabular text-right"
                >
                  {h.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metricsTable.map((row) => {
              const isPrimary = row.variant === "bm25_graph";
              return (
                <tr
                  key={row.variant}
                  className={`border-b border-ink-3/30 ${
                    isPrimary ? "bg-signal/10" : ""
                  }`}
                >
                  <td className="px-5 py-3.5">
                    <div className="font-display text-lg" style={{ fontVariationSettings: "'opsz' 18, 'wght' 480" }}>
                      {labelOf(row.variant)}
                      {isPrimary && (
                        <span className="ml-2 font-mono text-[10px] uppercase tracking-[0.22em] text-signal">
                          ★ primary
                        </span>
                      )}
                    </div>
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-3">
                      {row.variant}
                    </div>
                  </td>
                  {headers.map((h) => {
                    const v = row[h.key] as number;
                    const isBest =
                      (h.best === "max" &&
                        v ===
                          Math.max(
                            ...metricsTable.map(
                              (r) => r[h.key] as number
                            )
                          )) ||
                      (h.best === "min" &&
                        v ===
                          Math.min(
                            ...metricsTable.map(
                              (r) => r[h.key] as number
                            )
                          ));
                    return (
                      <td
                        key={h.key as string}
                        className={`px-5 py-3.5 font-mono text-sm tabular text-right ${
                          isBest ? "text-signal" : "text-ink-2"
                        }`}
                      >
                        {h.key === "em" || h.key === "f1" || h.key === "evidence_coverage"
                          ? v.toFixed(2)
                          : h.key === "callbacks_avg"
                          ? v.toFixed(1)
                          : v.toFixed(0)}
                        {h.suffix && (
                          <span className="text-ink-3 text-[10px] ml-1 uppercase tracking-[0.18em]">
                            {h.suffix}
                          </span>
                        )}
                        {isBest && <span className="text-signal ml-1">◀</span>}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-ink/90 bg-paper-2/40 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-3 leading-relaxed">
        Reading — bm25_graph attains the same EM/F1 as the callback variant on
        the demo slice with lower latency, while callbacks lift evidence coverage
        an additional 5 pts. ◆
      </div>
    </section>
  );
}
