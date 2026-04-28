import Link from "next/link";
import { notFound } from "next/navigation";
import { loadBrandData, loadPromptRuns } from "@/lib/data";
import { isValidSlug } from "@/lib/paths";
import { ReviewSidebar } from "@/components/prompts/ReviewSidebar";
import { ResponseReviewer } from "@/components/prompts/ResponseReviewer";
import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";

export const dynamic = "force-dynamic";

const CATEGORY_LABELS: Record<string, string> = {
  NEUTRAL: "중립",
  BRAND_ONLY: "브랜드 지명",
  COMP_ONLY: "경쟁사 대안",
  H2H: "직접 비교",
};

export default async function ReviewPage({
  params,
  searchParams,
}: {
  params: { brand: string };
  searchParams: { id?: string };
}) {
  if (!isValidSlug(params.brand)) notFound();
  const data = await loadBrandData(params.brand);
  if (!data) notFound();

  const prompts = data.byPrompt;
  const selectedId =
    searchParams.id && prompts.some((p) => p.prompt_id === searchParams.id)
      ? searchParams.id
      : prompts[0]?.prompt_id ?? null;
  const selected = prompts.find((p) => p.prompt_id === selectedId) ?? null;

  const runs = selected ? await loadPromptRuns(params.brand, selected.prompt_id) : null;
  const brandName = data.summary?.brand_name ?? params.brand;
  const competitorNames = Array.from(
    new Set([
      ...data.h2hByCompetitor.map((c) => c.target_competitor),
      ...data.compOnlyByCompetitor.map((c) => c.target_competitor),
    ]),
  ).filter(Boolean);

  return (
    <div className="flex h-[calc(100vh-180px)] flex-col gap-3 lg:h-[calc(100vh-160px)]">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-ink-900 dark:text-ink-50">
            응답 검토
          </h2>
          <p className="mt-0.5 text-xs text-ink-500 dark:text-ink-400">
            왼쪽에서 프롬프트 선택 → 오른쪽에서 모든 run의 응답을 한번에 확인. 분류기 판정이 옳은지 spot-check.
          </p>
        </div>
        <Link
          href={`/${params.brand}`}
          className="text-xs text-ink-600 hover:text-accent dark:text-ink-400"
        >
          ← 진단 리포트
        </Link>
      </div>

      <div className="grid flex-1 grid-cols-12 gap-4 overflow-hidden">
        {/* 좌측 사이드바 */}
        <div className="col-span-12 overflow-hidden rounded-lg border border-ink-200 bg-white lg:col-span-4 xl:col-span-3 dark:border-ink-800 dark:bg-ink-950">
          <ReviewSidebar
            brand={params.brand}
            prompts={prompts}
            selectedId={selectedId}
          />
        </div>

        {/* 우측 컨텐츠 */}
        <div className="col-span-12 overflow-y-auto pr-1 lg:col-span-8 xl:col-span-9">
          {selected && runs ? (
            <div className="space-y-4">
              {/* 프롬프트 헤더 */}
              <Card padding="md" className="bg-accent-soft dark:bg-accent/10">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <Pill tone="muted" size="xs">
                    {CATEGORY_LABELS[selected.category_code] || selected.category}
                  </Pill>
                  {selected.subcategory ? (
                    <span className="rounded-sm bg-ink-100 px-1.5 py-0.5 font-mono text-[10px] font-medium tabular-nums text-ink-700 dark:bg-ink-800 dark:text-ink-200">
                      {selected.subcategory}
                    </span>
                  ) : null}
                  {selected.target_competitor ? (
                    <Pill tone="warn" size="xs">vs {selected.target_competitor}</Pill>
                  ) : null}
                  <span className="ml-auto font-mono text-[11px] tabular-nums text-ink-500 dark:text-ink-400">
                    {selected.prompt_id}
                  </span>
                </div>
                <div className="mt-2 text-[11px] uppercase tracking-wider text-ink-600 dark:text-ink-300">
                  소비자가 AI에 던진 질문
                </div>
                <div className="mt-1 text-sm leading-relaxed text-ink-900 dark:text-ink-50">
                  {selected.prompt_text || "(no text)"}
                </div>
                <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 border-t border-ink-200 pt-2 text-[11px] tabular-nums text-ink-600 dark:border-ink-700 dark:text-ink-300">
                  <span>
                    언급 <strong>{selected.mention_count}/{selected.runs}</strong>
                  </span>
                  <span>
                    추천 <strong>{selected.recommendation_count ?? 0}/{selected.runs}</strong>
                  </span>
                  <span>
                    Top1 <strong>{selected.top1_count ?? 0}/{selected.runs}</strong>
                  </span>
                  {(selected.clarification_count ?? 0) > 0 ? (
                    <span className="text-amber-700 dark:text-amber-400">
                      되묻기 <strong>{selected.clarification_count}</strong>
                    </span>
                  ) : null}
                  {(selected.off_topic_count ?? 0) > 0 ? (
                    <span className="text-amber-700 dark:text-amber-400">
                      Off-topic <strong>{selected.off_topic_count}</strong>
                    </span>
                  ) : null}
                  {(selected.evasion_count ?? 0) > 0 ? (
                    <span className="text-ink-500 dark:text-ink-400">
                      회피 <strong>{selected.evasion_count}</strong>
                    </span>
                  ) : null}
                </div>
              </Card>

              <ResponseReviewer
                runs={runs}
                brandName={brandName}
                competitorNames={competitorNames}
              />
            </div>
          ) : (
            <Card padding="md">
              <p className="text-sm text-ink-500 dark:text-ink-400">
                좌측에서 프롬프트를 선택하세요.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
