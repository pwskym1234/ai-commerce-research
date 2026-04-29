import path from "node:path";
import fs from "node:fs/promises";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Card } from "@/components/primitives/Card";
import { Section } from "@/components/primitives/Section";
import { Pill } from "@/components/primitives/Pill";
import { brandsRoots, isValidSlug } from "@/lib/paths";

export const dynamic = "force-dynamic";

interface ClassifierSpec {
  classifier_model: string | null;
  classifier_mode: string;
  sentiment_classes: Record<string, string>;
  known_biases: string[];
  output_schema: unknown;
  system_prompt: string;
}

async function loadSpec(slug: string): Promise<ClassifierSpec | null> {
  for (const root of brandsRoots()) {
    const p = path.join(root, slug, "results", "classifier_spec.json");
    try {
      const raw = await fs.readFile(p, "utf8");
      return JSON.parse(raw) as ClassifierSpec;
    } catch {
      // try next
    }
  }
  return null;
}

export default async function MethodPage({
  params,
}: {
  params: { brand: string };
}) {
  if (!isValidSlug(params.brand)) notFound();
  const spec = await loadSpec(params.brand);

  return (
    <Section
      id="method"
      title="분석 방법 공개"
      caption="외부 감사·재현을 위해 실제로 쓰이는 분류기의 스펙을 공개합니다."
      action={
        <Link
          href={`/${params.brand}`}
          className="text-sm text-ink-600 hover:text-ink-900 dark:text-ink-400 dark:hover:text-ink-100"
        >
          ← 대시보드로
        </Link>
      }
    >
      {!spec ? (
        <Card padding="md">
          <p className="text-sm text-ink-600 dark:text-ink-300">
            아직 분류기 스펙이 생성되지 않았습니다.{" "}
            <code className="rounded bg-ink-100 px-1 py-0.5 text-xs dark:bg-ink-800">
              python 04_parse_responses.py --brand ...
            </code>{" "}
            를 한 번 더 실행하면{" "}
            <code className="rounded bg-ink-100 px-1 py-0.5 text-xs dark:bg-ink-800">
              results/classifier_spec.json
            </code>{" "}
            이 생성됩니다.
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          <Card padding="md">
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <span className="text-ink-500 dark:text-ink-400">모델</span>
              <Pill tone="accent" size="sm">
                {spec.classifier_model ?? "텍스트 매칭 전용"}
              </Pill>
              <span className="text-ink-500 dark:text-ink-400">모드</span>
              <code className="rounded bg-ink-100 px-1.5 py-0.5 text-xs dark:bg-ink-800">
                {spec.classifier_mode}
              </code>
            </div>
          </Card>

          <Card padding="md">
            <h3 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
              감성 분류 클래스
            </h3>
            <dl className="mt-3 space-y-2 text-sm">
              {Object.entries(spec.sentiment_classes).map(([k, v]) => (
                <div key={k} className="grid grid-cols-[100px_1fr] gap-3">
                  <dt>
                    <Pill
                      tone={
                        k === "positive"
                          ? "accent"
                          : k === "negative"
                          ? "danger"
                          : "muted"
                      }
                      size="xs"
                    >
                      {k}
                    </Pill>
                  </dt>
                  <dd className="text-ink-700 dark:text-ink-200">{v}</dd>
                </div>
              ))}
            </dl>
          </Card>

          <Card padding="md">
            <h3 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
              알려진 편향 (분류기 한계)
            </h3>
            <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm text-ink-700 dark:text-ink-200">
              {spec.known_biases.map((bias, i) => (
                <li key={i}>{bias}</li>
              ))}
            </ul>
          </Card>

          <Card padding="md">
            <h3 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
              시스템 프롬프트 (전문)
            </h3>
            <p className="mt-1 text-xs text-ink-500 dark:text-ink-400">
              매 호출에서 동일하게 전달되는 instruction. prompt caching 대상.
            </p>
            <pre className="mt-3 max-h-[480px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-ink-200 bg-ink-50 p-3 text-[11px] leading-relaxed text-ink-800 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-200">
              {spec.system_prompt}
            </pre>
          </Card>

          <Card padding="md">
            <h3 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
              출력 스키마 (JSON Schema)
            </h3>
            <pre className="mt-3 max-h-[360px] overflow-auto rounded-md border border-ink-200 bg-ink-50 p-3 text-[11px] leading-relaxed text-ink-800 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-200">
              {JSON.stringify(spec.output_schema, null, 2)}
            </pre>
          </Card>
        </div>
      )}
    </Section>
  );
}
