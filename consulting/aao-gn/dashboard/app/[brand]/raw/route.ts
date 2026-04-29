import { NextRequest, NextResponse } from "next/server";
import path from "node:path";
import fs from "node:fs/promises";
import { brandsRoots, isValidSlug, isValidTimestamp } from "@/lib/paths";

export const dynamic = "force-dynamic";

// raw_responses.json (배열)을 JSONL(줄 단위)로 변환해 다운로드 응답.
// 외부 감사/재분석을 위한 원본 데이터 공개용.
export async function GET(
  req: NextRequest,
  { params }: { params: { brand: string } },
) {
  const slug = params.brand;
  if (!isValidSlug(slug)) return new NextResponse("invalid brand", { status: 400 });

  const snapshot = req.nextUrl.searchParams.get("snapshot");
  if (snapshot && !isValidTimestamp(snapshot)) {
    return new NextResponse("invalid snapshot", { status: 400 });
  }

  const candidates = brandsRoots().flatMap((root) => {
    if (snapshot) {
      return [
        path.join(root, slug, "results", "history", snapshot, "raw_responses.json"),
      ];
    }
    return [path.join(root, slug, "results", "raw_responses.json")];
  });

  let raw: string | null = null;
  for (const p of candidates) {
    try {
      raw = await fs.readFile(p, "utf8");
      break;
    } catch {
      // try next
    }
  }
  if (raw === null) {
    return new NextResponse("raw_responses.json not found", { status: 404 });
  }

  let records: unknown[];
  try {
    const parsed = JSON.parse(raw);
    records = Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    return new NextResponse("malformed raw_responses.json", { status: 500 });
  }

  const jsonl = records.map((r) => JSON.stringify(r)).join("\n") + "\n";
  const filename = snapshot
    ? `${slug}_raw_${snapshot}.jsonl`
    : `${slug}_raw.jsonl`;
  return new NextResponse(jsonl, {
    status: 200,
    headers: {
      "Content-Type": "application/x-ndjson; charset=utf-8",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Cache-Control": "no-store",
    },
  });
}
