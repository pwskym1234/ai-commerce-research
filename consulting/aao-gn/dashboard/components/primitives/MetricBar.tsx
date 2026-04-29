import { clampPct } from "@/lib/format";
import { wilsonCI95Pct } from "@/lib/stats";

interface MetricBarProps {
  value: number;
  max?: number;
  tone?: "default" | "win" | "loss" | "warn";
  height?: number;
  showLabel?: boolean;
  // Optional Wilson 95% CI overlay — 둘 다 제공되면 CI 밴드 + hover 툴팁 렌더.
  successes?: number;
  n?: number;
}

const TONES = {
  default: "bg-ink-900 dark:bg-ink-100",
  win: "bg-emerald-500",
  loss: "bg-rose-500",
  warn: "bg-amber-500",
};

const CI_TONES = {
  default: "bg-ink-900/20 dark:bg-ink-100/20",
  win: "bg-emerald-500/25",
  loss: "bg-rose-500/25",
  warn: "bg-amber-500/25",
};

export function MetricBar({
  value,
  max = 100,
  tone = "default",
  height = 6,
  showLabel = false,
  successes,
  n,
}: MetricBarProps) {
  const ratio = Math.max(0, Math.min(100, (value / max) * 100));
  const hasCI =
    successes !== undefined &&
    n !== undefined &&
    Number.isFinite(successes) &&
    Number.isFinite(n) &&
    n > 0;
  const ci = hasCI ? wilsonCI95Pct(successes!, n!) : null;
  const title = ci
    ? `n=${ci.n} · 95% CI [${ci.low.toFixed(1)}%, ${ci.high.toFixed(1)}%]`
    : undefined;
  return (
    <div className="flex items-center gap-2">
      <div
        className="relative flex-1 overflow-hidden rounded-full bg-ink-100 dark:bg-ink-800"
        style={{ height }}
        title={title}
      >
        {ci ? (
          <div
            className={`absolute top-0 h-full ${CI_TONES[tone]}`}
            style={{
              left: `${clampPct((ci.low / max) * 100)}%`,
              width: `${clampPct(((ci.high - ci.low) / max) * 100)}%`,
            }}
            aria-hidden
          />
        ) : null}
        <div
          className={`relative h-full ${TONES[tone]}`}
          style={{ width: `${clampPct(ratio)}%` }}
        />
      </div>
      {showLabel ? (
        <span className="w-10 shrink-0 text-right text-xs tabular-nums text-ink-600 dark:text-ink-400">
          {value.toFixed(1)}%
        </span>
      ) : null}
    </div>
  );
}
