# AiEO 프로젝트 진행 요약 (2026-04-23 ~ 04-24)

> Wayne이 Claude와 대화하며 진행한 작업 전체 정리. 노션으로 옮겨 기록.

## 1. 프로젝트 방향 확정

| 결정 | 내용 |
|------|------|
| 전체 구조 | **산공통(인과 실험) + 데마(예측 모델링) + 컨설팅(바디닥터 개선)** 통합 연구 |
| 버티컬 | 의료기기(요실금치료기) **주**, 가글 **보조** — 두 버티컬 분리 모델 |
| 산공통 설계 | L54 직교배열(L27×2 복제), F1~F6 요인, 가상 페이지 54종 × 쿼리 24개 × 반복 20 = 25,920 호출, 예산 $27 |
| 데마 설계 | 실제 크롤 SKU × 관측형 AI 호출 × XGBoost + SHAP |
| 2026-04-24 우선순위 전환 | **산공통 보류, 데마+컨설팅 먼저** 완결 결정 |

## 2. 경쟁군 확정 과정 (N 값 변동 이력)

| 시점 | 의료기기 N | 가글 N | 주요 변경 |
|------|----------|--------|---------|
| 초기 | 6 | 6 | 학술 표본 권고 |
| 2026-04-23 | 6 | 6 | F2026-04-23_same_grade_competition 기준 확정 |
| 2026-04-24 오전 | 14 | 5 | 공산품 풀 포함, 닥터케이 제거, 코웨이 테라솔 추가 |
| 2026-04-24 오후 | **13** | 5 | Elvie 제외 (Wayne 결정) |
| 2026-04-24 밤 | 13 | **12** | **가글 풀 확장** — 어썸쿨/테라브레스/유시몰/콜게이트/오랄비/센소다인/광동 추가 |

**현재 최종 (2026-04-24 v5)**:
- **의료기기 N=13**: 바디닥터 anchor + 12 (easyk, coway_therasol, ceragem, furenhealth, peronian, hools, wavecare, stopyo, ems_vital, kegel_magic, huonsen, applehip)
- **가글 N=12**: 프로폴린스 anchor + 11 (listerine, garglin, perio, 2080, awesomecool, therabreath, usimol, colgate, oralb, sensodyne, kwangdong)

## 3. 크롤링 성과

### ✅ 크롤 성공 (Sixthshop 점수 있음)

| 브랜드 | 채널 | Sixthshop | 비고 |
|--------|------|-----------|------|
| **2080** | SSG | **82** | 최고점 — 이커머스 플랫폼 효과 |
| **애플힙** | kakao | 75 | 공산품인데 점수 높음 — H10 강한 사전 신호 |
| **페로니언** | 11st | 73 | 공산품 |
| **케겔매직** | 11st | 73 | 공산품 |
| **휴온센** | — | 73 | 공산품 |
| **바디닥터** (우리) | gncosshop | **59** | anchor |
| **이지케이** | — | 58 | 의료기기 대표 경쟁 |
| **Elvie** | Shopify | 57 | 해외, 경쟁군 제외됐지만 벤치마크 참조 |
| **코웨이 테라솔 P** | coway.com | **51** | 대기업 신규 — JSON-LD 없음이 약점 |
| **가그린** | dmall | 41 | — |
| **훌스** | hiliving_mall | **31** | 스마트스토어 우회로 확보 |
| **프로폴린스** | 자사몰 | 36 | JSON-LD 없음 |

### ⚠️ 크롤 제약 이력

| 브랜드 | 장애 | 우회 |
|--------|------|------|
| **훌스** smartstore | 네이버 로그인 벽 (성인 카테고리 분류) | ✅ 하이리빙 공식몰 URL로 우회 |
| **코웨이 테라솔** | goProductVip JS 함수 redirect | ✅ `/product/detail?prdno=1452&optno=1` 직접 접근 |
| **리스테린** 자사몰 | Cloudflare WAF | ✅ curl_cffi Chrome TLS 임퍼소네이트 성공 (3차까지 실패→4차 성공) |
| **스탑요** 쿠팡 | Akamai Bot Manager | ❌ 자동 불가, Wayne 수동 저장 대안 |
| **퓨런헬스케어** | — | ✅ furun.kr 확정 |

## 4. 핵심 발견 (Findings)

| 파일 | 요약 |
|------|------|
| `F2026-04-24_first_presentation_feedback_analysis.md` | 1차 발표 피드백 50+ 전수 분류 (P0/P1/P2) |
| `F2026-04-24_friend_dashboard_review.md` | 친구 대시보드 NER 교훈 — Y2a 5분화 + 가글 풀 확장 근거 |
| `F2026-04-24_dm_consulting_priority_roadmap.md` | 데마+컨설팅 우선 로드맵 (산공통 보류) |
| `F2026-04-24_listerine_furun_selfmall_measured.md` | curl_cffi 4차 WAF 우회 성공 |
| `F2026-04-24_week3_execution_plan.md` | Week 3 실행 일정 (파일럿+본실험) |
| `F2026-04-24_feature_comparison.md` | Playwright + 11 피처 실측 비교 |
| `F2026-04-24_mfds_oem_pool.md` | 식약처 API endpoint 확정, 13 OEM 풀 |

## 5. 인프라 구축 (스크립트·파이프라인)

### 크롤러
- `crawler/scripts/_base.py` — 정적 fetch 공통 베이스 (requests)
- `crawler/scripts/_playwright_base.py` — Playwright + stealth v2
- `crawler/scripts/scrape_competitor_pool_v3.py`~`v6.py` — 단계별 크롤 배치
- `crawler/scripts/scrape_elvie.py` — Shopify (curl_cffi)
- `crawler/scripts/scrape_stopyo_coupang.py` — Akamai 차단 기록용
- `crawler/scripts/collect_external_evidence.py` — NAVER 검색 API (Wayne 키 대기)
- `crawler/scripts/extract_features.py` — HTML → features.jsonl
- `crawler/scripts/sixthshop_score.py` — A/B/C/D 100점 채점

### 머신러닝
- `ml/scripts/run_observational_queries.py` — 관측형 AI 호출 (Phase B1 예정)
- `ml/scripts/baseline_logistic.py` — baseline (Phase B2 예정)
- `ml/scripts/shap_analysis.py` — XGBoost + SHAP (Phase B3 예정)
- `ml/scripts/eda.py` — EDA
- `ml/scripts/aggregate_brand_features.py` — SKU 매칭 + brand-level 집계 (완료)

### 실험
- `experiments/synthetic_pages/_template.html.j2` — Jinja2, F1~F6 변형
- `experiments/synthetic_pages/design_matrix.csv` — L54 직교배열
- `experiments/synthetic_pages/page_001.html ~ page_054.html` — 렌더된 가상 페이지 (hero rating C안 재확인 필요)
- `experiments/prompts/queries.yaml` — 쿼리 8유형 × 3개 = 24개
- `experiments/runner.py` — 본실험 러너 (페르소나 옵션 포함)

## 6. 산출물 (Phase A 완료)

- `data/processed/features.jsonl` — **47 SKU** 피처
- `data/processed/sixthshop_scores.jsonl` — **47 SKU** Sixthshop 점수
- `data/processed/brand_aggregated_features.jsonl` — **18 브랜드** 집계 (SKU 매칭 반영)
- `data/processed/external_evidence.jsonl` — 준비됨, NAVER 키 받으면 실행

## 7. 방법론 결정 이력 (주요)

| 결정 | 근거 |
|------|------|
| L54 직교배열 (L27×2 복제) | F1~F6 6요인 × 3수준, pyDOE2 호환성 문제 → 수동 Taguchi |
| 반복 20회 (최소 15) | 2차 발표 피드백 R1 |
| temperature default (0 금지) | 2차 발표 피드백 R2 |
| 모델 버전 .env 고정 (gpt-5.4-nano) | 2차 발표 피드백 R3 |
| Position bias 셔플 (매 반복 seed) | 2차 발표 피드백 R4 |
| Y2a 5분화 (mention/positive/alternative/wintieloss/singleselect) | 친구 대시보드 교훈 |
| NER other_brands_detected | 친구 대시보드 교훈 |
| Hero rating F6=Reviews 조건부 | 2026-04-24 option C (오염 방지) |
| 페르소나 옵션 (gn_buyer vs none) | 1차 발표 피드백 (보류 중, GN 구매 데이터 대기) |

## 8. 컨설팅 산출물 초안 (완료된 것만)

- `consulting/action_roadmap.md` — 병렬 실행 로드맵 (ChatGPT Shopping·Profound·Alhena·체인시프트 참조)
- `consulting/gn_requests.md` — GN 본사 요청 리스트 (P0: 바디닥터 실제 제조사 확인)
- `consulting/dashboard_upgrade_spec.md` — 친구 대시보드 기반 업그레이드 spec
- `consulting/diagnosis/furun_self_mall_2026-04-24.json` — 실측 진단
- `consulting/diagnosis/listerine_self_mall_2026-04-24.json` — 실측 진단

## 9. 문서 자산 (Ragless 전략)

- `docs/PROJECT_MASTER.md` — 프로젝트 전체 컨텍스트
- `docs/knowledge/DIGEST.md` — 주간 갱신 의식 대상, 현재 v2.7
- `CLAUDE.md` — AI 작업 지침 (재현성 룰 등)
- `docs/knowledge/competitors/*.md` — 경쟁사별 진단 카드 (14종)
- `docs/knowledge/methods/*.md` — 재사용 절차 (L54, 샘플사이즈 정당화, 가상페이지 설계)
- `docs/knowledge/findings/*.md` — 20+ 발견
- `docs/workflows/*.md` — 재사용 워크플로우

## 10. 현재 블로커 / 대기 항목

| # | 항목 | 담당 | 영향 |
|---|------|------|------|
| W1 | NAVER 검색 API 키 발급 | **Wayne** | 있으면 좋음 (H14 외부 증거) · 필수 아님 |
| W2 | 스탑요 쿠팡 페이지 수동 저장 or alt 채널 | **Wayne** (선택) | 페이지 피처 없으면 레이블만 포함 |
| W3 | GN 본사 질문 (바디닥터 실제 제조사) | **Wayne** | P0 |
| W4 | GN 구매자 페르소나 데이터 | **Wayne** | 페르소나 EXPLORATORY |

## 11. 다음 단계 (Phase B 준비)

**입력**: Phase A 산출물 (47 SKU, 18 브랜드 집계) + 가글 풀 확장으로 신규 7 브랜드 추가 크롤 예정
**산출**:
1. 관측형 AI 호출 데이터 (Y = 멘션/선택/대안/승패)
2. Baseline 로지스틱 회귀 모델
3. XGBoost + SHAP 분석
4. 버티컬별 분리 비교 (의료기기 vs 가글)
5. 바디닥터 개별 SHAP 워터폴 (Before/After 시뮬레이션용)

**예상 비용**: ~$2.50 (gpt-5.4-nano, ~2,000 호출)
**예상 시간**: 3~4시간

## 12. git 커밋 최근 흐름 (2026-04-24)

```
d49592a 경쟁군 N=14→N=13 확정 — elvie 제외, stopyo 레이블 유지
df0137c Phase A 데이터 보강 완료 — 47 SKU / 18 브랜드 집계
9e50895 훌스 공식몰(하이리빙) 우회 경로 확보 — Sixthshop 31
09636bd 페르소나 옵션 + 코웨이 테라솔 P 확정 크롤
5c7bb95 hero rating C안 + 1차 발표 피드백 분석 + 추가 URL 크롤링
c223292 닥터케이 전면 삭제 + 경쟁군 추가 크롤링 (페로니언/애플힙/코웨이)
cc7ecd4 경쟁군 N=14 최종 확정 (닥터케이 제거, 공산품 8개 포함)
02c1c3b 코웨이 테라솔 U 발견 (제허 25-725, 대기업 신규) + 공산품 풀 정리
dc0cde4 친구 대시보드 리뷰 + Y2a 5분화 + observational/baseline
eb32dff 리얼리티 템플릿 + 쿼리 24개 YAML + 데마 순서 재정리
```

---

## 💡 핵심 인사이트 3가지

1. **공산품 페이지 품질이 의료기기보다 높음** (페로니언 73, 애플힙 75 vs 바디닥터 59) — H10 검정 전부터 이미 사전 신호 강함. 바디닥터는 카테고리 내에서도 페이지 경쟁력 열세.

2. **JSON-LD(A 카테고리) 부재가 1등 병목** — 프로폴린스·코웨이 테라솔·리스테린·퓨런헬스케어 모두 JSON-LD 0점. 한 번에 A 카테고리 25~35점 추가 가능한 저비용 개입.

3. **외부 증거(브랜드 인지도) 미반영이 모델 한계** — 페이지 피처만으로는 "왜 AI가 리스테린을 늘 먼저 추천하는가"에 답 못 함. NAVER 블로그/카페 언급량 feature 추가 시 SHAP 해석이 "페이지 품질 vs 브랜드 인지도" 두 축으로 분리되며 컨설팅 의미 ↑.
