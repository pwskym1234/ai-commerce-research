# 데마 팀원용 가이드

> AiEO 데마(데이터마이닝) 프로젝트 진입점. 데마 팀원은 **이 파일에서 시작**해서 필요한 폴더만 보면 됩니다.
> 산공통·컨설팅 관련 파일들은 안 봐도 OK.

---

## 1. 데마 프로젝트 한 줄 요약

상품 페이지 피처(X) → AI 추천 확률(Y) 예측 모델 + SHAP 해석.

- **X** = 페이지에서 추출한 자동·수동 피처 (50+ 차원)
- **Y** = ChatGPT API에 쿼리 던졌을 때 그 브랜드/페이지가 추천받은 비율
- **모델** = LR / DT / KNN / XGBoost
- **해석** = SHAP + Tier 분류 + Before/After 워터폴

---

## 2. 봐야 할 폴더·파일 (✅) / 안 봐도 되는 폴더 (❌)

### ✅ 봐야 할 것

| 영역 | 경로 | 용도 |
|-----|----|-----|
| **데마 메인 코드** | `ml/scripts/` | 분석 스크립트 전체 (baseline·CV·SHAP·waterfall 등) |
| **데마 입력 X** | `data/processed/features.jsonl` | 자동 추출 22 차원 |
| 데마 입력 X | `data/processed/manual_tags_template.csv` | 수동 태깅 템플릿 (작업 대상) |
| 데마 입력 X | `data/processed/sixthshop_scores.jsonl` | A/B/C/D 100점 |
| 데마 입력 X | `data/processed/external_evidence.jsonl` | NAVER 외부 증거 (브랜드 단위) |
| 데마 입력 X | `data/processed/brand_brd_features.jsonl` | brand-level "AI prior" 변수 |
| **데마 입력 Y (B1 응답)** | `ml/data/b1_runs/<run_id>/parsed_claude.jsonl` | Claude 정밀 파싱본 |
| **쿼리** | `experiments/prompts/queries.yaml` (의료) | 24 쿼리 |
| 쿼리 | `experiments/prompts/queries_gargle.yaml` (가글) | 24 쿼리 |
| 쿼리 | `experiments/prompts/queries_kdr.yaml` (바디닥터 K) | 24 쿼리 (신규) |
| **태깅 가이드** | `docs/knowledge/methods/manual_tagging_guide.md` | 수동 태깅 매뉴얼 (★필독) |
| 가설 매핑 | `docs/knowledge/methods/h_taxonomy_to_tagging_mapping.md` | H1~H15 ↔ 태깅 차원 |
| **데마 결과 finding** | `docs/knowledge/findings/F2026-04-25_phase_b1_main_results.md` | B1 본실험 결과 |
| 데마 결과 finding | `docs/knowledge/findings/F2026-04-25_data_reliability_assessment.md` | 표본 한계·보완책 |
| 진행 요약 | `docs/progress/2026-04-24_session_summary_for_notion.md` | 노션 요약 |

### 🟡 데마 관련만 일부

| 영역 | 경로 | 데마 관련 항목 |
|-----|----|------------|
| 크롤러 | `crawler/scripts/` | `run_brd_per_brand.py`, `extract_features.py`, `sixthshop_score.py`, `collect_external_evidence.py` |
| HTML 원본 | `data/raw/<vertical>/<brand>/<channel>/<날짜>/*.html` | 수동 태깅 시 페이지 직접 열어볼 때만 |
| 경쟁사 카드 | `docs/knowledge/competitors/*.md` | 분석 시 참고용 |

### ❌ 안 봐도 되는 폴더

| 영역 | 폴더 | 안 보는 이유 |
|-----|----|-----------|
| 산공통 (보류 중) | `stats/` | 가설검정·로지스틱 회귀 — 데마와 별개 트랙 |
| 산공통 가상 페이지 | `experiments/synthetic_pages/` | 산공통 통제 실험용 54 페이지 |
| 컨설팅 산출물 | `consulting/` | GN그룹 컨설팅 — 데마 결과 받아 가공만 |
| 컨설팅 GEO 감사 도구 | `consulting/aao-gn/` | 상균이 운영 별도 트랙 — gpt-4o-search-preview + Next.js 대시보드. 데마 R1=20과 다른 REPEAT_COUNT=2 정책 (컨설팅 baseline 측정용) |
| 컨설팅 관련 finding | `consulting/action_roadmap.md`, `consulting/gn_requests.md` 등 | |
| 마스터 문서 일부 | `docs/PROJECT_MASTER.md` 의 산공통/컨설팅 섹션 | |

---

## 3. 작업 흐름 — 어떤 순서로 봐야?

### Step 1 — 프로젝트 이해 (15분)
1. 본 README 한 번 훑기
2. `docs/knowledge/findings/F2026-04-25_phase_b1_main_results.md` 읽기 (B1 본실험 핵심 발견)
3. `docs/progress/2026-04-24_session_summary_for_notion.md` (전체 진행 정리)

### Step 2 — 본인 영역 확인 (PPT 분장)
- **방우식**: 진행 정리·인프라 점검·태깅 본인분
- **박지윤**: 쿼리 검토 (`experiments/prompts/queries*.yaml`) + ChatGPT 응답 quality 검토 (`ml/data/b1_runs/<run>/parsed_claude.jsonl`) + Recommendation Score 정의
- **이경민**: EDA 직접 실행·Tier 분류·모델 선택·학습 — `ml/scripts/eda_analysis.py`, `tier_classifier.py`, `baseline_models.py`, `shap_pipeline.py` 검토
- **이소현**: 모델 평가·발표·보고서 — `ml/scripts/cv_evaluation.py` + 결과 정리

### Step 3 — 태깅 (다 같이, 약 1~2시간)
- `docs/knowledge/methods/manual_tagging_guide.md` 정독
- `data/processed/manual_tags_template.csv` 구글시트로 옮겨서 작업
- 본인 할당 SKU의 raw_path 따라가서 HTML 보고 태깅
- P0 17 차원 우선 (시간 부족 시 P0만)

### Step 4 — 분석 (Claude가 인프라 깔아둠)
- 태깅 끝나면: `python3 ml/scripts/run_phase_b234_full.py` 한 번 실행 → EDA/Tier/Baseline/CV/SHAP/Waterfall 6단계 자동
- 결과는 `ml/results/` 에 저장

---

## 4. 코드 모듈 구조 (`ml/scripts/`)

| 모듈 | 역할 | 의존 |
|-----|----|----|
| `_data_loader.py` | features + manual_tags + Y(B1) + external + sixthshop join | 다른 모듈이 import |
| `run_b1_async.py` | OpenAI API 호출 (open + closed × 의료/가글) | `_data_loader` |
| `run_brd_per_brand.py` | BRD per-brand 호출 (brand-level X 추출용) | — |
| `parse_responses_claude.py` | Claude haiku 정밀 파싱 (open·closed 응답) | — |
| `parse_brd_brand_claude.py` | BRD 응답 → brand_brd_features.jsonl | — |
| `aggregate_brand_features.py` | brand-level 집계 | — |
| `eda_analysis.py` | 분포·결측·VIF·이상치 | `_data_loader` |
| `tier_classifier.py` | 4분면 Tier 매트릭스 | `_data_loader` |
| `baseline_models.py` | LR / DT / KNN 학습 | `_data_loader` |
| `cv_evaluation.py` | 5-fold + LOOCV + Bootstrap CI | `baseline_models` |
| `shap_pipeline.py` | XGBoost + SHAP | `baseline_models` |
| `waterfall_simulator.py` | Before/After 시나리오 시뮬 | `shap_pipeline` |
| `run_phase_b234_full.py` | 6단계 통합 wrapper | 위 모두 |
| `verify_pipeline.py` | 본실험 전 smoke test | — |
| `build_manual_tags_template.py` | 태깅 빈 템플릿 생성 | — |

---

## 5. 데이터 구조 한눈에

```
data/
├── raw/                                ← 크롤한 HTML 원본
│   ├── medical_device/<brand>/<channel>/<date>/*.html
│   ├── gargle/<brand>/<channel>/<date>/*.html
│   └── kegel_exerciser/<brand>/...     (바디닥터 K 신규)
└── processed/                          ← 정제된 피처
    ├── features.jsonl                  ← 자동 X (22차원, 60 SKU)
    ├── sixthshop_scores.jsonl          ← Sixthshop 100점
    ├── brand_aggregated_features.jsonl ← brand 단위 집계
    ├── external_evidence.jsonl         ← NAVER 외부 증거 (브랜드)
    ├── brand_brd_features.jsonl        ← brand-level AI prior X
    ├── manual_tags_template.csv        ← 수동 태깅 빈 템플릿
    └── manual_tags.jsonl               ← (앞으로) 태깅 결과
```

```
ml/
├── data/b1_runs/<run_id>/               ← OpenAI API 응답
│   ├── b1.jsonl                          ← 룰 파싱 + raw 응답
│   ├── parsed_claude.jsonl               ← Claude 정밀 파싱본
│   └── summary.json                      ← run 메타 (비용·시간)
├── scripts/                              ← 분석 코드 (위 표 참조)
├── results/                              ← 모델·시각화 결과 (앞으로)
├── models/                               ← 학습된 모델 (앞으로)
└── notebooks/                            ← 노트북 (필요 시)
```

---

## 6. 데이터 소스 한정 범위

데마에서 가져오는 정보 출처:

**페이지 X (콘텐츠 자체)**:
- 각 SKU의 **상품 상세 페이지 1개만** (브랜드 단위 best 1개 선정)
- 채널: 자사·제조사 공식몰 + 리테일·오픈마켓 둘 다 포함
- 추출: 본문 텍스트(BS4) / 이미지 / JSON-LD / 인증·임상 키워드 / FAQ·Q&A / 가격·재고 메타

**브랜드 단위 외부 증거**:
- NAVER 검색 API 카운트만 (블로그/카페/뉴스/쇼핑 검색 결과 수)
- 외부 글 본문은 가져오지 않음

**브랜드 단위 AI prior**:
- BRD per-brand 응답 (OpenAI gpt-5.4-mini의 학습 지식)

**제외**: 메인 페이지·카테고리 리스트·리뷰 본문·SNS·유튜브·광고

---

## 7. 자주 헷갈리는 것

| Q | A |
|---|---|
| "open vs closed" | open = 페이지 컨텍스트 X, 쿼리만 / closed = 페이지 컨텍스트 + URL 메타 같이 |
| "anchor" | 우리 측 브랜드. 의료기기=바디닥터, 가글=프로폴린스, K=바디닥터 K |
| "vertical" | medical_device / gargle / kegel_exerciser (3종) |
| "P0 / P1" | P0 = 가설 검정 직결 핵심 차원 (먼저). P1 = 시간 여유 시 |
| "BRD per-brand" | 모든 브랜드 × BRD 1쿼리 × 20반복 = brand-level X 추출용 별도 트랙 |

---

## 8. 더 깊이 들어갈 때

- 전체 프로젝트 컨텍스트: `docs/PROJECT_MASTER.md` (산공통·컨설팅 포함 전체 — 데마 부분만 발췌해서 보면 됨)
- 현재 상태 한눈에: `docs/knowledge/DIGEST.md`
- 작업 가이드: `CLAUDE.md` (AI 어시스턴트 운영 지침 — 재현성 룰 R1~R10 등)
- 워크플로우 템플릿: `docs/workflows/`
