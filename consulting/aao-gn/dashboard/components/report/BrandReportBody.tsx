import { Section } from "@/components/primitives/Section";
import { EmptyState } from "@/components/primitives/EmptyState";
import { CoreCards } from "@/components/core/CoreCards";
import { ActionItems } from "@/components/core/ActionItems";
import { MeasurementQuality } from "@/components/core/MeasurementQuality";
import { NeutralDetail } from "@/components/category/NeutralDetail";
import { BrandOnlyDetail } from "@/components/category/BrandOnlyDetail";
import { CompOnlyDetail } from "@/components/category/CompOnlyDetail";
import { H2HDetail } from "@/components/category/H2HDetail";
import { PromptTable } from "@/components/prompts/PromptTable";
import { Card } from "@/components/primitives/Card";
import { num } from "@/lib/format";
import type { BrandData } from "@/lib/data";

export function BrandReportBody({ brand, data }: { brand: string; data: BrandData }) {
  const summary = data.summary;
  const cards = data.categoryCards;
  const cardByCode = Object.fromEntries(cards.map((c) => [c.category_code, c]));
  const spotlights = summary?.spotlights ?? {
    neutral_strong: [],
    neutral_weak: [],
    h2h_win: [],
    h2h_loss: [],
    comp_only_surfaced: [],
    comp_only_not_surfaced: [],
    brand_only_negative: [],
  };

  const totalPrompts = data.byPrompt.length;
  const totalRuns = data.auditMetadata?.total_responses ?? 0;

  return (
    <>
      <Section
        id="core-cards"
        title="핵심 진단"
        caption="4가지 질문 유형마다 의미가 다르기 때문에 각각의 카드가 분리된 질문에 답합니다"
      >
        {cards.length > 0 ? (
          <div className="space-y-4">
            <CoreCards cards={cards} />
            <details className="group rounded-xl border border-amber-200 bg-amber-50/40 dark:border-amber-900/40 dark:bg-amber-900/10">
              <summary className="flex cursor-pointer items-center justify-between gap-3 px-4 py-2.5 text-sm font-medium text-amber-900 dark:text-amber-200">
                <span>측정 신뢰도 보기</span>
                <span className="text-xs text-amber-700 dark:text-amber-400 group-open:hidden">▸ 펼치기</span>
                <span className="hidden text-xs text-amber-700 dark:text-amber-400 group-open:inline">▾ 접기</span>
              </summary>
              <div className="px-2 pb-2">
                <MeasurementQuality cards={cards} />
              </div>
            </details>
          </div>
        ) : (
          <EmptyState message="category_cards.csv 를 찾을 수 없습니다." />
        )}
      </Section>

      <Section
        id="neutral"
        title="중립 질문 성과"
        caption="브랜드를 모르는 상태의 질문에서 우리 브랜드가 얼마나 자연스럽게 등장하는가"
      >
        <NeutralDetail
          brand={brand}
          card={cardByCode["NEUTRAL"]}
          strong={spotlights.neutral_strong}
          weak={spotlights.neutral_weak}
          brandRanking={data.neutralBrandRanking}
          subcategoryBreakdown={summary?.neutral_by_subcategory ?? []}
        />
      </Section>

      <Section
        id="brand-only"
        title="브랜드 직접 질문 성과"
        caption="브랜드명을 직접 물었을 때 AI가 어떤 톤으로 소개하는가"
      >
        <BrandOnlyDetail
          brand={brand}
          card={cardByCode["BRAND_ONLY"]}
          negativeSpotlight={spotlights.brand_only_negative}
        />
      </Section>

      <Section
        id="comp-only"
        title="경쟁사 대안 질문 성과"
        caption="경쟁사 대신 다른 대안을 찾을 때 우리 브랜드가 끼어드는가"
      >
        <CompOnlyDetail
          brand={brand}
          rows={data.compOnlyByCompetitor}
          surfacedSpotlight={spotlights.comp_only_surfaced}
          notSurfacedSpotlight={spotlights.comp_only_not_surfaced}
        />
      </Section>

      <Section
        id="h2h"
        title="직접 비교 성과"
        caption="경쟁사와 정면 비교하는 질문에서 이기는가 지는가"
      >
        <H2HDetail
          brand={brand}
          rows={data.h2hByCompetitor}
          winSpotlight={spotlights.h2h_win}
          lossSpotlight={spotlights.h2h_loss}
        />
      </Section>

      <Section
        id="action-items"
        title="우선 개선 과제"
        caption="가장 중요한 3가지 — 문제 / 원인 가설 / 바로 할 일"
      >
        <ActionItems items={summary?.action_items ?? []} />
      </Section>

      <Section
        id="reference"
        title="참고 자료"
        caption="전체 프롬프트 원본·상세 탐색 (필요할 때만 펼쳐 보세요)"
      >
        <details className="group rounded-xl border border-ink-200 bg-white open:shadow-sm dark:border-ink-800 dark:bg-ink-900/40">
          <summary className="flex cursor-pointer items-center justify-between gap-3 px-5 py-3 text-sm font-medium text-ink-700 dark:text-ink-200">
            <span>전체 프롬프트 원본 테이블 열기</span>
            <span className="text-xs text-ink-500 dark:text-ink-400 tabular-nums group-open:hidden">
              ▸ {num(totalPrompts)}개 프롬프트 · {num(totalRuns)}회 응답
            </span>
            <span className="hidden text-xs text-ink-500 dark:text-ink-400 group-open:inline">▾ 접기</span>
          </summary>
          <div className="border-t border-ink-200 p-4 dark:border-ink-800">
            {data.byPrompt.length > 0 ? (
              <PromptTable brand={brand} rows={data.byPrompt} />
            ) : (
              <EmptyState message="by_prompt.csv 를 찾을 수 없습니다." />
            )}
          </div>
        </details>

        {summary?.audit_metadata || data.auditMetadata ? (
          <Card padding="md" className="mt-4">
            <div className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
              감사 메타 정보
            </div>
            <dl className="mt-2 grid grid-cols-2 gap-x-6 gap-y-2 text-xs text-ink-700 dark:text-ink-200 md:grid-cols-4">
              <Meta label="총 프롬프트 수" value={num(totalPrompts)} />
              <Meta label="총 응답 수" value={num(totalRuns)} />
              <Meta label="반복 횟수" value={num(data.auditMetadata?.repeat_count ?? 0)} />
              <Meta label="사용 모델" value={data.auditMetadata?.model || "—"} />
            </dl>
          </Card>
        ) : null}
      </Section>
    </>
  );
}

function Meta({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wider text-ink-500 dark:text-ink-400">{label}</dt>
      <dd className="mt-0.5 tabular-nums">{value}</dd>
    </div>
  );
}
