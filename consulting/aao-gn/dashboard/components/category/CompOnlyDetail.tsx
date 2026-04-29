import Link from "next/link";
import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { num, pct } from "@/lib/format";
import type { CompOnlyByCompetitor, SpotlightEntry } from "@/types";

export function CompOnlyDetail({
  brand,
  rows,
  surfacedSpotlight,
  notSurfacedSpotlight,
}: {
  brand: string;
  rows: CompOnlyByCompetitor[];
  surfacedSpotlight: SpotlightEntry[];
  notSurfacedSpotlight: SpotlightEntry[];
}) {
  if (!rows || rows.length === 0) {
    return (
      <Card padding="md">
        <p className="text-sm text-ink-500 dark:text-ink-400">경쟁사 대안 질문 데이터 없음</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-ink-50 text-[11px] uppercase tracking-wider text-ink-500 dark:bg-ink-900/60 dark:text-ink-400">
              <tr>
                <th className="px-4 py-3 text-left font-medium">경쟁사</th>
                <th className="px-4 py-3 text-right font-medium">질문 수</th>
                <th className="px-4 py-3 text-right font-medium text-emerald-700 dark:text-emerald-400">대안 소환율</th>
                <th className="px-4 py-3 text-right font-medium">공동 언급률</th>
                <th className="px-4 py-3 text-right font-medium text-rose-600 dark:text-rose-400">미노출률</th>
                <th className="px-4 py-3 text-right font-medium">소환 시 평균 순위</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-200 dark:divide-ink-800">
              {rows.map((r) => (
                <tr key={r.target_competitor} className="bg-white dark:bg-ink-900/40">
                  <td className="px-4 py-3 font-medium text-ink-900 dark:text-ink-50">
                    {r.target_competitor}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-ink-500 dark:text-ink-400">
                    {num(r.total_rows)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums font-semibold text-emerald-700 dark:text-emerald-400">
                    {pct(r.surfaced_rate)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-ink-700 dark:text-ink-200">
                    {pct(r.co_mentioned_rate)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums font-semibold text-rose-600 dark:text-rose-400">
                    {pct(r.not_surfaced_rate)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-ink-500 dark:text-ink-400">
                    {r.avg_our_rank_when_ranked !== null
                      ? `${r.avg_our_rank_when_ranked.toFixed(2)}위`
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs leading-relaxed text-ink-500 dark:text-ink-400">
        대안 소환율이 높을수록 경쟁사 수요를 흡수할 가능성이 큽니다. 미노출률이 높으면 해당 경쟁사 맥락에서 AI 후보군에 진입하지 못하고 있다는 신호입니다.
      </p>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SpotlightBlock
          brand={brand}
          title="대안으로 자주 등장한 프롬프트"
          rows={surfacedSpotlight}
          tone="strong"
          badgeLabel={(r) => `소환 ${num(r.surfaced_count)}`}
          emptyMessage="대안으로 등장한 프롬프트가 없습니다."
        />
        <SpotlightBlock
          brand={brand}
          title="대안으로 전혀 나오지 않은 프롬프트"
          rows={notSurfacedSpotlight}
          tone="weak"
          badgeLabel={(r) => `미노출 ${num(r.not_surfaced_count)}`}
          emptyMessage="모든 경쟁사 대안 질문에서 최소 1회는 소환되었습니다."
        />
      </div>
    </div>
  );
}

function SpotlightBlock({
  brand,
  title,
  rows,
  tone,
  badgeLabel,
  emptyMessage,
}: {
  brand: string;
  title: string;
  rows: SpotlightEntry[];
  tone: "strong" | "weak";
  badgeLabel: (r: SpotlightEntry) => string;
  emptyMessage: string;
}) {
  const accent =
    tone === "strong"
      ? "border-l-emerald-400 dark:border-l-emerald-500"
      : "border-l-rose-400 dark:border-l-rose-500";
  return (
    <Card padding="md">
      <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">{title}</h4>
      {rows.length === 0 ? (
        <p className="mt-3 text-xs text-ink-500 dark:text-ink-400">{emptyMessage}</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {rows.map((r) => (
            <li
              key={r.prompt_id}
              className={`flex items-start justify-between gap-3 border-l-4 ${accent} rounded-r-md bg-ink-50 px-3 py-2 dark:bg-ink-900/60`}
            >
              <div className="min-w-0 flex-1">
                <Link
                  href={`/${brand}/prompts/${r.prompt_id}`}
                  className="block text-xs leading-relaxed text-ink-800 hover:text-accent dark:text-ink-100"
                >
                  {r.prompt_text || r.prompt_id}
                </Link>
                <div className="mt-1 flex items-center gap-2 text-[10px] text-ink-400 dark:text-ink-500">
                  <span className="font-mono tabular-nums">{r.prompt_id}</span>
                  {r.target_competitor ? <span>· vs {r.target_competitor}</span> : null}
                </div>
              </div>
              <Pill tone={tone === "strong" ? "win" : "danger"} size="xs">
                {badgeLabel(r)}
              </Pill>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
