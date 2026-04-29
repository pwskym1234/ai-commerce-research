"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { CATEGORY_LABELS, CATEGORY_ORDER } from "@/lib/constants";
import { MetricBar } from "@/components/primitives/MetricBar";
import { Pill } from "@/components/primitives/Pill";
import { num } from "@/lib/format";
import type { ByPrompt } from "@/types";

type SortKey =
  | "prompt_id"
  | "recommendation_rate"
  | "mention_rate"
  | "negative_count";

export function PromptTable({ brand, rows }: { brand: string; rows: ByPrompt[] }) {
  const [category, setCategory] = useState<string>("ALL");
  const [competitor, setCompetitor] = useState<string>("ALL");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("recommendation_rate");
  const [asc, setAsc] = useState(false);

  const competitors = useMemo(() => {
    const set = new Set<string>();
    for (const r of rows) if (r.target_competitor) set.add(r.target_competitor);
    return Array.from(set).sort();
  }, [rows]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    for (const r of rows) set.add(r.category_code);
    return (CATEGORY_ORDER as readonly string[]).filter((c) => set.has(c));
  }, [rows]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((r) => category === "ALL" || r.category_code === category)
      .filter((r) => competitor === "ALL" || r.target_competitor === competitor)
      .filter((r) =>
        q === ""
          ? true
          : r.prompt_id.toLowerCase().includes(q) ||
            (r.prompt_text || "").toLowerCase().includes(q) ||
            (r.sample_response_preview || "").toLowerCase().includes(q),
      )
      .sort((a, b) => {
        const av = a[sort] as unknown as number | string;
        const bv = b[sort] as unknown as number | string;
        if (typeof av === "string" && typeof bv === "string") {
          return asc ? av.localeCompare(bv) : bv.localeCompare(av);
        }
        const an = Number(av);
        const bn = Number(bv);
        return asc ? an - bn : bn - an;
      });
  }, [rows, category, competitor, query, sort, asc]);

  function toggleSort(key: SortKey) {
    if (sort === key) setAsc(!asc);
    else {
      setSort(key);
      setAsc(false);
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-ink-200 dark:border-ink-800">
      <div className="flex flex-wrap items-center gap-2 border-b border-ink-200 bg-ink-50 px-4 py-3 dark:border-ink-800 dark:bg-ink-900/60">
        <FilterChip active={category === "ALL"} onClick={() => setCategory("ALL")}>
          전체
        </FilterChip>
        {categories.map((c) => (
          <FilterChip key={c} active={category === c} onClick={() => setCategory(c)}>
            {CATEGORY_LABELS[c] || c}
          </FilterChip>
        ))}
        {competitors.length > 0 ? (
          <select
            value={competitor}
            onChange={(e) => setCompetitor(e.target.value)}
            className="ml-auto rounded-md border border-ink-200 bg-white px-2 py-1 text-xs dark:border-ink-700 dark:bg-ink-900"
          >
            <option value="ALL">경쟁사 전체</option>
            {competitors.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        ) : null}
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="prompt_id · 질문문 · 응답 검색"
          className="w-56 rounded-md border border-ink-200 bg-white px-2 py-1 text-xs placeholder:text-ink-400 dark:border-ink-700 dark:bg-ink-900"
        />
      </div>
      <div className="max-h-[640px] overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10 bg-ink-50 text-xs uppercase tracking-wider text-ink-500 dark:bg-ink-900 dark:text-ink-400">
            <tr>
              <SortableTh active={sort === "prompt_id"} asc={asc} onClick={() => toggleSort("prompt_id")}>
                Prompt
              </SortableTh>
              <th className="px-3 py-2 text-left font-medium">카테고리</th>
              <th className="px-3 py-2 text-left font-medium">질문문</th>
              <SortableTh active={sort === "mention_rate"} asc={asc} onClick={() => toggleSort("mention_rate")} align="right">
                언급률
              </SortableTh>
              <SortableTh active={sort === "recommendation_rate"} asc={asc} onClick={() => toggleSort("recommendation_rate")} align="right">
                추천률
              </SortableTh>
              <SortableTh active={sort === "negative_count"} asc={asc} onClick={() => toggleSort("negative_count")} align="right">
                부정
              </SortableTh>
              <th className="px-3 py-2 text-right font-medium">상세</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-200 dark:divide-ink-800">
            {filtered.map((r) => (
              <tr key={r.prompt_id} className="bg-white hover:bg-ink-50 dark:bg-ink-900/40 dark:hover:bg-ink-900/80">
                <td className="px-3 py-2 font-mono text-xs tabular-nums text-ink-700 dark:text-ink-200">
                  <Link href={`/${brand}/prompts/${r.prompt_id}`} className="hover:text-accent">
                    {r.prompt_id}
                  </Link>
                </td>
                <td className="px-3 py-2">
                  <Pill tone="muted" size="xs">
                    {CATEGORY_LABELS[r.category_code] || r.category_code}
                  </Pill>
                  {r.subcategory ? (
                    <span
                      className="ml-1 rounded-sm bg-ink-100 px-1 text-[10px] font-medium tabular-nums text-ink-600 dark:bg-ink-800 dark:text-ink-300"
                      title={`서브분류: ${r.subcategory}`}
                    >
                      {r.subcategory}
                    </span>
                  ) : null}
                  {r.target_competitor ? (
                    <span className="ml-1 text-[11px] text-ink-500 dark:text-ink-400">vs {r.target_competitor}</span>
                  ) : null}
                </td>
                <td className="px-3 py-2 text-sm text-ink-700 dark:text-ink-200 max-w-md truncate" title={r.prompt_text}>
                  {r.prompt_text || "—"}
                </td>
                <td className="px-3 py-2">
                  <div className="w-24">
                    <MetricBar
                      value={r.mention_rate}
                      successes={r.mention_count}
                      n={r.runs}
                      showLabel
                    />
                  </div>
                </td>
                <td className="px-3 py-2">
                  <div className="w-24">
                    <MetricBar
                      value={r.recommendation_rate}
                      successes={r.recommendation_count}
                      n={r.runs}
                      showLabel
                    />
                  </div>
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {r.negative_count > 0 ? (
                    <span className="text-rose-600 dark:text-rose-400">{r.negative_count}</span>
                  ) : (
                    <span className="text-ink-400 dark:text-ink-500">0</span>
                  )}
                </td>
                <td className="px-3 py-2 text-right">
                  <Link
                    href={`/${brand}/prompts/${r.prompt_id}`}
                    className="text-xs font-medium text-accent hover:underline"
                  >
                    보기 →
                  </Link>
                </td>
              </tr>
            ))}
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-3 py-12 text-center text-sm text-ink-500 dark:text-ink-400">
                  조건에 맞는 프롬프트가 없습니다.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="border-t border-ink-200 bg-ink-50 px-4 py-2 text-[11px] text-ink-500 dark:border-ink-800 dark:bg-ink-900/60 dark:text-ink-400 tabular-nums">
        총 {num(filtered.length)} / {num(rows.length)}건 노출 중
      </div>
    </div>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-2.5 py-1 text-xs transition ${
        active
          ? "bg-ink-900 text-white dark:bg-ink-100 dark:text-ink-900"
          : "bg-white text-ink-600 hover:bg-ink-100 dark:bg-ink-900 dark:text-ink-300 dark:hover:bg-ink-800"
      }`}
    >
      {children}
    </button>
  );
}

function SortableTh({
  active,
  asc,
  onClick,
  align = "left",
  children,
}: {
  active: boolean;
  asc: boolean;
  onClick: () => void;
  align?: "left" | "right";
  children: React.ReactNode;
}) {
  return (
    <th className={`px-3 py-2 text-${align} font-medium`}>
      <button
        type="button"
        onClick={onClick}
        className={`inline-flex items-center gap-1 ${active ? "text-ink-900 dark:text-ink-100" : ""}`}
      >
        {children}
        {active ? <span className="text-[8px]">{asc ? "▲" : "▼"}</span> : null}
      </button>
    </th>
  );
}
