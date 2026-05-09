import { NextResponse } from "next/server";
import { existsSync } from "node:fs";
import path from "node:path";
import { PYTHON_BIN, REPO_ROOT, pythonExists, runPython } from "@/lib/server/cli";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const checks: Record<string, unknown> = {
    repo_root: REPO_ROOT,
    python_bin: PYTHON_BIN,
    python_present: pythonExists(),
  };

  if (!checks.python_present) {
    return NextResponse.json({ ok: false, ...checks, hint: "run `python3 -m venv .venv && .venv/bin/pip install -e .` from repo root" }, { status: 503 });
  }

  // CLI sanity
  try {
    const { code, stdout } = await runPython({
      args: ["-c", "import tracegraph, sys; sys.stdout.write(tracegraph.__name__)"],
      timeoutMs: 10_000,
    });
    checks.tracegraph_importable = code === 0 && stdout.includes("tracegraph");
  } catch (e: unknown) {
    checks.tracegraph_importable = false;
    checks.import_error = (e as Error).message;
  }

  // Graph artifacts
  const ptr = path.join(REPO_ROOT, "data", "outputs", "runs", "latest_run.txt");
  checks.has_graph_artifacts = existsSync(ptr);

  const ok = Boolean(checks.python_present) && Boolean(checks.tracegraph_importable);
  return NextResponse.json({ ok, ...checks }, { status: ok ? 200 : 503 });
}
