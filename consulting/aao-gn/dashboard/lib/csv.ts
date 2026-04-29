import fs from "node:fs/promises";
import Papa from "papaparse";
import { z } from "zod";

export async function readCsv<S extends z.ZodTypeAny>(
  filePath: string,
  schema: S,
): Promise<z.infer<S>[] | null> {
  let raw: string;
  try {
    raw = await fs.readFile(filePath, "utf8");
  } catch {
    return null;
  }
  if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1);

  const parsed = Papa.parse(raw, {
    header: true,
    skipEmptyLines: true,
    dynamicTyping: false,
    transformHeader: (h) => h.trim(),
  });

  const rows: unknown[] = parsed.data as unknown[];
  const out: z.infer<S>[] = [];
  for (const row of rows) {
    const result = schema.safeParse(row);
    if (result.success) {
      out.push(result.data as z.infer<S>);
    } else {
      console.warn(
        `[csv] row failed validation in ${filePath}:`,
        result.error.flatten(),
      );
    }
  }
  return out;
}

export async function readJson<S extends z.ZodTypeAny>(
  filePath: string,
  schema: S,
): Promise<z.infer<S> | null> {
  let raw: string;
  try {
    raw = await fs.readFile(filePath, "utf8");
  } catch {
    return null;
  }
  let json: unknown;
  try {
    json = JSON.parse(raw);
  } catch {
    return null;
  }
  const result = schema.safeParse(json);
  if (!result.success) {
    console.warn(
      `[json] validation failed in ${filePath}:`,
      result.error.flatten(),
    );
    return null;
  }
  return result.data as z.infer<S>;
}
