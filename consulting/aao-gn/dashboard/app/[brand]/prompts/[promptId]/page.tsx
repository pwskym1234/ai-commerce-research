import Link from "next/link";
import { notFound } from "next/navigation";
import { loadBrandData, loadPromptRuns } from "@/lib/data";
import { isValidSlug } from "@/lib/paths";
import { PromptDetail } from "@/components/prompts/PromptDetail";
import { ResponseReviewer } from "@/components/prompts/ResponseReviewer";

export const dynamic = "force-dynamic";

export default async function PromptPage({
  params,
}: {
  params: { brand: string; promptId: string };
}) {
  if (!isValidSlug(params.brand)) notFound();
  const data = await loadBrandData(params.brand);
  if (!data || !data.byPrompt) notFound();
  const prompt = data.byPrompt.find((p) => p.prompt_id === params.promptId);
  if (!prompt) notFound();

  const runs = await loadPromptRuns(params.brand, params.promptId);
  const brandName = data.summary?.brand_name ?? params.brand;
  // 경쟁사 이름은 h2h + comp_only 양쪽에서 모음 (중복 제거)
  const competitorNames = Array.from(
    new Set([
      ...data.h2hByCompetitor.map((c) => c.target_competitor),
      ...data.compOnlyByCompetitor.map((c) => c.target_competitor),
    ]),
  ).filter(Boolean);

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <Link
        href={`/${params.brand}#prompts`}
        className="mb-4 inline-flex items-center gap-1 text-xs font-medium text-ink-500 hover:text-accent dark:text-ink-400"
      >
        ← 진단 리포트로 돌아가기
      </Link>
      <div className="space-y-6">
        <PromptDetail prompt={prompt} />
        <ResponseReviewer
          runs={runs ?? []}
          brandName={brandName}
          competitorNames={competitorNames}
        />
      </div>
    </div>
  );
}
