import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import type { ActionItem } from "@/types";

const PRIMARY_COUNT = 3;

export function ActionItems({ items }: { items: ActionItem[] }) {
  if (!items || items.length === 0) {
    return (
      <Card padding="md" className="bg-ink-50 dark:bg-ink-900/60">
        <p className="text-sm text-ink-500 dark:text-ink-400">
          현재 우선 개선 과제 없음 — 유지 모니터링을 권장합니다.
        </p>
      </Card>
    );
  }

  const primary = items.slice(0, PRIMARY_COUNT);
  const rest = items.slice(PRIMARY_COUNT);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {primary.map((item, i) => (
          <Card key={i} padding="md" className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-rose-100 text-xs font-semibold text-rose-700 dark:bg-rose-500/20 dark:text-rose-300">
                {i + 1}
              </span>
              <Pill tone="warn" size="xs">우선</Pill>
            </div>
            <h4 className="mt-2 text-sm font-semibold leading-snug text-ink-900 dark:text-ink-50">
              {item.problem}
            </h4>

            <div className="mt-3">
              <div className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
                원인 가설
              </div>
              <p className="mt-0.5 text-xs leading-relaxed text-ink-600 dark:text-ink-300">
                {item.hypothesis}
              </p>
            </div>

            <div className="mt-3 border-t border-ink-100 pt-3 dark:border-ink-800">
              <div className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
                바로 할 일
              </div>
              <ul className="mt-1.5 space-y-1">
                {item.actions.map((a, j) => (
                  <li
                    key={j}
                    className="flex items-start gap-2 text-xs text-ink-800 dark:text-ink-100"
                  >
                    <span className="mt-0.5 text-accent">✓</span>
                    <span className="leading-relaxed">{a}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        ))}
      </div>

      {rest.length > 0 ? (
        <Card padding="md">
          <div className="flex items-baseline justify-between gap-2">
            <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
              그 외 개선 과제
            </h4>
            <span className="text-[11px] text-ink-500 dark:text-ink-400">
              {rest.length}건 — 우선 3개 다음 순위
            </span>
          </div>
          <ul className="mt-3 space-y-3">
            {rest.map((item, i) => (
              <li
                key={i}
                className="border-l-2 border-ink-200 pl-3 dark:border-ink-700"
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] tabular-nums text-ink-400 dark:text-ink-500">
                    #{i + PRIMARY_COUNT + 1}
                  </span>
                  <h5 className="text-xs font-semibold text-ink-900 dark:text-ink-50">
                    {item.problem}
                  </h5>
                </div>
                <p className="mt-1 text-[11px] leading-relaxed text-ink-600 dark:text-ink-300">
                  <span className="text-ink-400 dark:text-ink-500">원인 가설:</span>{" "}
                  {item.hypothesis}
                </p>
                {item.actions.length > 0 ? (
                  <ul className="mt-1.5 flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-ink-700 dark:text-ink-200">
                    {item.actions.map((a, j) => (
                      <li key={j} className="inline-flex items-start gap-1">
                        <span className="text-accent">✓</span>
                        <span>{a}</span>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}
