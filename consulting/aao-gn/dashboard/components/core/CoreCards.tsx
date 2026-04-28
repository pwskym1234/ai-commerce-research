import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { CIBadge } from "@/components/primitives/CIBadge";
import { pct } from "@/lib/format";
import { CATEGORY_COLORS } from "@/lib/constants";
import type { CategoryCard } from "@/types";

const CARD_ORDER = ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"] as const;

const SHORT_TITLES: Record<string, string> = {
  NEUTRAL: "중립 질문에서의 등장력",
  BRAND_ONLY: "브랜드 직접 질문 인식 톤",
  COMP_ONLY: "경쟁사 대안 탐색 침투력",
  H2H: "직접 비교 승부력",
};

const ONE_LINERS: Record<string, (c: CategoryCard) => string> = {
  NEUTRAL: (c) =>
    c.primary_metric_value >= 20
      ? "브랜드를 모르는 질문에서도 자연스럽게 후보로 등장함"
      : c.primary_metric_value >= 5
      ? "브랜드를 모르는 질문에서 가끔 등장하는 수준"
      : "브랜드를 모르는 질문에서는 거의 떠오르지 않음",
  BRAND_ONLY: (c) =>
    c.primary_metric_value >= 50
      ? "브랜드 직접 질문 시 대부분 긍정적으로 소개됨"
      : c.primary_metric_value >= 20
      ? "중립적 설명 위주, 긍정 요소 보강 여지 있음"
      : "긍정 시그널이 약함 — 평판 콘텐츠 보강 필요",
  COMP_ONLY: (c) =>
    c.primary_metric_value >= 30
      ? "경쟁사 수요를 꽤 흡수하고 있음"
      : c.primary_metric_value >= 10
      ? "일부 소환되지만 흡수력 제한적"
      : "경쟁사 대안으로 거의 노출되지 않음",
  H2H: (c) =>
    c.primary_metric_value >= 60
      ? "비교 질문에서 우위를 유지하고 있음"
      : c.primary_metric_value >= 40
      ? "비교 결과는 박빙 — 특정 경쟁사에서 약점"
      : "비교 질문에서 열세 — 비교 메시지 보강 필요",
};

const TOOLTIPS: Record<string, string> = {
  NEUTRAL:
    "브랜드를 모르는 상태에서 카테고리·상황·고민을 묻는 질문 75개. '언급률'은 AI 응답에 브랜드명이 언급된 비율.",
  BRAND_ONLY:
    "브랜드명을 직접 지목한 질문 15개. AI가 브랜드를 어떤 톤으로 소개하는지 — 긍정/중립/부정 분류.",
  COMP_ONLY:
    "경쟁사 이름을 지목해 '대안'을 묻는 질문 30개. 우리 브랜드가 대안 후보로 언급되는 비율(대안 소환율).",
  H2H:
    "우리 브랜드 + 특정 경쟁사를 직접 비교하는 질문 30개. 양측 응답 톤을 비교해 승/무/패 판정.",
};

export function CoreCards({ cards }: { cards: CategoryCard[] }) {
  const byCode = Object.fromEntries(cards.map((c) => [c.category_code, c]));

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {CARD_ORDER.map((code) => {
        const card = byCode[code];
        if (!card) return null;
        const color = CATEGORY_COLORS[code];
        const extraValue = card.extra_metric_value || "";
        return (
          <Card key={code} padding="md" className="relative">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider"
                  style={{ color }}
                >
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
                  {card.category}
                </div>
                <h3 className="mt-1 text-sm font-semibold text-ink-900 dark:text-ink-50">
                  {SHORT_TITLES[code]}
                </h3>
              </div>
              <span
                className="cursor-help rounded-full border border-ink-200 px-1.5 text-[10px] font-medium text-ink-500 dark:border-ink-700 dark:text-ink-400"
                title={TOOLTIPS[code]}
              >
                ?
              </span>
            </div>

            <div className="mt-4">
              <div className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
                {card.primary_metric_label}
              </div>
              <div
                className="mt-0.5 text-3xl font-semibold tabular-nums"
                style={{ color }}
              >
                {pct(card.primary_metric_value)}
              </div>
              {card.primary_metric_denom > 0 ? (
                <div className="mt-1">
                  <CIBadge
                    successes={card.primary_metric_count}
                    n={card.primary_metric_denom}
                  />
                </div>
              ) : null}
              {card.effective_denom > 0 &&
              (card.clarification_count > 0 || card.off_topic_count > 0) ? (
                <div className="mt-2 rounded-md border border-amber-200 bg-amber-50 px-2 py-1.5 dark:border-amber-800/60 dark:bg-amber-900/20">
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="text-[10px] font-medium uppercase tracking-wider text-amber-800 dark:text-amber-300">
                      보정값
                    </span>
                    <span
                      className="text-base font-semibold tabular-nums"
                      style={{ color }}
                    >
                      {pct(card.effective_primary_value)}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[10px] leading-snug text-amber-700 dark:text-amber-400">
                    되묻기·의도 미스매치{" "}
                    <span className="tabular-nums">
                      {card.clarification_count + card.off_topic_count}건
                    </span>{" "}
                    제외 · 유효 n={card.effective_denom}
                  </p>
                </div>
              ) : null}
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 border-t border-ink-100 pt-3 dark:border-ink-800">
              {card.secondary_metric_label ? (
                <div>
                  <div className="text-[10px] text-ink-500 dark:text-ink-400">
                    {card.secondary_metric_label}
                  </div>
                  <div className="mt-0.5 text-sm tabular-nums text-ink-800 dark:text-ink-200">
                    {pct(card.secondary_metric_value)}
                  </div>
                </div>
              ) : null}
              {card.extra_metric_label && extraValue ? (
                <div>
                  <div className="text-[10px] text-ink-500 dark:text-ink-400">
                    {card.extra_metric_label}
                  </div>
                  <div className="mt-0.5 text-sm tabular-nums text-ink-800 dark:text-ink-200">
                    {code === "H2H" || code === "BRAND_ONLY"
                      ? pct(Number(extraValue))
                      : extraValue}
                  </div>
                </div>
              ) : null}
            </div>

            <p className="mt-3 text-xs leading-relaxed text-ink-600 dark:text-ink-300">
              {ONE_LINERS[code](card)}
            </p>

            <p className="mt-1 text-[11px] text-ink-400 dark:text-ink-500">
              총 {card.total_rows}건 · {card.explain}
            </p>
          </Card>
        );
      })}
    </div>
  );
}
