import Link from "next/link";
import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { num, pct } from "@/lib/format";
import type { H2HByCompetitor, SpotlightEntry } from "@/types";

export function H2HDetail({
  brand,
  rows,
  winSpotlight,
  lossSpotlight,
}: {
  brand: string;
  rows: H2HByCompetitor[];
  winSpotlight: SpotlightEntry[];
  lossSpotlight: SpotlightEntry[];
}) {
  if (!rows || rows.length === 0) {
    return (
      <Card padding="md">
        <p className="text-sm text-ink-500 dark:text-ink-400">직접 비교 데이터 없음</p>
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
                <th className="px-4 py-3 text-right font-medium text-emerald-700 dark:text-emerald-400">승</th>
                <th className="px-4 py-3 text-right font-medium text-ink-500 dark:text-ink-400">무</th>
                <th className="px-4 py-3 text-right font-medium text-rose-600 dark:text-rose-400">패</th>
                <th className="px-4 py-3 text-right font-medium text-emerald-700 dark:text-emerald-400">승률</th>
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
                  <td className="px-4 py-3 text-right tabular-nums text-emerald-700 dark:text-emerald-400">
                    {num(r.wins)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-ink-500 dark:text-ink-400">
                    {num(r.draws)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums text-rose-600 dark:text-rose-400">
                    {num(r.losses)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums font-semibold text-emerald-700 dark:text-emerald-400">
                    {pct(r.win_rate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs leading-relaxed text-ink-500 dark:text-ink-400">
        직접 비교는 비교 포지셔닝 진단입니다. 승률이 낮은 경쟁사를 상대로는 비교 메시지/리뷰/차별 콘텐츠를 강화해야 합니다.
        <br />
        <span className="text-ink-400 dark:text-ink-500">
          무승부(draw)에는 AI가 한쪽을 명시 추천하지 않고 양쪽을 나란히 설명만 한 "결정 유보" 케이스도 포함됩니다. 무승부 비율이 지나치게 높다면 AI 답변에 차별화 신호를 아직 충분히 주지 못했다는 뜻입니다.
        </span>
      </p>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SpotlightBlock
          brand={brand}
          title="승리 프롬프트 top 3"
          rows={winSpotlight}
          tone="win"
          badgeLabel={(r) => `승 ${num(r.wins)}`}
          emptyMessage="승리가 기록된 프롬프트가 없습니다."
        />
        <SpotlightBlock
          brand={brand}
          title="패배 프롬프트 top 3"
          rows={lossSpotlight}
          tone="loss"
          badgeLabel={(r) => `패 ${num(r.losses)}`}
          emptyMessage="패배가 기록된 프롬프트가 없습니다."
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
  tone: "win" | "loss";
  badgeLabel: (r: SpotlightEntry) => string;
  emptyMessage: string;
}) {
  const accent =
    tone === "win"
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
              <Pill tone={tone} size="xs">
                {badgeLabel(r)}
              </Pill>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
