import { Card } from "@/components/primitives/Card";
import type { CategoryCard } from "@/types";

export function MeasurementQuality({ cards }: { cards: CategoryCard[] }) {
  const total = cards.reduce((s, c) => s + (c.total_rows || 0), 0);
  const clar = cards.reduce((s, c) => s + (c.clarification_count || 0), 0);
  const off = cards.reduce((s, c) => s + (c.off_topic_count || 0), 0);
  if (total === 0) return null;

  // 유효 응답 = total - clar∪off (중복 가능). category_cards에 effective_denom이 이미 정확히 계산되어 있음.
  const effective = cards.reduce((s, c) => s + (c.effective_denom || 0), 0);
  const noisePct = total > 0 ? Math.round(((total - effective) / total) * 100) : 0;

  if (clar === 0 && off === 0) return null; // 데이터에 보정 정보 없음

  return (
    <Card
      padding="md"
      className="border-l-4 border-l-amber-400 bg-amber-50 dark:border-l-amber-500 dark:bg-amber-900/15"
    >
      <div className="flex flex-wrap items-start gap-x-6 gap-y-2 justify-between">
        <div className="min-w-0">
          <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-200">
            측정 신뢰도 — 응답 {total}건 중 {total - effective}건이 노이즈성 응답
          </h4>
          <p className="mt-1 text-xs leading-relaxed text-amber-800 dark:text-amber-300">
            AI가 답하기 전에 추가 정보를 되묻거나(되묻기), 질문 의도와 다른 답을 한(의도 미스매치) 케이스입니다.
            진짜 미추천이 아니라 측정 노이즈에 가까우므로 분모에서 빼고 본 "보정값"을 각 카드에 함께 표시합니다.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 shrink-0">
          <Stat label="되묻기" value={clar} />
          <Stat label="의도 미스매치" value={off} />
          <Stat label="노이즈 비중" value={`${noisePct}%`} accent />
        </div>
      </div>
    </Card>
  );
}

function Stat({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: number | string;
  accent?: boolean;
}) {
  return (
    <div className="text-right">
      <div className="text-[10px] uppercase tracking-wider text-amber-700 dark:text-amber-400">
        {label}
      </div>
      <div
        className={`mt-0.5 text-lg font-semibold tabular-nums ${
          accent
            ? "text-amber-900 dark:text-amber-200"
            : "text-amber-800 dark:text-amber-300"
        }`}
      >
        {value}
      </div>
    </div>
  );
}
