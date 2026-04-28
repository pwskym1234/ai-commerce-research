import { wilsonCI95Pct } from "@/lib/stats";

interface CIBadgeProps {
  successes: number;
  n: number;
  className?: string;
}

// 점추정 뒤에 붙는 95% CI 배지. n 없으면 렌더 안 함.
export function CIBadge({ successes, n, className = "" }: CIBadgeProps) {
  if (!Number.isFinite(n) || n <= 0) return null;
  const ci = wilsonCI95Pct(successes, n);
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] tabular-nums text-ink-500 dark:text-ink-400 ${className}`}
      title={`n=${ci.n} · Wilson 95% 신뢰구간`}
    >
      <span>95% CI</span>
      <span className="font-medium">
        [{ci.low.toFixed(1)}, {ci.high.toFixed(1)}]
      </span>
    </span>
  );
}
