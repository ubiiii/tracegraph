"use client";

import { useEffect, useMemo, useState } from "react";
import type { RunResult } from "@/lib/types";

interface Props {
  result: RunResult | null;
  typing: boolean;
}

export function AnswerPanel({ result, typing }: Props) {
  const pathLines = useMemo(() => {
    if (!result?.answer.retrieval_path_explanation) return [];
    return result.answer.retrieval_path_explanation
      .split("\n")
      .filter(Boolean)
      .slice(0, 3);
  }, [result?.answer.retrieval_path_explanation]);

  const hopOptions = result?.answer.retrieval_path_hops ?? [];
  const [selectedPathIdx, setSelectedPathIdx] = useState(0);

  useEffect(() => {
    setSelectedPathIdx(0);
  }, [result?.question]);

  const selectedHops =
    hopOptions.length > 0
      ? hopOptions[Math.min(selectedPathIdx, hopOptions.length - 1)] ?? []
      : [];
  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Answer
        </div>
        {result && (
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70 flex gap-3">
            <span>conf {result.answer.confidence.toFixed(2)}</span>
            <span>cb {result.callback_count}</span>
            <span className="tabular">{(result.overall_latency * 1000).toFixed(0)}ms</span>
          </div>
        )}
      </div>

      <div className="p-5">
        {!result ? (
          <div
            className="font-display italic text-ink-3 text-lg leading-snug"
            style={{
              fontVariationSettings:
                "'opsz' 18, 'SOFT' 100, 'wght' 380, 'slnt' -10",
            }}
          >
            Awaiting interrogation.
          </div>
        ) : (
          <>
            <p
              className={`font-display text-ink leading-[1.18] ${typing ? "typeon" : ""}`}
              style={{
                fontVariationSettings: "'opsz' 64, 'SOFT' 40, 'wght' 420",
                fontSize: "clamp(22px, 2.4vw, 34px)",
              }}
            >
              <span className="text-signal italic mr-1">“</span>
              {result.answer.answer_text}
              <span className="text-signal italic ml-0.5">”</span>
            </p>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3 items-start">
              <p className="font-mono text-[11px] leading-relaxed text-ink-2">
                {renderCited(result.answer.cited_answer_text)}
              </p>
            </div>

            <div className="mt-4 border-t border-rule pt-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3 mb-1.5 flex flex-wrap items-center gap-2">
                <span>Path</span>
                {hopOptions.length > 1 ? (
                  <select
                    aria-label="Select retrieval path"
                    className="ml-auto max-w-[min(100%,240px)] border border-ink/60 bg-paper px-2 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-ink"
                    value={selectedPathIdx}
                    onChange={(e) => setSelectedPathIdx(Number(e.target.value))}
                  >
                    {hopOptions.map((_, i) => (
                      <option key={i} value={i}>
                        Path {i + 1}
                      </option>
                    ))}
                  </select>
                ) : null}
              </div>
              {hopOptions.length > 0 ? (
                <>
                  {pathLines[selectedPathIdx] ? (
                    <div className="mb-2 flex gap-2 font-mono text-[11px] leading-snug text-ink-2">
                      <span className="text-signal select-none">→</span>
                      <span>{pathLines[selectedPathIdx]}</span>
                    </div>
                  ) : null}
                  <ol className="list-decimal list-inside space-y-1.5 pl-1 font-mono text-[10px] leading-relaxed text-ink-2 marker:text-ink-3">
                    {selectedHops.map((hop, hi) => (
                      <li key={hi} className="break-words">
                        {hop}
                      </li>
                    ))}
                  </ol>
                </>
              ) : (
                <div className="space-y-1 font-mono text-[11px] leading-snug text-ink-2">
                  {pathLines.map((line, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-signal select-none">→</span>
                      <span className="truncate">{line}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function renderCited(text: string) {
  const parts = text.split(/(\[Source:[^\]]*\])/g);
  return parts.map((p, i) =>
    p.startsWith("[Source:") ? (
      <span key={i} className="text-signal-2"> {p} </span>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}
