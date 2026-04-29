import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-20 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">브랜드를 찾을 수 없습니다</h1>
      <p className="mt-2 text-sm text-ink-500">
        해당 슬러그의 진단 데이터가 없습니다. <code className="rounded bg-ink-100 px-1.5 py-0.5 text-xs">brands/&lt;slug&gt;/results/dashboard/</code> 디렉토리를 확인해주세요.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block rounded-md border border-ink-200 px-4 py-2 text-sm hover:bg-ink-50 dark:border-ink-700 dark:hover:bg-ink-900"
      >
        브랜드 목록으로
      </Link>
    </main>
  );
}
