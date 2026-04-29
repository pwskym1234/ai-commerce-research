import Link from "next/link";
import { redirect } from "next/navigation";
import { listBrands } from "@/lib/brands";

export const dynamic = "force-dynamic";

export default async function Home() {
  const brands = await listBrands();
  if (brands.length === 1) {
    redirect(`/${brands[0]}`);
  }
  if (brands.length === 0) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-20">
        <h1 className="text-2xl font-semibold tracking-tight">GEO 진단 리포트</h1>
        <p className="mt-2 text-sm text-ink-500">
          분석할 브랜드 데이터가 없습니다. <code className="rounded bg-ink-100 px-1.5 py-0.5 text-xs">brands/&lt;slug&gt;/results/dashboard/</code> 에 6개 파일을 배치하거나 <code className="rounded bg-ink-100 px-1.5 py-0.5 text-xs">npm run seed</code>로 샘플을 생성하세요.
        </p>
      </main>
    );
  }
  return (
    <main className="mx-auto max-w-3xl px-6 py-20">
      <h1 className="text-2xl font-semibold tracking-tight">GEO 진단 리포트</h1>
      <p className="mt-2 text-sm text-ink-500">분석할 브랜드를 선택하세요.</p>
      <ul className="mt-8 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {brands.map((b) => (
          <li key={b}>
            <Link
              href={`/${b}`}
              className="block rounded-xl border border-ink-200 px-5 py-4 transition hover:border-ink-400 dark:border-ink-800 dark:hover:border-ink-600"
            >
              <div className="text-sm font-medium text-ink-900 dark:text-ink-50">{b}</div>
              <div className="mt-1 text-xs text-ink-500 dark:text-ink-400">진단 리포트 보기 →</div>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
