import fs from "node:fs/promises";
import path from "node:path";
import { z } from "zod";
import { AuditMetadataSchema, SummarySchema } from "@/types";

export const SnapshotSchema = z.object({
  timestamp: z.string(),
  brand_name: z.string().optional().default(""),
  audit_metadata: AuditMetadataSchema.optional(),
  summary: SummarySchema.optional(),
});
export type Snapshot = z.infer<typeof SnapshotSchema>;

export async function loadHistory(brandDir: string): Promise<Snapshot[]> {
  const historyDir = path.join(brandDir, "..", "history");
  let entries: string[] = [];
  try {
    entries = await fs.readdir(historyDir);
  } catch {
    return [];
  }

  const snapshots: Snapshot[] = [];
  for (const entry of entries) {
    const snapPath = path.join(historyDir, entry, "snapshot.json");
    try {
      const raw = await fs.readFile(snapPath, "utf8");
      const parsed = SnapshotSchema.safeParse(JSON.parse(raw));
      if (parsed.success) snapshots.push(parsed.data);
    } catch {
      // skip malformed snapshots; new schema is incompatible with old snapshots
    }
  }
  return snapshots.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}

export interface KpiDelta {
  current: number;
  previous: number | null;
  delta: number | null;
  direction: "up" | "down" | "flat" | null;
}

export function computeDelta(current: number, previous: number | null): KpiDelta {
  if (previous === null || !Number.isFinite(previous)) {
    return { current, previous: null, delta: null, direction: null };
  }
  const delta = current - previous;
  const eps = 0.05;
  return {
    current,
    previous,
    delta,
    direction: Math.abs(delta) < eps ? "flat" : delta > 0 ? "up" : "down",
  };
}
