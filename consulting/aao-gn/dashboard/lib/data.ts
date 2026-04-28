import path from "node:path";
import fs from "node:fs/promises";
import { readCsv, readJson } from "./csv";
import { brandDir, brandSnapshotDir, fileMtime } from "./paths";
import { z } from "zod";
import {
  AuditMetadataSchema,
  ByPromptSchema,
  CategoryCardSchema,
  CompOnlyByCompetitorSchema,
  H2HByCompetitorSchema,
  NeutralBrandRankingSchema,
  ParsedRunSchema,
  RawResponseSchema,
  SummarySchema,
  type AuditMetadata,
  type ByPrompt,
  type CategoryCard,
  type CompOnlyByCompetitor,
  type H2HByCompetitor,
  type NeutralBrandRanking,
  type ParsedRun,
  type RawResponse,
  type Summary,
} from "@/types";

export interface BrandData {
  brand: string;
  dir: string;
  mtime: number;
  categoryCards: CategoryCard[];
  h2hByCompetitor: H2HByCompetitor[];
  compOnlyByCompetitor: CompOnlyByCompetitor[];
  byPrompt: ByPrompt[];
  summary: Summary | null;
  auditMetadata: AuditMetadata | null;
  neutralBrandRanking: NeutralBrandRanking | null;
  snapshotTimestamp: string | null;
}

async function loadAuditMetadata(dashboardDir: string): Promise<AuditMetadata | null> {
  const candidates = [
    path.join(dashboardDir, "..", "audit_metadata.json"),
    path.join(dashboardDir, "audit_metadata.json"),
  ];
  for (const p of candidates) {
    try {
      const raw = await fs.readFile(p, "utf8");
      const parsed = AuditMetadataSchema.safeParse(JSON.parse(raw));
      if (parsed.success) return parsed.data;
    } catch {
      // try next candidate
    }
  }
  return null;
}

export async function loadBrandData(
  brand: string,
  snapshotTimestamp: string | null = null,
): Promise<BrandData | null> {
  const dir = snapshotTimestamp
    ? await brandSnapshotDir(brand, snapshotTimestamp)
    : await brandDir(brand);
  if (!dir) return null;

  const categoryCardsPath = path.join(dir, "category_cards.csv");
  const h2hPath = path.join(dir, "h2h_by_competitor.csv");
  const compOnlyPath = path.join(dir, "comp_only_by_competitor.csv");
  const byPromptPath = path.join(dir, "by_prompt.csv");
  const summaryPath = path.join(dir, "summary.json");
  const neutralBrandRankingPath = path.join(dir, "neutral_brand_ranking.json");

  const [
    categoryCards,
    h2hByCompetitor,
    compOnlyByCompetitor,
    byPrompt,
    summary,
    mtimeRaw,
    auditMetadata,
    neutralBrandRanking,
  ] = await Promise.all([
    readCsv(categoryCardsPath, CategoryCardSchema),
    readCsv(h2hPath, H2HByCompetitorSchema),
    readCsv(compOnlyPath, CompOnlyByCompetitorSchema),
    readCsv(byPromptPath, ByPromptSchema),
    readJson(summaryPath, SummarySchema),
    fileMtime(summaryPath),
    loadAuditMetadata(dir).then(async (fromFile) => {
      if (fromFile) return fromFile;
      // fallback — summary.json 안에 embed된 audit_metadata
      try {
        const raw = await fs.readFile(summaryPath, "utf8");
        const parsed = SummarySchema.safeParse(JSON.parse(raw));
        return parsed.success ? parsed.data.audit_metadata ?? null : null;
      } catch {
        return null;
      }
    }),
    readJson(neutralBrandRankingPath, NeutralBrandRankingSchema),
  ]);

  let mtime = mtimeRaw;
  const auditEnd = auditMetadata?.audit_end;
  if (auditEnd) {
    const parsed = Date.parse(auditEnd);
    if (Number.isFinite(parsed) && parsed > 0) mtime = parsed;
  }

  let effectiveMtime = mtime;
  if (snapshotTimestamp) {
    const y = Number(snapshotTimestamp.slice(0, 4));
    const mo = Number(snapshotTimestamp.slice(4, 6)) - 1;
    const d = Number(snapshotTimestamp.slice(6, 8));
    const h = Number(snapshotTimestamp.slice(9, 11));
    const mi = Number(snapshotTimestamp.slice(11, 13));
    const s = Number(snapshotTimestamp.slice(13, 15));
    const parsed = new Date(y, mo, d, h, mi, s).getTime();
    if (Number.isFinite(parsed) && parsed > 0) effectiveMtime = parsed;
  }

  return {
    brand,
    dir,
    mtime: effectiveMtime,
    categoryCards: categoryCards ?? [],
    h2hByCompetitor: h2hByCompetitor ?? [],
    compOnlyByCompetitor: compOnlyByCompetitor ?? [],
    byPrompt: byPrompt ?? [],
    summary,
    auditMetadata,
    neutralBrandRanking,
    snapshotTimestamp,
  };
}

export interface PromptRunRow {
  run_number: number;
  parsed: ParsedRun | null;
  raw: RawResponse | null;
}

// 한 prompt에 대한 모든 run의 분류 결과 + 원본 응답을 조인.
// 수동 검증·spot check 용도.
export async function loadPromptRuns(
  brand: string,
  promptId: string,
  snapshotTimestamp: string | null = null,
): Promise<PromptRunRow[] | null> {
  const dir = snapshotTimestamp
    ? await brandSnapshotDir(brand, snapshotTimestamp)
    : await brandDir(brand);
  if (!dir) return null;

  // brand results 디렉토리 = dashboard 디렉토리의 부모
  const resultsDir = path.join(dir, "..");
  const parsedPath = path.join(resultsDir, "parsed_results.csv");
  const rawPath = path.join(resultsDir, "raw_responses.json");

  const parsedAll = (await readCsv(parsedPath, ParsedRunSchema)) ?? [];
  const parsed = parsedAll.filter((r) => r.prompt_id === promptId);

  let rawAll: RawResponse[] = [];
  try {
    const text = await fs.readFile(rawPath, "utf8");
    const arr = JSON.parse(text);
    if (Array.isArray(arr)) {
      rawAll = arr
        .map((x) => RawResponseSchema.safeParse(x))
        .filter((r): r is z.SafeParseSuccess<RawResponse> => r.success)
        .map((r) => r.data);
    }
  } catch {
    // raw 없으면 parsed만으로 진행
  }
  const raw = rawAll.filter((r) => r.prompt_id === promptId);

  // run_number 기준 outer join
  const runs = new Set<number>();
  parsed.forEach((p) => runs.add(p.run_number));
  raw.forEach((r) => runs.add(r.run_number));

  return Array.from(runs)
    .sort((a, b) => a - b)
    .map((n) => ({
      run_number: n,
      parsed: parsed.find((p) => p.run_number === n) ?? null,
      raw: raw.find((r) => r.run_number === n) ?? null,
    }));
}
