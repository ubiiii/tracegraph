import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, unlinkSync } from "node:fs";
import path from "node:path";
import os from "node:os";

// Resolve TraceGraph repo root: web/ is one level inside it.
export const REPO_ROOT = path.resolve(process.cwd(), "..");

export const PYTHON_BIN =
  process.env.TRACEGRAPH_PYTHON ||
  path.join(REPO_ROOT, ".venv", "bin", "python");

export interface RunOptions {
  args: string[];
  cwd?: string;
  timeoutMs?: number;
}

export interface RunOutput {
  stdout: string;
  stderr: string;
  code: number | null;
}

export function pythonExists(): boolean {
  return existsSync(PYTHON_BIN);
}

export function runPython({
  args,
  cwd = REPO_ROOT,
  timeoutMs = 60_000,
}: RunOptions): Promise<RunOutput> {
  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON_BIN, args, {
      cwd,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
    });

    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      reject(new Error(`python timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    child.stdout.on("data", (b) => (stdout += b.toString()));
    child.stderr.on("data", (b) => (stderr += b.toString()));
    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ stdout, stderr, code });
    });
  });
}

const VARIANT_CONFIG: Record<string, string> = {
  bm25_only: "configs/retrieval/bm25_only.yaml",
  embedding_graph: "configs/retrieval/embedding_graph.yaml",
  bm25_graph: "configs/retrieval/bm25_graph.yaml",
  bm25_graph_callbacks: "configs/retrieval/bm25_graph_callbacks.yaml",
};

export function configForVariant(key: string): string {
  return VARIANT_CONFIG[key] ?? VARIANT_CONFIG.bm25_graph_callbacks;
}

export async function runAnswer(question: string, variant: string) {
  const cfg = configForVariant(variant);
  const tmpDir = mkdtempSync(path.join(os.tmpdir(), "tg-"));
  const outPath = path.join(tmpDir, "answer.json");

  const { code, stderr } = await runPython({
    args: [
      "-m",
      "tracegraph.cli",
      "answer",
      "--question",
      question,
      "--config",
      cfg,
      "--llm-mode",
      "mock",
      "--output-path",
      outPath,
    ],
    timeoutMs: 90_000,
  });

  if (code !== 0 || !existsSync(outPath)) {
    throw new Error(`tracegraph answer failed (code=${code}): ${stderr.slice(-400)}`);
  }
  const json = JSON.parse(readFileSync(outPath, "utf8"));
  try { unlinkSync(outPath); } catch {}
  return json;
}

export async function dumpGraph() {
  const { stdout, stderr, code } = await runPython({
    args: [path.join(REPO_ROOT, "scripts", "web_dump_graph.py")],
    timeoutMs: 30_000,
  });
  if (code !== 0) {
    throw new Error(`graph dump failed (code=${code}): ${stderr.slice(-400)}`);
  }
  return JSON.parse(stdout);
}
