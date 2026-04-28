import Link from "next/link";
import { Card } from "@/components/primitives/Card";
import { MetricBar } from "@/components/primitives/MetricBar";
import { Pill } from "@/components/primitives/Pill";
import { pct } from "@/lib/format";
import { NeutralBrandRankingTable } from "@/components/category/NeutralBrandRankingTable";
import type {
  CategoryCard,
  NeutralBrandRanking,
  NeutralSubcategoryRow,
  SpotlightEntry,
} from "@/types";

export function NeutralDetail({
  brand,
  card,
  strong,
  weak,
  brandRanking,
  subcategoryBreakdown = [],
}: {
  brand: string;
  card: CategoryCard | undefined;
  strong: SpotlightEntry[];
  weak: SpotlightEntry[];
  brandRanking: NeutralBrandRanking | null;
  subcategoryBreakdown?: NeutralSubcategoryRow[];
}) {
  if (!card) {
    return (
      <Card padding="md">
        <p className="text-sm text-ink-500 dark:text-ink-400">중립 질문 데이터 없음</p>
      </Card>
    );
  }

  const mentionRate = card.primary_metric_value;
  const recoRate = card.secondary_metric_value;

  return (
    <div className="space-y-4">
      <Card padding="md">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <RatePanel label="언급률" value={mentionRate} hint="중립 질문에서 AI 응답에 우리 브랜드가 언급된 비율" />
          <RatePanel label="추천률" value={recoRate} tone="accent" hint="언급을 넘어 '추천' 맥락으로 등장한 비율" />
        </div>
        <p className="mt-4 text-xs leading-relaxed text-ink-500 dark:text-ink-400">
          {mentionRate < 5
            ? "중립 질문에서 거의 떠오르지 않습니다 — 브랜드 인지/노출 콘텐츠 보강이 시급합니다."
            : mentionRate < 20
            ? "가끔 언급되지만 기본 후보군 수준은 아닙니다 — 카테고리 탐색·비교형 콘텐츠 확대가 필요합니다."
            : "중립 질문에서도 자연스럽게 후보로 등장합니다."}
        </p>
      </Card>

      {subcategoryBreakdown.length > 0 ? (
        <SubcategoryBreakdown rows={subcategoryBreakdown} />
      ) : null}

      <NeutralBrandRankingTable data={brandRanking} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SpotlightList
          brand={brand}
          title="강점 프롬프트 — 자주 언급된 질문"
          rows={strong}
          emptyMessage="언급된 중립 프롬프트가 없습니다."
          metric="mention_rate"
        />
        <SpotlightList
          brand={brand}
          title="약점 프롬프트 — 전혀 언급되지 않은 질문"
          rows={weak}
          emptyMessage="모든 중립 질문에서 최소 1회는 언급되었습니다."
          metric="none"
          tone="weak"
        />
      </div>
    </div>
  );
}

// 각 서브분류 의미 + 예시 질문 (대시보드에서만 사용 — 데이터 컬럼은 코드/라벨만)
const SUBCATEGORY_DESCRIPTIONS: Record<
  string,
  { intent: string; example: string }
> = {
  CAT: {
    intent: "카테고리 일반 — '뭘 사야 돼?' 같은 가장 평범한 추천 질문",
    example: "“입문자한테 무난한 거 뭐 있어?”",
  },
  SYM: {
    intent: "증상·상황 — 일상의 불편을 집에서 어떻게 해결할지 묻는 질문",
    example: "“기침할 때 찔끔 새는데 도움되는 거 있어?”",
  },
  ALT: {
    intent: "솔루션 대안 — 제품 vs 운동·시술·앱 등 다른 해결 방식과 비교",
    example: "“운동으로 할지 기기 살지 고민”",
  },
  PRC: {
    intent: "가격 — 예산·가성비 시그널이 들어간 질문",
    example: "“5만원 이하로 살 만한 거 추천해줘”",
  },
  USE: {
    intent: "유스케이스 — 시간·장소·대상이 구체적인 사용 맥락 질문",
    example: "“출근 전에 쓸 건데 뭐 좋아?”",
  },
  DEC: {
    intent: "구매의도 단일선택 — 여러 후보 말고 ‘딱 하나’만 꼽으라는 질문",
    example: "“딱 하나만 추천해줘”",
  },
};

function SubcategoryBreakdown({ rows }: { rows: NeutralSubcategoryRow[] }) {
  return (
    <Card padding="md">
      <div>
        <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
          서브분류별 성과
        </h4>
        <p className="mt-1 text-xs leading-relaxed text-ink-500 dark:text-ink-400">
          중립 질문(브랜드를 모르는 상태의 질문)을 사용자 의도에 따라 6종으로 쪼갠 결과예요.
          의도가 다르면 AI 응답 패턴도 달라지기 때문에 평균 한 숫자에 묻혀버리지 않도록
          분리해서 봐요. 각 행 = 그 의도에 해당하는 질문들을 모아 측정한 비율입니다.
        </p>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-ink-200 text-left text-[11px] uppercase tracking-wider text-ink-500 dark:border-ink-700 dark:text-ink-400">
              <th className="py-2 pr-3">의도</th>
              <th className="py-2 pr-3 text-right">n</th>
              <th className="py-2 pr-3">언급률</th>
              <th className="py-2 pr-3">추천률</th>
              <th className="py-2 pr-3">Top1율</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100 dark:divide-ink-800">
            {rows.map((r) => {
              const desc = SUBCATEGORY_DESCRIPTIONS[r.subcategory];
              return (
                <tr key={r.subcategory} className="align-top">
                  <td className="py-2.5 pr-3">
                    <div className="flex items-center gap-2">
                      <span
                        className="rounded-sm bg-ink-100 px-1.5 py-0.5 font-mono text-[10px] font-medium tabular-nums text-ink-700 dark:bg-ink-800 dark:text-ink-200"
                        title={desc?.intent}
                      >
                        {r.subcategory}
                      </span>
                      <span className="text-xs font-medium text-ink-800 dark:text-ink-100">
                        {r.subcategory_label}
                      </span>
                    </div>
                    {desc ? (
                      <div className="mt-1 max-w-md text-[11px] leading-relaxed text-ink-500 dark:text-ink-400">
                        <span>{desc.intent.split(" — ")[1] ?? desc.intent}</span>
                        <span className="ml-1.5 italic text-ink-400 dark:text-ink-500">
                          예: {desc.example}
                        </span>
                      </div>
                    ) : null}
                  </td>
                  <td className="py-2.5 pr-3 text-right tabular-nums text-ink-700 dark:text-ink-200">
                    {r.total_rows}
                  </td>
                  <td className="py-2.5 pr-3">
                    <div className="w-32">
                      <MetricBar
                        value={r.mention_rate}
                        successes={r.mention_count}
                        n={r.total_rows}
                        showLabel
                      />
                    </div>
                  </td>
                  <td className="py-2.5 pr-3">
                    <div className="w-32">
                      <MetricBar
                        value={r.recommendation_rate}
                        successes={r.recommendation_count}
                        n={r.total_rows}
                        showLabel
                      />
                    </div>
                  </td>
                  <td className="py-2.5 pr-3">
                    <div className="w-32">
                      <MetricBar
                        value={r.top1_rate}
                        successes={r.top1_count}
                        n={r.total_rows}
                        showLabel
                      />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function RatePanel({
  label,
  value,
  tone = "default",
  hint,
}: {
  label: string;
  value: number;
  tone?: "default" | "accent";
  hint: string;
}) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
        {label}
      </div>
      <div
        className={`mt-1 text-3xl font-semibold tabular-nums ${
          tone === "accent" ? "text-accent" : "text-ink-900 dark:text-ink-50"
        }`}
      >
        {pct(value)}
      </div>
      <div className="mt-2">
        <MetricBar value={value} />
      </div>
      <p className="mt-2 text-[11px] text-ink-500 dark:text-ink-400">{hint}</p>
    </div>
  );
}

function SpotlightList({
  brand,
  title,
  rows,
  emptyMessage,
  metric,
  tone = "strong",
}: {
  brand: string;
  title: string;
  rows: SpotlightEntry[];
  emptyMessage: string;
  metric: "mention_rate" | "none";
  tone?: "strong" | "weak";
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
                <div className="mt-1 font-mono text-[10px] tabular-nums text-ink-400 dark:text-ink-500">
                  {r.prompt_id}
                </div>
              </div>
              {metric === "mention_rate" ? (
                <Pill tone="accent" size="xs">
                  {pct(r.mention_rate)}
                </Pill>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
