"use client";

import { useState } from "react";
import { exampleQuestions, variants } from "@/lib/mock";

interface Props {
  onSubmit: (question: string, variantKey: string) => void;
  running: boolean;
  selectedVariant: string;
  onVariant: (k: string) => void;
}

export function Console({ onSubmit, running, selectedVariant, onVariant }: Props) {
  const [q, setQ] = useState(exampleQuestions[0]);

  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Console
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70">
          {running ? "running" : "idle"}
        </div>
      </div>

      {/* Question field */}
      <div className="field rounded-none border-0 border-b border-ink-3/30">
        <div className="flex items-start gap-3 px-4 py-3">
          <span className="font-mono text-signal mt-1 select-none">▸</span>
          <textarea
            value={q}
            onChange={(e) => setQ(e.target.value)}
            rows={2}
            placeholder="Ask a multi-hop question…"
            className="flex-1 bg-transparent resize-none outline-none font-display text-xl leading-snug placeholder:text-mute"
            style={{ fontVariationSettings: "'opsz' 22, 'SOFT' 20, 'wght' 420" }}
          />
        </div>
      </div>

      {/* Variant + run row */}
      <div className="px-4 py-2.5 flex items-center gap-3 flex-wrap">
        <div className="flex border border-ink-3/40">
          {variants.map((v) => {
            const active = v.key === selectedVariant;
            return (
              <button
                key={v.key}
                onClick={() => onVariant(v.key)}
                title={v.description}
                className={`font-mono text-[10px] uppercase tracking-[0.18em] px-2.5 py-1.5 border-r border-ink-3/40 last:border-r-0 transition-colors ${
                  active
                    ? "bg-ink text-paper"
                    : "bg-paper hover:bg-paper-2"
                }`}
              >
                {v.label}
              </button>
            );
          })}
        </div>

        <button
          disabled={running || !q.trim()}
          onClick={() => onSubmit(q.trim(), selectedVariant)}
          className="btn-ink rounded-none px-3.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.24em] flex items-center gap-2 ml-auto"
        >
          {running ? "tracing…" : "run trace"}
          <span className="text-signal">→</span>
        </button>
      </div>

      {/* Example chips */}
      <div className="border-t border-ink-3/30 px-4 py-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-3">
        <span>examples</span>
        {exampleQuestions.map((eq, i) => (
          <button
            key={i}
            onClick={() => setQ(eq)}
            className="hover:text-signal transition-colors"
          >
            {String(i + 1).padStart(2, "0")}. {eq.slice(0, 30)}…
          </button>
        ))}
      </div>
    </section>
  );
}
