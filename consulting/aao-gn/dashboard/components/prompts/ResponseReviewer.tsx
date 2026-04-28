import { Card } from "@/components/primitives/Card";
import { Pill } from "@/components/primitives/Pill";
import type { PromptRunRow } from "@/lib/data";

// 분류 필드의 Y/N → boolean 정규화 (CSV 값이 문자열로 들어오므로)
function isYes(v?: string | null): boolean {
  return (v ?? "").trim().toUpperCase() === "Y";
}

interface ResponseReviewerProps {
  runs: PromptRunRow[];
  brandName: string;
  competitorNames: string[];
}

// 한 프롬프트의 모든 run을 카드로 나란히 보여준다.
// 각 카드 = AI 응답 본문 + 자동 분류 결과 + 의심 신호(clarification/off_topic).
// 사람이 spot-check 할 때 분류기가 옳은지 빠르게 검증할 수 있도록.
export function ResponseReviewer({
  runs,
  brandName,
  competitorNames,
}: ResponseReviewerProps) {
  if (!runs || runs.length === 0) {
    return (
      <Card padding="md" className="bg-ink-50 dark:bg-ink-900/60">
        <p className="text-sm text-ink-500 dark:text-ink-400">
          이 프롬프트의 응답 데이터가 없습니다.
        </p>
      </Card>
    );
  }

  // 의심 신호 카운트 — 헤더에 노출
  const flags = {
    clarification: runs.filter((r) => isYes(r.parsed?.clarification_request)).length,
    offTopic: runs.filter((r) => isYes(r.parsed?.off_topic)).length,
    evasion: runs.filter((r) => isYes(r.parsed?.evasion)).length,
  };
  const totalFlags = flags.clarification + flags.offTopic + flags.evasion;

  return (
    <Card padding="md">
      <div className="flex items-baseline justify-between gap-2">
        <div>
          <h4 className="text-sm font-semibold text-ink-900 dark:text-ink-50">
            응답별 검토 ({runs.length}건)
          </h4>
          <p className="mt-1 text-xs leading-relaxed text-ink-500 dark:text-ink-400">
            자동 분류기가 매긴 판정을 응답 원문과 함께 표시합니다. 분류 오류
            (예: 추천했는데 “아니오”로 잘못 매김, 되묻기를 “미추천”으로 잘못 셈)를
            spot-check 할 때 사용하세요.
          </p>
        </div>
        {totalFlags > 0 ? (
          <div className="shrink-0 text-right text-[11px] tabular-nums">
            <div className="text-ink-500 dark:text-ink-400">의심 신호</div>
            <div className="mt-0.5 flex flex-wrap gap-1.5">
              {flags.clarification > 0 ? (
                <Pill tone="warn" size="xs">되묻기 {flags.clarification}</Pill>
              ) : null}
              {flags.offTopic > 0 ? (
                <Pill tone="warn" size="xs">Off-topic {flags.offTopic}</Pill>
              ) : null}
              {flags.evasion > 0 ? (
                <Pill tone="muted" size="xs">회피 {flags.evasion}</Pill>
              ) : null}
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-4 space-y-4">
        {runs.map((run) => (
          <RunCard
            key={run.run_number}
            run={run}
            brandName={brandName}
            competitorNames={competitorNames}
          />
        ))}
      </div>
    </Card>
  );
}

function RunCard({
  run,
  brandName,
  competitorNames,
}: {
  run: PromptRunRow;
  brandName: string;
  competitorNames: string[];
}) {
  const p = run.parsed;
  const r = run.raw;
  const text = r?.response ?? "";
  const citations = r?.citations ?? [];

  const verdicts = p
    ? [
        { label: "언급", value: isYes(p.mention_brand), tone: "primary" },
        { label: "추천", value: isYes(p.our_brand_recommended), tone: "primary" },
        { label: "Top1", value: isYes(p.our_brand_top1), tone: "primary" },
        { label: "Top3", value: isYes(p.our_brand_top3), tone: "primary" },
      ]
    : [];

  const flags = p
    ? [
        { code: "되묻기", on: isYes(p.clarification_request) },
        { code: "Off-topic", on: isYes(p.off_topic) },
        { code: "회피", on: isYes(p.evasion) },
      ]
    : [];

  const sentiment = p?.sentiment_to_brand;

  return (
    <div className="overflow-hidden rounded-lg border border-ink-200 dark:border-ink-700">
      {/* 헤더 — 분류 결과 한눈에 */}
      <div className="border-b border-ink-200 bg-ink-50 px-3 py-2 dark:border-ink-700 dark:bg-ink-900/60">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs">
          <span className="font-mono font-medium tabular-nums text-ink-600 dark:text-ink-300">
            run {run.run_number}
          </span>
          <span className="text-ink-300 dark:text-ink-600">|</span>
          <span className="text-ink-500 dark:text-ink-400">자동 분류:</span>
          {verdicts.map((v) => (
            <span
              key={v.label}
              className={`inline-flex items-center gap-1 rounded-sm px-1.5 py-0.5 text-[10px] font-medium tabular-nums ${
                v.value
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200"
                  : "bg-ink-100 text-ink-500 dark:bg-ink-800 dark:text-ink-500"
              }`}
            >
              <span>{v.label}</span>
              <span>{v.value ? "✓" : "✗"}</span>
            </span>
          ))}
          {p?.our_brand_rank !== null && p?.our_brand_rank !== undefined ? (
            <span className="text-[10px] tabular-nums text-ink-600 dark:text-ink-300">
              순위 #{p.our_brand_rank}
            </span>
          ) : null}
          {sentiment ? (
            <Pill
              tone={
                sentiment === "positive"
                  ? "win"
                  : sentiment === "negative"
                  ? "danger"
                  : "muted"
              }
              size="xs"
            >
              {sentiment === "positive"
                ? "긍정"
                : sentiment === "negative"
                ? "부정"
                : sentiment === "neutral"
                ? "중립"
                : sentiment}
            </Pill>
          ) : null}
          {p?.win_loss_draw ? (
            <Pill
              tone={
                p.win_loss_draw === "win"
                  ? "win"
                  : p.win_loss_draw === "loss"
                  ? "loss"
                  : "draw"
              }
              size="xs"
            >
              H2H {p.win_loss_draw}
            </Pill>
          ) : null}
          {p?.surfacing_outcome && p.surfacing_outcome !== "" ? (
            <Pill
              tone={
                p.surfacing_outcome === "surfaced"
                  ? "win"
                  : p.surfacing_outcome === "co_mentioned"
                  ? "warn"
                  : "loss"
              }
              size="xs"
            >
              {p.surfacing_outcome === "surfaced"
                ? "대안 노출"
                : p.surfacing_outcome === "co_mentioned"
                ? "공동 언급"
                : "미노출"}
            </Pill>
          ) : null}
          {flags.some((f) => f.on) ? (
            <span className="ml-auto inline-flex flex-wrap gap-1">
              {flags
                .filter((f) => f.on)
                .map((f) => (
                  <span
                    key={f.code}
                    className="rounded-sm bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-200"
                    title="자동 분류기가 의심스러운 응답으로 표시한 항목"
                  >
                    ⚠ {f.code}
                  </span>
                ))}
            </span>
          ) : null}
        </div>
      </div>

      {/* 응답 본문 */}
      <div className="px-3 py-3">
        {text ? (
          <ResponseBody
            text={text}
            brandName={brandName}
            competitorNames={competitorNames}
          />
        ) : (
          <p className="text-xs text-ink-400 dark:text-ink-500">응답 본문 없음</p>
        )}

        {citations.length > 0 ? (
          <div className="mt-3 border-t border-ink-100 pt-2 text-[11px] text-ink-500 dark:border-ink-800 dark:text-ink-400">
            <span className="font-medium">인용 {citations.length}건:</span>{" "}
            {citations.slice(0, 5).map((c, i) => (
              <span key={i} className="ml-1.5 inline-block">
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                  title={c.url}
                >
                  {c.title || new URL(c.url).hostname}
                </a>
                {i < Math.min(citations.length, 5) - 1 ? "," : ""}
              </span>
            ))}
            {citations.length > 5 ? (
              <span className="ml-1.5">+{citations.length - 5}</span>
            ) : null}
          </div>
        ) : null}

        {/* parser가 추출한 부가 정보 */}
        {p && (p.top1_brand || p.recommended_competitors || p.competitor_mentioned) ? (
          <div className="mt-3 grid grid-cols-1 gap-2 border-t border-ink-100 pt-2 text-[11px] text-ink-500 sm:grid-cols-3 dark:border-ink-800 dark:text-ink-400">
            {p.top1_brand ? (
              <div>
                <span className="text-ink-400 dark:text-ink-500">Top1 브랜드:</span>{" "}
                <span className="text-ink-700 dark:text-ink-200">{p.top1_brand}</span>
              </div>
            ) : null}
            {p.recommended_competitors ? (
              <div>
                <span className="text-ink-400 dark:text-ink-500">추천된 경쟁사:</span>{" "}
                <span className="text-ink-700 dark:text-ink-200">
                  {p.recommended_competitors}
                </span>
              </div>
            ) : null}
            {p.competitor_mentioned ? (
              <div>
                <span className="text-ink-400 dark:text-ink-500">언급된 경쟁사:</span>{" "}
                <span className="text-ink-700 dark:text-ink-200">
                  {p.competitor_mentioned}
                </span>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

// 응답 본문에서 우리 브랜드와 경쟁사명을 강조 (수동 검증 가독성).
function ResponseBody({
  text,
  brandName,
  competitorNames,
}: {
  text: string;
  brandName: string;
  competitorNames: string[];
}) {
  // 길면 접기 — 600자 이상이면 details로 감싼다
  const SOFT_LIMIT = 600;
  const isLong = text.length > SOFT_LIMIT;
  const preview = isLong ? text.slice(0, SOFT_LIMIT) + "…" : text;

  const highlight = (s: string) => {
    if (!s) return s;
    const escaped = (v: string) =>
      v.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    const all = [brandName, ...competitorNames].filter(Boolean);
    if (all.length === 0) return [<span key="0">{s}</span>];
    const re = new RegExp("(" + all.map(escaped).join("|") + ")", "g");
    const parts = s.split(re);
    return parts.map((part, i) => {
      if (part === brandName) {
        return (
          <mark
            key={i}
            className="rounded bg-rose-100 px-0.5 font-medium text-rose-800 dark:bg-rose-900/40 dark:text-rose-200"
          >
            {part}
          </mark>
        );
      }
      if (competitorNames.includes(part)) {
        return (
          <mark
            key={i}
            className="rounded bg-amber-100 px-0.5 font-medium text-amber-900 dark:bg-amber-900/40 dark:text-amber-200"
          >
            {part}
          </mark>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return isLong ? (
    <details className="group">
      <summary className="cursor-pointer text-sm leading-relaxed text-ink-800 dark:text-ink-100 [&::-webkit-details-marker]:hidden">
        <div className="whitespace-pre-wrap">{highlight(preview)}</div>
        <span className="mt-1 inline-block text-[11px] text-accent group-open:hidden">
          전체 보기 ({text.length}자) ▾
        </span>
      </summary>
      <div className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink-800 dark:text-ink-100">
        {highlight(text)}
      </div>
      <span className="mt-1 inline-block text-[11px] text-accent">접기 ▴</span>
    </details>
  ) : (
    <div className="whitespace-pre-wrap text-sm leading-relaxed text-ink-800 dark:text-ink-100">
      {highlight(text)}
    </div>
  );
}
