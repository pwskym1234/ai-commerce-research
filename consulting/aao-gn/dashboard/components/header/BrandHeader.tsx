import Link from "next/link";
import { Pill } from "@/components/primitives/Pill";
import { absoluteDate, absoluteTime, num, relativeTime } from "@/lib/format";
import { listBrands } from "@/lib/brands";
import { PrintButton, TodayLabel } from "@/components/print/PrintMeta";
import { SnapshotPicker } from "@/components/header/SnapshotPicker";
import type { Snapshot } from "@/lib/history";
import type { AuditMetadata } from "@/types";

interface BrandHeaderProps {
  brand: string;
  brandName: string;
  totalRows: number;
  mtime: number;
  history?: Snapshot[];
  currentSnapshot?: string | null;
  auditMetadata?: AuditMetadata | null;
}

export async function BrandHeader({
  brand,
  brandName,
  totalRows,
  mtime,
  history = [],
  currentSnapshot = null,
  auditMetadata = null,
}: BrandHeaderProps) {
  const brands = await listBrands();
  const meta = auditMetadata;
  const seedRange =
    meta && meta.seed_min !== null && meta.seed_max !== null
      ? meta.seed_min === meta.seed_max
        ? `${meta.seed_min}`
        : `${meta.seed_min} ~ ${meta.seed_max}`
      : null;
  const totalCalls =
    meta && meta.total_calls
      ? meta.total_calls
      : meta && meta.total_prompts && meta.repeat_count
      ? meta.total_prompts * meta.repeat_count
      : null;
  const rawHref = currentSnapshot
    ? `/${brand}/raw?snapshot=${currentSnapshot}`
    : `/${brand}/raw`;

  return (
    <header className="border-b border-ink-200 bg-white/80 backdrop-blur-md dark:border-ink-800 dark:bg-ink-950/60">
      <div className="mx-auto max-w-6xl px-6 py-6">
        <Pill tone="accent" size="xs">GEO 진단 리포트</Pill>
        <div className="mt-2 flex items-center justify-between gap-4">
          <h1 className="text-3xl font-semibold tracking-tight text-ink-900 dark:text-ink-50">
            {brandName || brand}
          </h1>
          <div className="flex items-center gap-3">
            {brands.length > 1 ? (
              <nav className="no-print flex items-center gap-1.5 text-sm">
                {brands.map((b) => (
                  <Link
                    key={b}
                    href={`/${b}`}
                    className={`rounded-md px-2.5 py-1 transition ${
                      b === brand
                        ? "bg-ink-900 text-white dark:bg-ink-100 dark:text-ink-900"
                        : "text-ink-600 hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800"
                    }`}
                  >
                    {b}
                  </Link>
                ))}
              </nav>
            ) : null}
            <SnapshotPicker brand={brand} history={history} current={currentSnapshot} />
            <PrintButton brand={brand} brandName={brandName || brand} />
          </div>
        </div>
        <div>
          <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">
            총 <span className="tabular-nums font-medium text-ink-700 dark:text-ink-200">{num(totalRows)}</span>건의
            AI 응답을 분석했습니다.
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-xs">
            <DateBadge
              label="감사 실행일"
              value={absoluteDate(mtime)}
              hint={mtime ? `${absoluteTime(mtime).split(" ")[1]} · ${relativeTime(mtime)}` : ""}
              tone="muted"
            />
            <TodayLabel />
          </div>
          {meta ? (
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-ink-100 pt-2 text-[11px] text-ink-500 dark:border-ink-800 dark:text-ink-400">
              {meta.model ? <MetaItem label="모델" value={meta.model} /> : null}
              <MetaItem
                label="Temperature"
                value={meta.temperature === null ? "기본값" : String(meta.temperature)}
              />
              {seedRange ? <MetaItem label="Seed" value={seedRange} /> : null}
              {meta.repeat_count ? (
                <MetaItem label="반복" value={`n=${meta.repeat_count}`} />
              ) : null}
              {totalCalls ? (
                <MetaItem label="총 호출" value={num(totalCalls)} />
              ) : null}
              {meta.total_tokens ? (
                <MetaItem label="총 토큰" value={num(meta.total_tokens)} />
              ) : null}
              {meta.error_count ? (
                <MetaItem label="에러" value={num(meta.error_count)} />
              ) : null}
              <Link
                href={`/${brand}/review`}
                className="no-print ml-auto inline-flex items-center gap-1 rounded-md border border-ink-200 px-2 py-0.5 font-medium text-ink-700 transition hover:bg-ink-100 dark:border-ink-700 dark:text-ink-200 dark:hover:bg-ink-800"
                title="모든 프롬프트와 응답을 사이드바로 빠르게 훑으며 분류 검증"
              >
                응답 검토
              </Link>
              <Link
                href={`/${brand}/method`}
                className="no-print inline-flex items-center gap-1 rounded-md border border-ink-200 px-2 py-0.5 font-medium text-ink-700 transition hover:bg-ink-100 dark:border-ink-700 dark:text-ink-200 dark:hover:bg-ink-800"
                title="사용 중인 분류기 모델·시스템 프롬프트·알려진 편향 공개"
              >
                분석 방법
              </Link>
              <a
                href={rawHref}
                className="no-print inline-flex items-center gap-1 rounded-md border border-ink-200 px-2 py-0.5 font-medium text-ink-700 transition hover:bg-ink-100 dark:border-ink-700 dark:text-ink-200 dark:hover:bg-ink-800"
                title="raw_responses.jsonl 다운로드 (외부 검증·재분석용)"
              >
                Raw JSONL ↓
              </a>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span>{label}</span>
      <span className="font-medium tabular-nums text-ink-800 dark:text-ink-100">{value}</span>
    </span>
  );
}

function DateBadge({
  label,
  value,
  hint,
  tone = "muted",
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: "muted" | "accent";
}) {
  const dot =
    tone === "accent" ? "bg-accent" : "bg-ink-400 dark:bg-ink-500";
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} aria-hidden />
      <span className="text-ink-500 dark:text-ink-400">{label}</span>
      <span className="font-medium tabular-nums text-ink-900 dark:text-ink-50">
        {value}
      </span>
      {hint ? (
        <span className="text-ink-400 dark:text-ink-500 tabular-nums">· {hint}</span>
      ) : null}
    </span>
  );
}
