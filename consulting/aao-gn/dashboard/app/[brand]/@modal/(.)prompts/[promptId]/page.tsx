import { notFound } from "next/navigation";
import { loadBrandData } from "@/lib/data";
import { isValidSlug } from "@/lib/paths";
import { PromptDetail } from "@/components/prompts/PromptDetail";
import { PromptModal } from "@/components/prompts/PromptModal";

export const dynamic = "force-dynamic";

export default async function InterceptedPrompt({
  params,
}: {
  params: { brand: string; promptId: string };
}) {
  if (!isValidSlug(params.brand)) notFound();
  const data = await loadBrandData(params.brand);
  if (!data || !data.byPrompt) notFound();

  const prompt = data.byPrompt.find((p) => p.prompt_id === params.promptId);
  if (!prompt) notFound();

  return (
    <PromptModal brand={params.brand}>
      <PromptDetail prompt={prompt} />
    </PromptModal>
  );
}
