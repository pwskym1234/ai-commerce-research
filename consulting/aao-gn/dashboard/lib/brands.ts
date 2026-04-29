import fs from "node:fs/promises";
import path from "node:path";
import { brandsRoots, isValidSlug } from "./paths";

export async function listBrands(): Promise<string[]> {
  const seen = new Set<string>();
  for (const root of brandsRoots()) {
    let entries: string[] = [];
    try {
      entries = await fs.readdir(root);
    } catch {
      continue;
    }
    for (const name of entries) {
      if (!isValidSlug(name)) continue;
      const dashboardPath = path.join(root, name, "results", "dashboard");
      try {
        const stat = await fs.stat(dashboardPath);
        if (stat.isDirectory()) seen.add(name);
      } catch {
        // skip
      }
    }
  }
  return Array.from(seen).sort();
}
