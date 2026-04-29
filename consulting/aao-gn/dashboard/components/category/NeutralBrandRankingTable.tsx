import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { num, pct, clampPct } from "@/lib/format";
import type { NeutralBrandRanking } from "@/types";

export function NeutralBrandRankingTable({ data }: { data: NeutralBrandRanking | null }) {
  if (!data || !data.rows || data.rows.length === 0) {
    return null;
  }

  const total = data.total_runs;
  const ourRank = data.our_brand_rank;
  const detectedBrandCount = data.total_brands_detected;
  const topShare = data.rows[0]?.share ?? 0;
  const competitorRows = data.rows.filter((r) => !r.is_ours);
  const noBrandsSurfaced =
    competitorRows.length === 0 ||
    competitorRows.every((r) => r.hit_count === 0);

  return (
    <Card padding="md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
            중립 질문 응답 속 브랜드 점유율 랭킹
          </h4>
          <p className="mt-1 text-xs text-ink-500 dark:text-ink-400">
            AI 응답 {num(total)}건에 등장한 모든 제품·브랜드를 집계. 우리 브랜드가 경쟁 지형에서 몇 위에 있는지 보여줍니다.
          </p>
        </div>
        <div className="shrink-0 text-right">
          <div className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
            우리 브랜드 순위
          </div>
          <div className="mt-0.5 text-2xl font-semibold tabular-nums text-rose-600 dark:text-rose-400">
            {ourRank !== null ? `${ourRank}위` : "순외"}
          </div>
          <div className="text-[10px] text-ink-500 dark:text-ink-400 tabular-nums">
            총 {num(detectedBrandCount)}개 브랜드 감지 중
          </div>
        </div>
      </div>

      {noBrandsSurfaced ? (
        <div className="mt-4 rounded-md border border-amber-300 bg-amber-50 px-3 py-2.5 text-xs leading-relaxed text-amber-900 dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-200">
          <strong className="font-semibold">⚠ 응답에서 특정 브랜드명이 거의 등장하지 않음.</strong>{" "}
          AI가 일반 카테고리어(예: “케겔 트레이너”, “저항밴드”)나 기능·증상 설명으로만 답변하고
          구체 브랜드를 언급하지 않은 결과입니다. 이는 (1) 해당 카테고리의 브랜드 인지도가 시장 전반적으로 낮거나
          (2) AI가 검색을 적극적으로 호출하지 않은 결과일 수 있으며, 그 자체가 진단 신호입니다.
          더 큰 모델(예: gpt-5.4 풀 버전)로 재실행하면 다른 분포가 나올 수 있어요.
        </div>
      ) : null}

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-ink-50 text-[11px] uppercase tracking-wider text-ink-500 dark:bg-ink-900/60 dark:text-ink-400">
            <tr>
              <th className="px-3 py-2 text-right font-medium w-12">순위</th>
              <th className="px-3 py-2 text-left font-medium">브랜드 / 제품명</th>
              <th className="px-3 py-2 text-right font-medium w-20">등장</th>
              <th className="px-3 py-2 text-right font-medium w-24">점유율</th>
              <th className="px-3 py-2 text-left font-medium w-48">점유율 분포</th>
              <th className="px-3 py-2 text-left font-medium w-28">분류</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-200 dark:divide-ink-800">
            {data.rows.map((r) => {
              const barWidth = topShare > 0 ? clampPct((r.share / topShare) * 100) : 0;
              const barColor = r.is_ours
                ? "bg-rose-500"
                : r.is_known_competitor
                ? "bg-amber-500"
                : "bg-ink-400 dark:bg-ink-500";
              const rowHighlight = r.is_ours
                ? "bg-rose-50 dark:bg-rose-900/20"
                : "";
              return (
                <tr key={`${r.rank}-${r.brand}`} className={rowHighlight}>
                  <td
                    className={`px-3 py-2 text-right tabular-nums font-medium ${
                      r.is_ours ? "text-rose-700 dark:text-rose-400" : "text-ink-500 dark:text-ink-400"
                    }`}
                  >
                    {r.rank}
                  </td>
                  <td
                    className={`px-3 py-2 ${
                      r.is_ours
                        ? "font-semibold text-rose-700 dark:text-rose-400"
                        : "text-ink-900 dark:text-ink-50"
                    }`}
                  >
                    {r.brand}
                    {r.is_ours ? (
                      <span className="ml-1.5 text-[10px] font-medium text-rose-600 dark:text-rose-300">
                        ◉ 우리
                      </span>
                    ) : null}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums text-ink-700 dark:text-ink-200">
                    {num(r.hit_count)}
                  </td>
                  <td
                    className={`px-3 py-2 text-right tabular-nums font-medium ${
                      r.is_ours ? "text-rose-700 dark:text-rose-400" : "text-ink-900 dark:text-ink-50"
                    }`}
                  >
                    {pct(r.share)}
                  </td>
                  <td className="px-3 py-2">
                    <div className="h-2 overflow-hidden rounded-full bg-ink-100 dark:bg-ink-800">
                      <div className={`h-full ${barColor}`} style={{ width: `${barWidth}%` }} />
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    {r.is_ours ? (
                      <Pill tone="danger" size="xs">우리 브랜드</Pill>
                    ) : r.is_known_competitor ? (
                      <Pill tone="warn" size="xs">경쟁사</Pill>
                    ) : (
                      <Pill tone="muted" size="xs">기타</Pill>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-ink-500 dark:text-ink-400">
        * "등장"은 {num(total)}개의 AI 응답 중 해당 브랜드가 텍스트에 노출된 응답 수.
        brand_config에 등록된 경쟁사는 "경쟁사"로 표시되고, 그 외 응답에서 자동 추출된 브랜드는 "기타"로 표시됩니다.
        "기타"에는 우리가 인지하지 못한 실질 경쟁자가 포함될 수 있으므로 우선적으로 검토할 가치가 있습니다.
      </p>
    </Card>
  );
}
