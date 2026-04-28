"use client";

import { useEffect, useState } from "react";
import { absoluteDate, absoluteTime } from "@/lib/format";

interface PrintMetaProps {
  brandName: string;
  brand: string;
  auditMtime: number;
  totalRows: number;
  position?: "top" | "bottom";
}

const pad2 = (n: number) => (n < 10 ? `0${n}` : String(n));

function formatDateTime(d: Date): string {
  return `${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

function formatDate(d: Date): string {
  return `${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())}`;
}

/**
 * 인쇄/PDF 출력 시에만 보이는 메타 블록.
 * - 감사 실행일 (data freshness)
 * - 리포트 출력일 (오늘, beforeprint 시점에 갱신)
 * - 브랜드 스탬프
 */
export function PrintMeta({
  brandName,
  brand,
  auditMtime,
  totalRows,
  position = "top",
}: PrintMetaProps) {
  const [exportedAt, setExportedAt] = useState<Date | null>(null);

  useEffect(() => {
    setExportedAt(new Date());
    const onBeforePrint = () => setExportedAt(new Date());
    window.addEventListener("beforeprint", onBeforePrint);
    return () => window.removeEventListener("beforeprint", onBeforePrint);
  }, []);

  const exportedLabel = exportedAt ? formatDateTime(exportedAt) : "—";
  const exportedDateOnly = exportedAt ? formatDate(exportedAt) : "—";
  const auditLabel = auditMtime ? absoluteTime(auditMtime) : "—";

  if (position === "bottom") {
    return (
      <div className="print-meta-bottom hidden print:block mt-8 border-t border-ink-300 pt-3 text-[10px] text-ink-500 tabular-nums">
        <div className="flex items-center justify-between">
          <span>{brandName} · GEO 진단 리포트</span>
          <span>
            출력 {exportedDateOnly} · 감사 {auditMtime ? absoluteDate(auditMtime) : "—"}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="print-meta-top hidden print:block mb-6 border-b border-ink-300 pb-4">
      <div className="flex items-baseline justify-between gap-4">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-ink-500">
            GEO 진단 리포트
          </div>
          <div className="mt-1 text-2xl font-semibold tracking-tight text-ink-900">
            {brandName}
          </div>
          <div className="mt-0.5 text-xs text-ink-500">
            슬러그: <span className="font-mono">{brand}</span> · 분석 {totalRows}건
          </div>
        </div>
        <div className="text-right text-[11px] leading-relaxed text-ink-600 tabular-nums">
          <div>
            <span className="text-ink-500">감사 실행일</span>{" "}
            <span className="font-medium text-ink-900">{auditLabel}</span>
          </div>
          <div>
            <span className="text-ink-500">리포트 출력일</span>{" "}
            <span className="font-medium text-ink-900">{exportedLabel}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 헤더에 들어갈 PDF 저장 버튼 (화면 전용, 인쇄 시에는 숨김).
 * - 인쇄 시점에 document.title 을 `{brand}_GEO진단_YYYYMMDD` 로 임시 변경
 *   → 브라우저 PDF 저장 대화창의 기본 파일명에 자동 반영됨.
 */
export function PrintButton({
  brand,
  brandName,
}: {
  brand: string;
  brandName: string;
}) {
  return (
    <button
      type="button"
      onClick={() => {
        const original = document.title;
        const d = new Date();
        const ymd = `${d.getFullYear()}${pad2(d.getMonth() + 1)}${pad2(d.getDate())}`;
        // 한글 + 영문 슬러그 둘 다 포함 — 파일 시스템·이메일 호환
        const safe = (brandName || brand).replace(/[\\/:*?"<>|]/g, "");
        document.title = `${safe}_GEO진단_${ymd}`;
        const restore = () => {
          document.title = original;
          window.removeEventListener("afterprint", restore);
        };
        window.addEventListener("afterprint", restore);
        // afterprint 이벤트가 모든 브라우저에서 항상 발화하지 않으므로 안전망
        setTimeout(() => {
          if (document.title !== original) document.title = original;
        }, 60_000);
        window.print();
      }}
      className="no-print inline-flex items-center gap-1.5 rounded-md border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:border-ink-400 hover:bg-ink-50 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-200 dark:hover:bg-ink-800"
      title="브라우저 인쇄 대화창으로 PDF 저장 (파일명에 오늘 날짜 자동 포함)"
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
        <path d="M3 4V1h6v3M3 9h6v2H3V9z M2 4h8a1 1 0 011 1v3a1 1 0 01-1 1H9V7H3v2H2a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" strokeWidth="1" strokeLinejoin="round" fill="none"/>
      </svg>
      PDF로 저장
    </button>
  );
}

/**
 * 헤더의 "오늘" 날짜 칩 — 클라이언트에서만 렌더 (마운트 후 표시).
 * 모니터링 도구의 핵심 컨텍스트: "지금 보는 기준일"이 언제인지 명확히.
 */
export function TodayLabel() {
  const [today, setToday] = useState<string>("");
  useEffect(() => {
    const d = new Date();
    setToday(`${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())}`);
  }, []);
  if (!today) return null;
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
      <span className="text-ink-500 dark:text-ink-400">오늘</span>
      <span className="font-medium tabular-nums text-ink-900 dark:text-ink-50">
        {today}
      </span>
    </span>
  );
}
