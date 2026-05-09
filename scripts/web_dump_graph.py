"""Print the latest persisted graph + chunks as JSON for the web frontend."""

from __future__ import annotations

import json
import math
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def latest_run_dir() -> Path:
    runs_dir = ROOT / "data" / "outputs" / "runs"
    # Prefer the freshly-updated pointer file, fall back to a globbed scan.
    for name in ("latest_run.txt", "latest"):
        ptr = runs_dir / name
        if ptr.exists():
            raw = ptr.read_text().strip()
            cand = (ROOT / raw) if not Path(raw).is_absolute() else Path(raw)
            if (cand / "artifacts" / "graph.pkl").exists():
                return cand
    # Fall back: pick the most recent build-graph run that actually has artifacts.
    candidates = sorted(
        [p for p in runs_dir.glob("*_demo_build_graph") if (p / "artifacts" / "graph.pkl").exists()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise SystemExit("no graph artifacts: run `tracegraph build-graph` first")
    return candidates[0]


def deterministic_layout(node_ids: list[str], width: int = 920, height: int = 500) -> dict[str, tuple[float, float]]:
    """Lay nodes out evenly around an ellipse — deterministic and dense."""
    n = len(node_ids)
    cx, cy = width / 2, height / 2
    rx, ry = width * 0.36, height * 0.34
    layout: dict[str, tuple[float, float]] = {}
    for i, nid in enumerate(sorted(node_ids)):
        theta = -math.pi / 2 + (2 * math.pi * i) / max(n, 1)
        layout[nid] = (cx + rx * math.cos(theta), cy + ry * math.sin(theta))
    return layout


def main() -> int:
    run = latest_run_dir()
    graph_path = run / "artifacts" / "graph.pkl"
    chunks_path = run / "artifacts" / "chunks.jsonl"
    docs_path = run / "artifacts" / "documents.jsonl"
    stats_path = run / "artifacts" / "graph_stats.json"

    with open(graph_path, "rb") as f:
        g = pickle.load(f)

    chunk_records = [json.loads(line) for line in chunks_path.read_text().splitlines() if line.strip()]
    doc_records = [json.loads(line) for line in docs_path.read_text().splitlines() if line.strip()]
    stats = json.loads(stats_path.read_text())

    node_ids = [str(n) for n in g.nodes()]
    pos = deterministic_layout(node_ids)

    nodes = []
    for nid in node_ids:
        attrs = dict(g.nodes[nid])
        x, y = pos[nid]
        nodes.append({
            "id": nid,
            "doc_id": attrs.get("doc_id"),
            "doc_title": attrs.get("title", attrs.get("doc_id", nid)),
            "position": attrs.get("chunk_id", 0),
            "x": x,
            "y": y,
            "summary": attrs.get("summary"),
            "entities": attrs.get("entities", []),
            "keywords": attrs.get("keywords", []),
        })

    edges = []
    seen: set[tuple[str, str, str]] = set()
    edge_iter = g.edges(data=True, keys=True) if g.is_multigraph() else g.edges(data=True)
    for tup in edge_iter:
        if g.is_multigraph():
            u, v, k, data = tup
        else:
            u, v, data = tup
        etype = str(data.get("edge_type", "RELATION"))
        # de-dup symmetric edges of the same type
        key_pair = tuple(sorted([str(u), str(v)]))
        key = (key_pair[0], key_pair[1], etype)
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "source": str(u),
            "target": str(v),
            "type": etype,
            "weight": float(data.get("weight", 0.5)),
        })

    chunks = [
        {
            "id": c.get("node_id"),
            "doc_id": c.get("doc_id"),
            "doc_title": c.get("title"),
            "position": c.get("chunk_id", 0),
            "text": c.get("text", ""),
            "entities": c.get("entities", []),
            "keywords": c.get("keywords", []),
        }
        for c in chunk_records
    ]

    documents = [
        {
            "id": d.get("doc_id"),
            "title": d.get("title", d.get("doc_id")),
            "source": d.get("source", d.get("doc_id", "")),
        }
        for d in doc_records
    ]

    payload = {
        "documents": documents,
        "chunks": chunks,
        "nodes": nodes,
        "edges": edges,
        "stats": stats,
        "run_dir": (
            str(run.relative_to(ROOT)) if run.is_absolute() and ROOT in run.parents
            else str(run)
        ),
    }

    sys.stdout.write(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
