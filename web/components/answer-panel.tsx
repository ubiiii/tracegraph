"use client";

import type { RunResult } from "@/lib/types";

interface Props {
  result: RunResult | null;
  typing: boolean;
}

export function AnswerPanel({ result, typing }: Props) {
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
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3 mb-1.5">
                Path
              </div>
              <div className="space-y-1 font-mono text-[11px] leading-snug text-ink-2">
                {result.answer.retrieval_path_explanation
                  .split("\n")
                  .filter(Boolean)
                  .slice(0, 3)
                  .map((line, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-signal select-none">→</span>
                      <span className="truncate">{line}</span>
                    </div>
                  ))}
              </div>
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
