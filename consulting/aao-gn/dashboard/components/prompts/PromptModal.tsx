"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";

export function PromptModal({
  brand,
  children,
}: {
  brand: string;
  children: ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") router.back();
    }
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [router]);

  return (
    <div
      className="no-print fixed inset-0 z-50 flex items-stretch justify-end bg-ink-900/40 backdrop-blur-sm"
      onClick={() => router.back()}
    >
      <div
        className="relative h-full w-full max-w-xl overflow-y-auto border-l border-ink-200 bg-white shadow-2xl dark:border-ink-800 dark:bg-ink-950"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-ink-200 bg-white/90 px-5 py-3 backdrop-blur dark:border-ink-800 dark:bg-ink-950/90">
          <div className="text-xs font-medium uppercase tracking-wider text-ink-500 dark:text-ink-400">
            프롬프트 상세
          </div>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md p-1 text-ink-500 hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800"
            aria-label="닫기"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
        <div className="px-5 py-5">{children}</div>
      </div>
    </div>
  );
}
