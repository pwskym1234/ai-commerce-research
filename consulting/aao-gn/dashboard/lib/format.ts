const KO = "ko-KR";

export function pct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

export function num(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  return value.toLocaleString(KO);
}

export function rank(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  return `${value.toFixed(2)}위`;
}

export function relativeTime(mtimeMs: number): string {
  if (!mtimeMs) return "—";
  const now = Date.now();
  const diffMs = now - mtimeMs;
  const min = 60 * 1000;
  const hr = 60 * min;
  const day = 24 * hr;
  if (diffMs < min) return "방금 전";
  if (diffMs < hr) return `${Math.floor(diffMs / min)}분 전`;
  if (diffMs < day) return `${Math.floor(diffMs / hr)}시간 전`;
  if (diffMs < 7 * day) return `${Math.floor(diffMs / day)}일 전`;
  const d = new Date(mtimeMs);
  return d.toLocaleDateString(KO, { year: "numeric", month: "2-digit", day: "2-digit" });
}

function pad2(n: number) {
  return n < 10 ? `0${n}` : String(n);
}

export function absoluteTime(mtimeMs: number): string {
  if (!mtimeMs) return "—";
  const d = new Date(mtimeMs);
  // 로케일 독립 포맷 — 서버(Node ICU)와 클라이언트 브라우저 간 하이드레이션 차이 방지
  return `${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

export function absoluteDate(mtimeMs: number): string {
  if (!mtimeMs) return "—";
  const d = new Date(mtimeMs);
  return `${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())}`;
}

export function clampPct(v: number): number {
  if (!Number.isFinite(v)) return 0;
  return Math.max(0, Math.min(100, v));
}
