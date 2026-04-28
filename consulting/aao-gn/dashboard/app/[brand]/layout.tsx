import { ReactNode } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { headers } from "next/headers";
import { loadBrandData } from "@/lib/data";
import { isValidSlug, isValidTimestamp } from "@/lib/paths";
import { BrandHeader } from "@/components/header/BrandHeader";
import { SectionNav } from "@/components/nav/SectionNav";
import { PrintMeta } from "@/components/print/PrintMeta";
import { absoluteDate } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function BrandLayout({
  children,
  modal,
  params,
}: {
  children: ReactNode;
  modal: ReactNode;
  params: { brand: string };
}) {
  if (!isValidSlug(params.brand)) notFound();

  // URL 에서 history snapshot 감지 → /sample/history/<timestamp>
  // middleware.ts 가 x-pathname 헤더로 주입.
  const pathname = headers().get("x-pathname") || "";
  const snapMatch = pathname.match(/\/history\/(\d{8}-\d{6})/);
  const currentSnapshot = snapMatch && isValidTimestamp(snapMatch[1]) ? snapMatch[1] : null;
  // Review 페이지는 자체 사이드바가 있어 SectionNav 숨김 (전체 폭 활용)
  const isReviewPage = pathname.includes(`/${params.brand}/review`);

  const data = await loadBrandData(params.brand, currentSnapshot);
  if (!data) notFound();

  const brandName = data.summary?.brand_name ?? params.brand;
  const totalRows = data.auditMetadata?.total_responses ?? 0;

  return (
    <>
      <BrandHeader
        brand={params.brand}
        brandName={brandName}
        totalRows={totalRows}
        mtime={data.mtime}
        history={[]}
        currentSnapshot={currentSnapshot}
        auditMetadata={data.auditMetadata}
      />
      {currentSnapshot ? (
        <SnapshotBanner brand={params.brand} timestamp={currentSnapshot} />
      ) : null}
      <main
        className={
          isReviewPage
            ? "mx-auto max-w-[1600px] px-4 py-4 print:max-w-none print:px-0 print:py-0"
            : "mx-auto max-w-6xl px-6 py-8 print:max-w-none print:px-0 print:py-0"
        }
      >
        {isReviewPage ? (
          children
        ) : (
          <>
            <PrintMeta
              brand={params.brand}
              brandName={brandName}
              auditMtime={data.mtime}
              totalRows={totalRows}
              position="top"
            />
            <div className="grid grid-cols-12 gap-8 print:block">
              <aside className="col-span-12 lg:col-span-2 print:hidden">
                <SectionNav />
              </aside>
              <div className="col-span-12 space-y-12 lg:col-span-10 print:space-y-8">{children}</div>
            </div>
            <PrintMeta
              brand={params.brand}
              brandName={brandName}
              auditMtime={data.mtime}
              totalRows={totalRows}
              position="bottom"
            />
          </>
        )}
      </main>
      {modal}
    </>
  );
}

function SnapshotBanner({ brand, timestamp }: { brand: string; timestamp: string }) {
  // timestamp = "YYYYMMDD-HHMMSS"
  const y = timestamp.slice(0, 4);
  const m = timestamp.slice(4, 6);
  const d = timestamp.slice(6, 8);
  const date = `${y}.${m}.${d}`;
  return (
    <div className="no-print sticky top-0 z-30 border-b border-amber-300 bg-amber-50 px-6 py-2.5 text-sm text-amber-900 shadow-sm dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-200">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden>
            <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.5" />
            <path d="M7 4v3l2 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <span>
            <strong className="font-semibold">{date}</strong> 시점 스냅샷을 보고 있습니다 — 이때의 데이터로 진단 리포트가 재현됩니다.
          </span>
        </div>
        <Link
          href={`/${brand}`}
          className="inline-flex items-center gap-1 rounded-md border border-amber-400 bg-white/60 px-2.5 py-1 text-xs font-medium hover:bg-white dark:border-amber-600 dark:bg-amber-900/20 dark:hover:bg-amber-900/40"
        >
          최신 데이터로 돌아가기 →
        </Link>
      </div>
    </div>
  );
}
