"use client";

import type { Chunk, Document } from "@/lib/types";

interface Props {
  documents: Document[];
  chunks: Chunk[];
  contextNodes: Set<string>;
  hoverNode: string | null;
  onHover: (id: string | null) => void;
  selectedNode: string | null;
  onSelect: (id: string | null) => void;
}

export function Corpus({
  documents,
  chunks,
  contextNodes,
  hoverNode,
  onHover,
  selectedNode,
  onSelect,
}: Props) {
  return (
    <section className="border border-ink/90 bg-paper">
      <div className="flex items-center justify-between border-b border-ink/90 px-4 py-1.5 bg-ink text-paper">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-signal" />
          Corpus Ledger
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-70">
          {documents.length} docs · {chunks.length} chunks
        </div>
      </div>

      <ol className="divide-y divide-ink-3/20">
        {chunks.map((c, i) => {
          const inContext = contextNodes.has(c.id);
          const isHover = hoverNode === c.id;
          const isSelected = selectedNode === c.id;
          return (
            <li
              key={c.id}
              onMouseEnter={() => onHover(c.id)}
              onMouseLeave={() => onHover(null)}
              onClick={() => onSelect(isSelected ? null : c.id)}
              className={`px-4 py-2.5 grid grid-cols-[28px_1fr_auto] items-baseline gap-3 transition-colors cursor-pointer ${
                isSelected
                  ? "bg-ink/10 border-l-2 border-signal"
                  : isHover
                  ? "bg-paper-3/50"
                  : inContext
                  ? "bg-paper-2/40"
                  : "bg-paper hover:bg-paper-2/40"
              }`}
            >
              <span
                className="font-mono text-[10px] tabular text-signal"
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="min-w-0">
                <div className="flex items-baseline gap-2">
                  <span
                    className="font-display text-base leading-tight"
                    style={{ fontVariationSettings: "'opsz' 16, 'wght' 480" }}
                  >
                    {c.doc_title}
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-3">
                    {c.id}
                  </span>
                </div>
                <p className="font-display text-[13px] leading-snug text-ink-2 mt-0.5 line-clamp-2"
                  style={{ fontVariationSettings: "'opsz' 14, 'wght' 380" }}>
                  {c.text}
                </p>
              </div>
              {inContext && (
                <span className="font-mono text-[9px] uppercase tracking-[0.2em] px-1.5 py-0.5 bg-ink text-paper">
                  ctx
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
