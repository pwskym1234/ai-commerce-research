import path from "node:path";
import fs from "node:fs/promises";

const SLUG_RE = /^[a-z0-9_-]+$/i;

export function isValidSlug(slug: string): boolean {
  return SLUG_RE.test(slug) && slug.length > 0 && slug.length < 64;
}

export function brandsRoots(): string[] {
  const cwd = process.cwd();
  const roots = [
    process.env.GEO_BRANDS_DIR,
    path.join(cwd, "brands"),
    path.join(cwd, "..", "brands"),
  ].filter((p): p is string => Boolean(p));
  return Array.from(new Set(roots));
}

export async function brandDir(slug: string): Promise<string | null> {
  if (!isValidSlug(slug)) return null;
  for (const root of brandsRoots()) {
    const candidate = path.join(root, slug, "results", "dashboard");
    try {
      const stat = await fs.stat(candidate);
      if (stat.isDirectory()) return candidate;
    } catch {
      // continue
    }
  }
  return null;
}

const TS_RE = /^\d{8}-\d{6}$/;

export function isValidTimestamp(ts: string): boolean {
  return TS_RE.test(ts);
}

/**
 * 시점 이동용 — brands/<slug>/results/history/<timestamp>/dashboard/ 경로 반환.
 */
export async function brandSnapshotDir(
  slug: string,
  timestamp: string,
): Promise<string | null> {
  if (!isValidSlug(slug) || !isValidTimestamp(timestamp)) return null;
  for (const root of brandsRoots()) {
    const candidate = path.join(
      root, slug, "results", "history", timestamp, "dashboard",
    );
    try {
      const stat = await fs.stat(candidate);
      if (stat.isDirectory()) return candidate;
    } catch {
      // continue
    }
  }
  return null;
}

export async function fileMtime(filePath: string): Promise<number> {
  try {
    const stat = await fs.stat(filePath);
    return stat.mtimeMs;
  } catch {
    return 0;
  }
}
