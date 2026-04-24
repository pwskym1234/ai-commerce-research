---
date: 2026-04-24
title: 데마 분석 순서 재정리 — EDA 먼저, 모델링 나중
related_findings: [F2026-04-24_both_projects_pivot]
contradicts: []
supports: []
vertical: medical_device
phase: design
author: Claude (Wayne 피드백 반영)
---

# 데마 분석 순서 재정리

## 0. Wayne 지적 요약

"데마도 데이터 크롤링하고 태깅 끝낸 다음 쿼리 가지고 돌려서 결과 뽑으면 그거 분석부터 하고 모델 만들어야 되는 거 아냐?"

**맞음.** 이전 정리가 바로 XGBoost/SHAP로 직행해서 **EDA(결과 분석) 단계가 빠짐**. 재정리.

## 1. 올바른 데마 워크플로

```
(1) 크롤링 → data/raw/
   ├── 바디닥터 gncosshop (✅ 완료)
   ├── 이지케이 coreatech (✅ 완료)
   ├── 세라젬·퓨런 furun.kr (✅ 완료)
   ├── 리스테린·가그린·페리오·2080·프로폴린스 (✅ 완료)
   └── 닥터케이 11번가 (⏳ Wayne/데마 팀)
            ↓
(2) 태깅·피처 추출 → data/processed/features.jsonl
   ├── extract_features.py (HTML 구조 피처, ✅ 완료)
   └── sixthshop_score.py (점수화, ✅ 완료)
            ↓
(3) 쿼리 실행 (관찰형 — 산공통 본실험과 별도)
   ├── "경쟁 리스트 실제 브랜드명으로" 주입한 쿼리
   ├── 바디닥터·이지케이·세라젬·... 브랜드별 Y2a (멘션율) 수집
   └── Wayne 진단 리포트 구조 차용 (BRD/CAT/SYM/CMP/COM)
            ↓
★ (4) EDA (Exploratory Data Analysis) — 여기가 빠졌던 단계 ★
   ├── 기술통계: 브랜드별 Y2a, Y5(순위), Y7(감성) 분포
   ├── 피처 분포: Sixthshop 점수, 텍스트 길이, 리뷰 수 등
   ├── 단변량 상관: 각 피처 vs Y2a (Pearson r, scatter)
   ├── 다변량 시각화: heatmap, pairplot
   ├── 그룹별 비교: 의료기기 vs 가글 드라이버 차이
   ├── 아웃라이어 탐지: 특이 케이스 개별 분해
   └── 가설 생성: 데이터 보고 H14 외 추가 EXPLORATORY 가설
            ↓
(5) 피처 엔지니어링
   ├── 결측 처리 (퓨런 F1 등)
   ├── 스케일링 (가격 vs 리뷰수 vs 텍스트 길이 scale 차이)
   └── 카테고리 인코딩 (브랜드 더미)
            ↓
(6) Baseline: 로지스틱 회귀 (Harrell EPV 권장)
   ├── AUC / PR-AUC / Brier / Calibration curve
   └── 계수 해석 (SHAP 없이도 선형 설명 가능)
            ↓
(7) XGBoost + SHAP (블랙박스 모델 + 설명)
   ├── Global summary
   ├── Dependence plot 상위 피처
   ├── 바디닥터 individual waterfall
   └── 버티컬 분리 학습 (의료기기 vs 가글 SHAP 비교)
            ↓
(8) 결론 → 컨설팅 Before/After 시뮬레이터
```

## 2. 이전 정리와 차이

**이전 (잘못)**: (1) → (2) → (3) → **(7) XGBoost+SHAP 직행**

**수정 (올바름)**: (1) → (2) → (3) → **(4) EDA** → (5) → (6) → (7)

## 3. EDA에서 반드시 체크할 것

### 3.1 기술통계 & 분포
- 브랜드별 Y2a(멘션률), Y5(순위), Y7(감성) 평균·분산
- 페이지 피처 분포 (text_length, Sixthshop 점수 등) — 왜곡 여부
- 버티컬별(의료기기/가글) 분포 차이

### 3.2 상관 분석
- 단변량 상관: 각 피처 vs Y2a (Pearson / Spearman)
- 피처 간 상관 heatmap — 다중공선성 위험
- 특히 Sixthshop 총점 vs 각 소점수 (A/B/C/D)

### 3.3 그룹 비교
- 의료기기 vs 가글: 어느 피처가 각 버티컬에서 더 중요한가
- 자사몰 vs 이커머스 플랫폼(SSG/쿠팡): 앞서 발견된 격차(2080 82점 vs 프로폴린스 36점) 일반화?

### 3.4 시각화 (필수)
- box plot: 브랜드별 Y2a 분포
- scatter: 핵심 피처 × Y2a (trend line)
- heatmap: 피처 × 피처 상관
- bar chart: 브랜드별 Sixthshop 점수 (A/B/C/D 적층)
- 감성 분포 (Y7): positive/neutral/negative 스택드 바

### 3.5 가설 탐색
EDA 단계에서 **모델 적합 전에** 눈으로 관찰한 패턴을 EXPLORATORY_X 로 기록. 
본실험 사전 등록된 H1~H15와 별도 트랙.

## 4. 구현 파일 구조

```
ml/
├── notebooks/
│   └── 01_eda.ipynb                    # 대화형 EDA (옵션)
├── scripts/
│   ├── run_observational_queries.py    # (3) 브랜드별 쿼리 실행
│   ├── eda.py                          # ★ (4) 기술통계 + 상관 + 시각화 자동화
│   ├── feature_engineering.py          # (5) 피처 정제
│   ├── baseline_logistic.py            # (6) 로지스틱 baseline
│   └── shap_analysis.py                # (7) XGBoost + SHAP (마지막)
└── results/
    ├── eda/
    │   ├── descriptive_stats.csv
    │   ├── correlation_heatmap.png
    │   ├── brand_y2a_boxplot.png
    │   ├── sixthshop_stacked.png
    │   └── findings.md                  # EDA에서 발견한 것 기록
    ├── baseline_metrics.json
    └── shap_*.png
```

## 5. Week 3~4 재정렬

| 주차 | 기존 계획 | 수정 계획 |
|------|---------|---------|
| W3 Day 1~2 | 파일럿 실행 | 파일럿 실행 + **관찰형 쿼리 실행 준비** |
| W3 Day 3~4 | 본실험 실행 | **산공통 본실험 + 데마 관찰 쿼리** 병렬 |
| W3 Day 5 | 검증 | 검증 + **EDA 시작** |
| W4 Mon~Tue | XGBoost 학습 | **EDA 완료 + baseline 로지스틱** |
| W4 Wed~Thu | SHAP | **XGBoost + SHAP** |
| W4 Fri | 결합 분석 | 결합 분석 |

## 6. 당장 해야 할 것

- [ ] ml/scripts/eda.py 신규 작성 (기본 골격)
- [ ] ml/scripts/run_observational_queries.py 작성 (산공통 본실험과 별도 쿼리)
- [ ] `ml/scripts/shap_analysis.py` 에 "EDA 선행" 전제 명시 주석 추가
- [ ] Week 3~4 일정 보강 ([F2026-04-24_week3_execution_plan.md](F2026-04-24_week3_execution_plan.md) 갱신)
