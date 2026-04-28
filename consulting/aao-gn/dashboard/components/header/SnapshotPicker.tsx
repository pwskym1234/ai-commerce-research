"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import type { Snapshot } from "@/lib/history";
import { absoluteDate } from "@/lib/format";

interface SnapshotPickerProps {
  brand: string;
  history: Snapshot[];
  /** 현재 보고 있는 스냅샷 timestamp ("YYYYMMDD-HHMMSS" 또는 null=최신) */
  current: string | null;
}

function tsKey(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}00`;
}

export function SnapshotPicker({ brand, history, current }: SnapshotPickerProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  if (history.length === 0) return null;

  const sorted = [...history].sort((a, b) =>
    b.timestamp.localeCompare(a.timestamp),
  );
  const latestKey = tsKey(sorted[0].timestamp);
  const currentLabel = current
    ? `${absoluteDate(new Date(sorted.find((s) => tsKey(s.timestamp) === current)?.timestamp || sorted[0].timestamp).getTime())} 시점`
    : "최신 감사";

  return (
    <div className="no-print relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium transition ${
          current
            ? "border-amber-400 bg-amber-50 text-amber-900 hover:bg-amber-100 dark:border-amber-600 dark:bg-amber-900/30 dark:text-amber-200"
            : "border-ink-200 bg-white text-ink-700 hover:bg-ink-50 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-200 dark:hover:bg-ink-800"
        }`}
        title="과거 감사 시점 보기"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
          <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.2" />
          <path d="M6 3v3l2 1.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
        {currentLabel}
        <svg width="8" height="8" viewBox="0 0 8 8" fill="none" aria-hidden>
          <path d="M2 3l2 2 2-2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open ? (
        <div className="absolute right-0 top-full z-40 mt-1 min-w-[220px] overflow-hidden rounded-lg border border-ink-200 bg-white shadow-xl dark:border-ink-700 dark:bg-ink-900">
          <div className="border-b border-ink-100 px-3 py-1.5 text-[10px] font-medium uppercase tracking-wider text-ink-500 dark:border-ink-800 dark:text-ink-400">
            감사 시점 선택
          </div>
          <ul className="max-h-80 overflow-y-auto py-1">
            <li>
              <Link
                href={`/${brand}`}
                onClick={() => setOpen(false)}
                className={`flex items-center justify-between gap-3 px-3 py-2 text-sm transition ${
                  !current
                    ? "bg-ink-100 font-medium text-ink-900 dark:bg-ink-800 dark:text-ink-100"
                    : "text-ink-700 hover:bg-ink-50 dark:text-ink-300 dark:hover:bg-ink-800"
                }`}
              >
                <span>최신 감사</span>
                <span className="text-[10px] text-ink-400 tabular-nums">
                  {absoluteDate(new Date(sorted[0].timestamp).getTime())}
                </span>
              </Link>
            </li>
            <li className="my-1 mx-3 border-t border-ink-100 dark:border-ink-800" />
            {sorted.map((s) => {
              const k = tsKey(s.timestamp);
              const isLatest = k === latestKey;
              const date = absoluteDate(new Date(s.timestamp).getTime());
              const isCurrent = k === current;
              return (
                <li key={k}>
                  <Link
                    href={`/${brand}/history/${k}`}
                    onClick={() => setOpen(false)}
                    className={`flex items-center justify-between gap-3 px-3 py-2 text-sm transition ${
                      isCurrent
                        ? "bg-amber-50 font-medium text-amber-900 dark:bg-amber-900/30 dark:text-amber-200"
                        : "text-ink-700 hover:bg-ink-50 dark:text-ink-300 dark:hover:bg-ink-800"
                    }`}
                  >
                    <span className="tabular-nums">{date}</span>
                    {isLatest ? (
                      <span className="rounded-full bg-ink-100 px-1.5 py-0.5 text-[9px] uppercase tracking-wider text-ink-600 dark:bg-ink-800 dark:text-ink-300">
                        Latest
                      </span>
                    ) : null}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
