# aao-gn — GEO 감사 파이프라인 & 대시보드

AI 답변(예: ChatGPT, gpt-4o-search-preview) 기준으로 브랜드의 **생성형 엔진 최적화(GEO) 노출·추천 상태를 감사**하고, 담당자가 3분 안에 읽는 **보고용 대시보드**로 시각화하는 도구.

## 구조

```
pipeline/                           # Python 파이프라인 (5단계)
  02_generate_prompts.py            # 150개 프롬프트 생성 (4카테고리)
  03_run_audit.py                   # gpt-4o-search-preview 로 AI 응답 수집 (×2회)
  04_parse_responses.py             # Claude 로 응답 파싱 → parsed_results.csv
  05_aggregate_dashboard.py         # 카테고리 카드 / H2H / COMP_ONLY / diagnostics 집계
  06_neutral_brand_ranking.py       # NEUTRAL 응답 속 경쟁 브랜드 자동 추출 & 랭킹
  config.py                         # API 키 (gitignore됨, config.sample.py 참고)
  config.sample.py                  # 키 빈 샘플 — 신규 셋업 시 복사
  tools/
    score_prompts.py                # 프롬프트 품질 채점 (A/B 비교)
    spot_check_neutral.py           # NEUTRAL 응답 스팟체크 진단

brands/<slug>/                      # 브랜드별 작업 디렉토리
  brand_config.json                 # 브랜드명·경쟁사·카테고리 타깃
  prompts.csv                       # 02 출력 — 150 프롬프트
  results/
    raw_responses.json              # 03 출력 — AI 원문 응답
    parsed_results.csv              # 04 출력 — 구조화된 판정
    audit_metadata.json             # 감사 실행 메타
    classifier_spec.json            # 04 분류기 사양 (감사 투명성)
    dashboard/                      # 05/06 출력 — 대시보드 원본 데이터
      category_cards.csv
      neutral_by_subcategory.csv
      h2h_by_competitor.csv
      comp_only_by_competitor.csv
      by_prompt.csv
      by_prompt_type.csv
      summary.json
      neutral_brand_ranking.json    # 06 출력

dashboard/                          # Next.js 14 (app router) 보고용 UI
  app/[brand]/                      # /brand 라우트 (단일 스크롤, 섹션 앵커)
  components/
    core/                           # CoreCards · AutoDiagnosis · ActionItems
    category/                       # NeutralDetail · BrandOnlyDetail · CompOnlyDetail · H2HDetail · NeutralBrandRankingTable
    prompts/                        # PromptTable · PromptDetail · ResponseReviewer
  lib/
    data.ts                         # CSV/JSON 로더 + zod 검증
    paths.ts                        # 브랜드 디렉토리 탐색 (GEO_BRANDS_DIR / ./brands / ../brands)
    constants.ts                    # 한글 라벨 매핑 (LABELS / SECTIONS)

archive/                            # 과거 스냅샷 (활성 흐름 아님)
  evals/                            # 프롬프트 품질 평가 기록
  pilots/                           # v2/v2.1 파일럿 런
  backups/                          # 구버전 prompts.csv·results 보관

docs/                               # 설계 노트 & 변경 이력
  parse_logic_alignment.md          # 02 의도 ↔ 04 파싱 정합성 가이드
  CHANGES_2026-04-25.md             # 측정 신뢰도·리뷰 UI 추가 변경기
```

## 카테고리 구조

| code | 한글 | 수량 | 의미 |
|---|---|---|---|
| NEUTRAL | 중립 질문 | 75 | 브랜드를 모르는 상태의 카테고리·상황·고민 질문 |
| BRAND_ONLY | 브랜드 직접 질문 | 15 | 우리 브랜드명을 직접 지목 |
| COMP_ONLY | 경쟁사 대안 질문 | 30 | 경쟁사 이름을 지목, 대안을 물음 |
| H2H | 직접 비교 | 30 | 우리 브랜드 vs 특정 경쟁사 |

## 실행 순서

### 1회성 설정
```bash
# pipeline/config.sample.py 를 복사해 키 채우기
cp pipeline/config.sample.py pipeline/config.py
# pipeline/config.py 안의 OPENAI_API_KEY, ANTHROPIC_API_KEY 채우기
```

### 새 브랜드 감사
```bash
# 0) brands/<slug>/brand_config.json 작성
# 1) 프롬프트 생성
python3 pipeline/02_generate_prompts.py --brand brands/<slug>/brand_config.json
# 2) 육안 검수 후 감사 실행 (약 150×2=300 호출, 20~40분)
python3 pipeline/03_run_audit.py --brand brands/<slug>/brand_config.json
# 3) 파싱 (Claude 호출)
python3 pipeline/04_parse_responses.py --brand brands/<slug>/brand_config.json
# 4) 대시보드 집계
python3 pipeline/05_aggregate_dashboard.py --brand brands/<slug>/brand_config.json
# 5) NEUTRAL 브랜드 랭킹
python3 pipeline/06_neutral_brand_ranking.py --brand brands/<slug>/brand_config.json
```

### 대시보드
```bash
cd dashboard
npm install
GEO_BRANDS_DIR=$(pwd)/../brands npm run dev
# http://localhost:3000
```

> 빌드/배포 시 `npm run sync-brands` 가 `../brands/` 를 `dashboard/brands/` 로 rsync 합니다 (Vercel 환경 대응). `dashboard/brands/` 는 산출물이라 git에는 포함되지 않습니다.

### 보조 도구
```bash
# 프롬프트 v2.1 vs baseline 채점 비교
python3 pipeline/tools/score_prompts.py --csv brands/<slug>/prompts.csv --label v2.1

# NEUTRAL 응답이 0% 인 프롬프트의 스팟 체크
python3 pipeline/tools/spot_check_neutral.py
```

## 대시보드 섹션

1. **핵심 진단** — 4카테고리 카드 (중립 등장력 · 브랜드 직접 톤 · 경쟁사 대안 침투력 · 직접 비교 승률)
2. **자동 해석** — 05 에서 규칙 기반으로 생성한 3줄 진단
3. **중립 질문 성과** — 언급/추천률 + **경쟁 브랜드 점유율 랭킹 (우리 몇 위)** + 강/약점 프롬프트
4. **브랜드 직접 질문** — 긍/중/부 감성 분포 + 부정 프롬프트
5. **경쟁사 대안 질문** — 경쟁사별 소환/공동언급/미노출 테이블
6. **직접 비교 성과** — 경쟁사별 W/L/D 테이블 + 승리/패배 top 3
7. **우선 개선 과제** — 문제 / 원인 가설 / 바로 할 일
8. **참고 자료** — 전체 프롬프트 테이블 (접힘)

## 주요 설계 결정

- 파이프라인과 대시보드 분리 — 파이프라인은 CSV/JSON만 쓰고, 대시보드는 그걸 읽기만 함
- 파서(04)는 원재료 저장, 집계기(05)는 의미 번역. UI 에서 규칙 중복 방지
- NEUTRAL 브랜드 랭킹(06)은 raw_responses.json을 재활용해 bold/heading 패턴에서 브랜드를 자동 추출 → Claude 1회 호출로 정제
- H2H 에서 AI가 한쪽을 명시 추천 안 한 "결정 유보" 케이스도 무승부로 포함 (60 runs 전체 집계되도록)
