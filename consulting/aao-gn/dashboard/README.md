# GEO 진단 대시보드

`new/` 의 5단계 Python 파이프라인이 떨어뜨리는 `brands/<slug>/results/dashboard/` 출력(6개 파일)을 그대로 읽어 단일 브랜드 진단 리포트를 보여주는 Next.js 대시보드.

## 빠른 시작

```bash
npm install
npm run seed   # 샘플 브랜드(바디닥터) 시드 데이터 생성
npm run dev    # http://localhost:3000
```

샘플 데이터는 `dashboard/brands/sample/results/dashboard/` 에 6개 파일로 커밋되어 있어 `npm run seed` 없이 바로 실행 가능.

## 실데이터 연결

파이썬 파이프라인이 떨어뜨린 디렉토리를 다음 위치 중 하나로 두면 자동 감지:

1. `dashboard/brands/<slug>/results/dashboard/`
2. `aao_gn/brands/<slug>/results/dashboard/` (대시보드 상위)
3. 환경 변수 `GEO_BRANDS_DIR` 로 지정한 디렉토리

각 위치에 `<slug>/results/dashboard/` 하위 6파일(overview/by_prompt_type/by_target_competitor/by_prompt/by_sentiment.csv + summary.json)이 있으면 `/<slug>` 라우트로 접근.

## 구조

- `app/[brand]/page.tsx` — 단일 페이지 진단 리포트 (Server Component, 6개 로더 병렬)
- `app/[brand]/@modal/(.)prompts/[promptId]/` — intercepted 모달 드로어 (URL shareable)
- `app/[brand]/prompts/[promptId]/` — 풀페이지 폴백
- `lib/csv.ts` — papaparse + zod 검증
- `lib/derive/callouts.ts` — 결정론적 한국어 자동 진단 규칙
- `components/` — 섹션별 컴포넌트 (KPI/콜아웃/경쟁사 매트릭스/감성/근거/프롬프트 테이블)

## 디자인

Linear/Vercel 톤 (모노톤 + accent #FF5C00, 하이라인 보더, 큰 숫자, `tabular-nums`).
Pretendard 폰트, 한국어 코피, 라이트/다크 모드 (`prefers-color-scheme`), 인쇄 스타일시트 포함.
