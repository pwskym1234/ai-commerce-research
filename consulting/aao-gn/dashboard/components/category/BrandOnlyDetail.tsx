import Link from "next/link";
import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import { clampPct, pct, num } from "@/lib/format";
import { SENTIMENT_COLORS } from "@/lib/constants";
import type { CategoryCard, SpotlightEntry } from "@/types";

export function BrandOnlyDetail({
  brand,
  card,
  negativeSpotlight,
}: {
  brand: string;
  card: CategoryCard | undefined;
  negativeSpotlight: SpotlightEntry[];
}) {
  if (!card) {
    return (
      <Card padding="md">
        <p className="text-sm text-ink-500 dark:text-ink-400">브랜드 직접 질문 데이터 없음</p>
      </Card>
    );
  }

  const positive = card.primary_metric_value;
  const negative = card.secondary_metric_value;
  const neutral = Number(card.extra_metric_value || 0);
  const total = positive + negative + neutral;

  return (
    <div className="space-y-4">
      <Card padding="md">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Tone label="긍정 비율" value={positive} color={SENTIMENT_COLORS.positive} />
          <Tone label="중립 비율" value={neutral} color={SENTIMENT_COLORS.neutral} />
          <Tone label="부정 비율" value={negative} color={SENTIMENT_COLORS.negative} />
        </div>
        {total > 0 ? (
          <div className="mt-5">
            <div className="text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
              감성 분포 (언급된 {card.total_rows}건 중)
            </div>
            <div className="mt-2 flex h-3 overflow-hidden rounded-full">
              <div
                style={{ width: `${clampPct(positive)}%`, background: SENTIMENT_COLORS.positive }}
                title={`긍정 ${pct(positive)}`}
              />
              <div
                style={{ width: `${clampPct(neutral)}%`, background: SENTIMENT_COLORS.neutral }}
                title={`중립 ${pct(neutral)}`}
              />
              <div
                style={{ width: `${clampPct(negative)}%`, background: SENTIMENT_COLORS.negative }}
                title={`부정 ${pct(negative)}`}
              />
            </div>
          </div>
        ) : null}
        <p className="mt-4 text-xs leading-relaxed text-ink-500 dark:text-ink-400">
          {negative > 20
            ? "부정 톤 비율이 높습니다 — 평판 리스크 대응 필요."
            : positive >= 50
            ? "브랜드 직접 질문에서 대부분 긍정적으로 소개됩니다."
            : "중립적 설명 위주입니다 — 긍정 시그널(수상·임상·리뷰) 노출을 강화할 여지가 있습니다."}
        </p>
      </Card>

      <Card padding="md">
        <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
          부정 언급이 많은 프롬프트
        </h4>
        {negativeSpotlight.length === 0 ? (
          <p className="mt-3 text-xs text-ink-500 dark:text-ink-400">
            부정 언급이 기록된 프롬프트가 없습니다.
          </p>
        ) : (
          <ul className="mt-3 space-y-2">
            {negativeSpotlight.map((r) => (
              <li
                key={r.prompt_id}
                className="flex items-start justify-between gap-3 border-l-4 border-l-rose-400 rounded-r-md bg-ink-50 px-3 py-2 dark:border-l-rose-500 dark:bg-ink-900/60"
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
                <Pill tone="danger" size="xs">부정 {num(r.negative_count)}</Pill>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function Tone({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-ink-500 dark:text-ink-400">
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums" style={{ color }}>
        {pct(value)}
      </div>
    </div>
  );
}
