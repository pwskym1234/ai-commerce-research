// Wilson 95% 신뢰구간 — 이항 비율의 표준 신뢰구간. n 작을 때도 안정적.
// Wilson E. B. (1927). JASA, 22(158). z=1.96 (95% 신뢰수준).
export interface WilsonCI {
  point: number;   // 점추정치 (0..1)
  low: number;     // 95% CI 하한 (0..1)
  high: number;    // 95% CI 상한 (0..1)
  n: number;
  successes: number;
  hasData: boolean;
}

const Z_95 = 1.96;

export function wilsonCI95(successes: number, n: number): WilsonCI {
  if (!Number.isFinite(n) || n <= 0) {
    return { point: 0, low: 0, high: 1, n: 0, successes: 0, hasData: false };
  }
  const k = Math.max(0, Math.min(successes, n));
  const p = k / n;
  const z2 = Z_95 * Z_95;
  const denom = 1 + z2 / n;
  const center = (p + z2 / (2 * n)) / denom;
  const half = (Z_95 * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / denom;
  return {
    point: p,
    low: Math.max(0, center - half),
    high: Math.min(1, center + half),
    n,
    successes: k,
    hasData: true,
  };
}

// 퍼센트 형식 (0..100) → Wilson CI도 0..100 스케일로 반환.
export interface WilsonCIPct {
  point: number;
  low: number;
  high: number;
  n: number;
  successes: number;
  hasData: boolean;
}

export function wilsonCI95Pct(successes: number, n: number): WilsonCIPct {
  const ci = wilsonCI95(successes, n);
  return {
    point: ci.point * 100,
    low: ci.low * 100,
    high: ci.high * 100,
    n: ci.n,
    successes: ci.successes,
    hasData: ci.hasData,
  };
}

// "6.7% · 95% CI [1.1, 21.4]" 형식.
export function formatCIPct(ci: WilsonCIPct, fractionDigits = 1): string {
  if (!ci.hasData) return "-";
  const p = ci.point.toFixed(fractionDigits);
  const lo = ci.low.toFixed(fractionDigits);
  const hi = ci.high.toFixed(fractionDigits);
  return `${p}% · 95% CI [${lo}, ${hi}]`;
}
