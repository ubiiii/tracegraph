import { NextResponse } from "next/server";
import { dumpGraph } from "@/lib/server/cli";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const data = await dumpGraph();
    return NextResponse.json({ ok: true, ...data });
  } catch (e: unknown) {
    return NextResponse.json(
      { ok: false, error: (e as Error).message },
      { status: 500 }
    );
  }
}
