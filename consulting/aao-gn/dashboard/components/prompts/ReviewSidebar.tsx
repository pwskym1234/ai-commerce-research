"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { ByPrompt } from "@/types";

const CATEGORY_LABELS: Record<string, string> = {
  NEUTRAL: "중립",
  BRAND_ONLY: "브랜드",
  COMP_ONLY: "경쟁사",
  H2H: "비교",
};

const CATEGORY_ORDER = ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"];

interface Props {
  brand: string;
  prompts: ByPrompt[];
  selectedId: string | null;
}

// 사이드바 — 모든 프롬프트를 리스트로, 클릭하면 ?id= 로 이동.
// 필터: 카테고리, 의심 신호, 텍스트 검색.
export function ReviewSidebar({ brand, prompts, selectedId }: Props) {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<string>("ALL");
  const [flag, setFlag] = useState<"ALL" | "FLAGGED" | "MENTIONED" | "NOT_MENTIONED">(
    "ALL",
  );

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return prompts
      .filter((p) => (cat === "ALL" ? true : p.category_code === cat))
      .filter((p) => {
        if (flag === "ALL") return true;
        if (flag === "MENTIONED") return p.mention_count > 0;
        if (flag === "NOT_MENTIONED") return p.mention_count === 0;
        if (flag === "FLAGGED")
          return (
            (p.clarification_count ?? 0) > 0 ||
            (p.off_topic_count ?? 0) > 0 ||
            (p.evasion_count ?? 0) > 0
          );
        return true;
      })
      .filter((p) =>
        ql === ""
          ? true
          : p.prompt_id.toLowerCase().includes(ql) ||
            (p.prompt_text || "").toLowerCase().includes(ql) ||
            (p.target_competitor || "").toLowerCase().includes(ql),
      );
  }, [prompts, q, cat, flag]);

  // 카테고리 순 그룹핑
  const grouped = useMemo(() => {
    const g: Record<string, ByPrompt[]> = {};
    for (const code of CATEGORY_ORDER) g[code] = [];
    for (const p of filtered) {
      const code = p.category_code in g ? p.category_code : "NEUTRAL";
      g[code].push(p);
    }
    return g;
  }, [filtered]);

  return (
    <aside className="flex h-full flex-col">
      {/* 필터 영역 */}
      <div className="border-b border-ink-200 bg-white p-3 dark:border-ink-800 dark:bg-ink-950">
        <input
          type="text"
          placeholder="프롬프트 검색…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="w-full rounded-md border border-ink-200 bg-white px-2.5 py-1.5 text-xs text-ink-900 placeholder:text-ink-400 focus:border-accent focus:outline-none dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
        />
        <div className="mt-2 flex flex-wrap gap-1">
          {[
            { v: "ALL", l: "전체" },
            { v: "NEUTRAL", l: "중립" },
            { v: "BRAND_ONLY", l: "브랜드" },
            { v: "COMP_ONLY", l: "경쟁사" },
            { v: "H2H", l: "비교" },
          ].map(({ v, l }) => (
            <button
              key={v}
              onClick={() => setCat(v)}
              className={`rounded-sm px-2 py-0.5 text-[10px] font-medium ${
                cat === v
                  ? "bg-ink-900 text-white dark:bg-ink-100 dark:text-ink-900"
                  : "bg-ink-100 text-ink-600 hover:bg-ink-200 dark:bg-ink-800 dark:text-ink-300 dark:hover:bg-ink-700"
              }`}
            >
              {l}
            </button>
          ))}
        </div>
        <div className="mt-1.5 flex flex-wrap gap-1">
          {[
            { v: "ALL", l: "전체" },
            { v: "MENTIONED", l: "✓ 언급됨" },
            { v: "NOT_MENTIONED", l: "✗ 미언급" },
            { v: "FLAGGED", l: "⚠ 의심신호" },
          ].map(({ v, l }) => (
            <button
              key={v}
              onClick={() => setFlag(v as typeof flag)}
              className={`rounded-sm px-2 py-0.5 text-[10px] font-medium ${
                flag === v
                  ? "bg-accent text-white"
                  : "bg-ink-100 text-ink-600 hover:bg-ink-200 dark:bg-ink-800 dark:text-ink-300 dark:hover:bg-ink-700"
              }`}
            >
              {l}
            </button>
          ))}
        </div>
        <div className="mt-2 text-[10px] tabular-nums text-ink-500 dark:text-ink-400">
          {filtered.length} / {prompts.length} 프롬프트
        </div>
      </div>

      {/* 리스트 */}
      <div className="flex-1 overflow-y-auto">
        {CATEGORY_ORDER.map((code) => {
          const items = grouped[code];
          if (!items || items.length === 0) return null;
          return (
            <div key={code}>
              <div className="sticky top-0 z-10 border-b border-ink-200 bg-ink-50 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-ink-500 dark:border-ink-800 dark:bg-ink-900/80 dark:text-ink-400">
                {CATEGORY_LABELS[code]} ({items.length})
              </div>
              <ul className="divide-y divide-ink-100 dark:divide-ink-800">
                {items.map((p) => (
                  <PromptItem
                    key={p.prompt_id}
                    brand={brand}
                    p={p}
                    selected={p.prompt_id === selectedId}
                  />
                ))}
              </ul>
            </div>
          );
        })}
        {filtered.length === 0 ? (
          <div className="p-6 text-center text-xs text-ink-500 dark:text-ink-400">
            조건에 맞는 프롬프트 없음
          </div>
        ) : null}
      </div>
    </aside>
  );
}

function PromptItem({
  brand,
  p,
  selected,
}: {
  brand: string;
  p: ByPrompt;
  selected: boolean;
}) {
  const flagged =
    (p.clarification_count ?? 0) > 0 ||
    (p.off_topic_count ?? 0) > 0 ||
    (p.evasion_count ?? 0) > 0;
  const mentioned = p.mention_count > 0;

  return (
    <li>
      <Link
        href={`/${brand}/review?id=${p.prompt_id}`}
        scroll={false}
        className={`block px-3 py-2 transition ${
          selected
            ? "bg-accent-soft dark:bg-accent/15"
            : "hover:bg-ink-50 dark:hover:bg-ink-900/60"
        }`}
      >
        <div className="flex items-start gap-2">
          {/* 좌측 상태 점 */}
          <div className="mt-0.5 flex flex-col items-center gap-1 pt-0.5">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                mentioned ? "bg-emerald-500" : "bg-ink-300 dark:bg-ink-600"
              }`}
              title={mentioned ? "우리 브랜드 언급됨" : "미언급"}
            />
            {flagged ? (
              <span
                className="h-1.5 w-1.5 rounded-full bg-amber-500"
                title="의심 신호 (되묻기/Off-topic/회피)"
              />
            ) : null}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono tabular-nums text-ink-500 dark:text-ink-400">
              <span>{p.prompt_id}</span>
              {p.subcategory ? (
                <span className="rounded-sm bg-ink-100 px-1 dark:bg-ink-800">
                  {p.subcategory}
                </span>
              ) : null}
              <span className="ml-auto tabular-nums">
                {p.mention_count}/{p.runs}
              </span>
            </div>
            <div
              className={`mt-0.5 truncate text-xs leading-snug ${
                selected
                  ? "text-ink-900 dark:text-ink-50 font-medium"
                  : "text-ink-700 dark:text-ink-200"
              }`}
            >
              {p.prompt_text || "(no text)"}
            </div>
            {p.target_competitor ? (
              <div className="mt-0.5 truncate text-[10px] text-ink-400 dark:text-ink-500">
                vs {p.target_competitor}
              </div>
            ) : null}
          </div>
        </div>
      </Link>
    </li>
  );
}
