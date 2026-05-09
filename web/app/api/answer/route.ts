import { NextResponse } from "next/server";
import { runAnswer } from "@/lib/server/cli";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

interface Body {
  question?: string;
  variant?: string;
}

export async function POST(req: Request) {
  let body: Body;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { ok: false, error: "invalid JSON body" },
      { status: 400 }
    );
  }
  const question = (body.question ?? "").trim();
  const variant = (body.variant ?? "bm25_graph_callbacks").trim();
  if (!question) {
    return NextResponse.json({ ok: false, error: "question required" }, { status: 400 });
  }

  try {
    const data = await runAnswer(question, variant);
    return NextResponse.json({ ok: true, run: data, variant });
  } catch (e: unknown) {
    return NextResponse.json(
      { ok: false, error: (e as Error).message },
      { status: 500 }
    );
  }
}
