"use client";

export function Masthead() {
  return (
    <header className="border-b border-ink/90">
      <div className="mx-auto max-w-[1480px] px-6 pt-8 pb-5 flex items-end justify-between gap-6 flex-wrap">
        <h1
          className="font-display leading-[0.86] tracking-tight text-ink"
          style={{
            fontVariationSettings: "'opsz' 144, 'SOFT' 40, 'wght' 470",
            fontSize: "clamp(48px, 7vw, 96px)",
          }}
        >
          Trace
          <span
            className="italic"
            style={{
              fontVariationSettings:
                "'opsz' 144, 'SOFT' 100, 'wght' 380, 'slnt' -10",
            }}
          >
            Graph
          </span>
          <span
            className="text-signal align-top text-[0.28em] ml-2 font-mono not-italic"
            style={{ fontVariationSettings: "normal" }}
          >
            ◆
          </span>
        </h1>

        <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-3 leading-relaxed shrink-0 max-w-[44ch]">
          Graph-traversal retrieval for multi-hop questions whose evidence
          isn't in any single most-similar passage.
        </div>
      </div>
    </header>
  );
}
