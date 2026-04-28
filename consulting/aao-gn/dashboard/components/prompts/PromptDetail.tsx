import { CATEGORY_LABELS, SENTIMENT_COLORS } from "@/lib/constants";
import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { num, pct, clampPct } from "@/lib/format";
import type { ByPrompt } from "@/types";

export function PromptDetail({ prompt }: { prompt: ByPrompt }) {
  const sentTotal = prompt.positive_count + prompt.neutral_count + prompt.negative_count;
  const isH2H = prompt.category_code === "H2H";
  const isCompOnly = prompt.category_code === "COMP_ONLY";
  const isBrandOnly = prompt.category_code === "BRAND_ONLY";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <Pill tone="muted" size="xs">
          {CATEGORY_LABELS[prompt.category_code] || prompt.category}
        </Pill>
        {prompt.target_competitor ? (
          <Pill tone="warn" size="xs">vs {prompt.target_competitor}</Pill>
        ) : null}
        <span className="text-xs text-ink-500 dark:text-ink-400 tabular-nums">
          · {num(prompt.runs)}회 반복
        </span>
        <span className="ml-auto font-mono text-xs tabular-nums text-ink-500 dark:text-ink-400">
          {prompt.prompt_id}
        </span>
      </div>

      {prompt.prompt_text ? (
        <Card padding="md" className="bg-accent-soft dark:bg-accent/10">
          <div className="text-[11px] uppercase tracking-wider text-ink-600 dark:text-ink-300">
            소비자가 AI에 던진 질문
          </div>
          <div className="mt-2 text-sm leading-relaxed text-ink-900 dark:text-ink-50">
            {prompt.prompt_text}
          </div>
        </Card>
      ) : null}

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Mini label="언급률" value={pct(prompt.mention_rate)} />
        <Mini label="추천률" value={pct(prompt.recommendation_rate)} accent />
        <Mini label="Top-1 비율" value={pct(prompt.top1_rate)} accent />
        <Mini label="Top-3 비율" value={pct(prompt.top3_rate)} />
      </div>

      {isH2H ? (
        <Card padding="md">
          <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
            직접 비교 결과 (승 / 무 / 패)
          </div>
          <div className="mt-2 flex items-center gap-3 text-sm tabular-nums">
            <span className="text-emerald-600 dark:text-emerald-400">승 {num(prompt.wins)}</span>
            <span className="text-ink-500 dark:text-ink-400">무 {num(prompt.draws)}</span>
            <span className="text-rose-600 dark:text-rose-400">패 {num(prompt.losses)}</span>
          </div>
        </Card>
      ) : null}

      {isCompOnly ? (
        <Card padding="md">
          <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
            경쟁사 대안 탐색 결과
          </div>
          <div className="mt-2 flex items-center gap-3 text-sm tabular-nums">
            <span className="text-emerald-600 dark:text-emerald-400">
              대안으로 등장 {num(prompt.surfaced_count)}
            </span>
            <span className="text-ink-500 dark:text-ink-400">공동 언급 {num(prompt.co_mentioned_count ?? 0)}</span>
            <span className="text-rose-600 dark:text-rose-400">대안으로 안 나옴 {num(prompt.not_surfaced_count)}</span>
          </div>
        </Card>
      ) : null}

      {(isBrandOnly || sentTotal > 0) ? (
        <Card padding="md">
          <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
            감성 분포 ({num(sentTotal)}건)
          </div>
          {sentTotal > 0 ? (
            <div className="mt-2 flex h-2.5 overflow-hidden rounded-full">
              <div
                style={{
                  width: `${clampPct((prompt.positive_count / sentTotal) * 100)}%`,
                  background: SENTIMENT_COLORS.positive,
                }}
              />
              <div
                style={{
                  width: `${clampPct((prompt.neutral_count / sentTotal) * 100)}%`,
                  background: SENTIMENT_COLORS.neutral,
                }}
              />
              <div
                style={{
                  width: `${clampPct((prompt.negative_count / sentTotal) * 100)}%`,
                  background: SENTIMENT_COLORS.negative,
                }}
              />
            </div>
          ) : (
            <div className="mt-2 text-xs text-ink-400 dark:text-ink-500">데이터 없음</div>
          )}
          <div className="mt-2 flex justify-between text-[11px] tabular-nums text-ink-500 dark:text-ink-400">
            <span className="text-emerald-600 dark:text-emerald-400">긍정 {num(prompt.positive_count)}</span>
            <span>중립 {num(prompt.neutral_count)}</span>
            <span className="text-rose-600 dark:text-rose-400">부정 {num(prompt.negative_count)}</span>
          </div>
        </Card>
      ) : null}

      {prompt.sample_response_preview ? (
        <Card padding="md" className="bg-ink-50 dark:bg-ink-900/60">
          <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
            응답 샘플 (첫 번째 run · 최대 800자)
          </div>
          <blockquote className="mt-2 border-l-2 border-accent/60 pl-3 font-mono text-[13px] leading-relaxed text-ink-700 dark:text-ink-200">
            “{prompt.sample_response_preview}”
          </blockquote>
        </Card>
      ) : null}
    </div>
  );
}

function Mini({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <Card padding="sm">
      <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
        {label}
      </div>
      <div
        className={`mt-1 text-stat tabular-nums ${
          accent ? "text-accent" : "text-ink-900 dark:text-ink-50"
        }`}
      >
        {value}
      </div>
    </Card>
  );
}
