---
date: 2026-04-24
title: 데마 + 컨설팅 우선 로드맵 (산공통 보류)
related_findings: [F2026-04-24_week3_execution_plan.md, F2026-04-24_first_presentation_feedback_analysis.md]
contradicts: []
supports: []
vertical: both
phase: plan
author: Claude + Wayne 결정
sources_summary: Wayne 지시 2026-04-24 "데마·컨설팅 먼저, 산공통은 미룸"
---

# 데마 + 컨설팅 우선 로드맵

## 결정 배경

Wayne 지시(2026-04-24): 산업공학통계 프로젝트(L54 가상 페이지 실험 + H1~H15 인과 검정)는 **보류**. 데이터마이닝(실측 크롤링 + 예측 모델링) + 컨설팅(바디닥터K 개선 진단)을 먼저 완결.

## 현재 확보 상태 (Phase A 완료 시점)

- 크롤 **47 SKU** (18 브랜드)
- features.jsonl + sixthshop_scores.jsonl 47 row 처리 완료
- brand_aggregated_features.jsonl **18 브랜드 집계** 완료 (SKU 매칭 피드백 반영)
- Elvie/코웨이/훌스 신규 확보 (각각 57/51/31점)
- NAVER 외부증거 수집기 스크립트 준비 완료 — Wayne 키 대기

## 4-Phase 실행 계획

### Phase A — 데이터 보강 (✅ 완료 또는 pending)

| # | 작업 | 상태 |
|---|-----|------|
| A1 | elvie 공식 URL 크롤 | ✅ 완료 (Shopify 57점) |
| A1 | propolinse/perio 추가 SKU | ⏸ 자사몰 JS 렌더링 필요, 기존 1 SKU 유지 (한계로 문서화) |
| A1 | stopyo 실재 확인 | 🔴 Wayne 결정 대기 (검색 결과 0건) |
| A2 | features + Sixthshop 재추출 | ✅ 완료 (47 row) |
| A3 | 외부 증거 H14 NAVER API 수집 | 🔴 Wayne NAVER 키 대기 — 스크립트 준비됨 |
| A4 | SKU 매칭 + brand-level 집계 | ✅ 완료 (18 브랜드) |

### Phase B — 관측형 AI 호출 + 데마 모델링 (다음)

**Y 변수 확보 전략**: 산공통 본실험(25k 호출)은 보류하지만, 데마용 관측형 소규모 호출(1.1k)은 가능.

| # | 작업 | 예상 |
|---|-----|-----|
| B1 | `ml/scripts/run_observational_queries.py` 실행 — 14 브랜드 × 8 쿼리유형 × 10 반복 = 1,120 호출 | 30분, $1.20 (gpt-5.4-nano) |
| B2 | `baseline_logistic.py` — 페이지 피처 + Sixthshop → 멘션/선택 확률 | 30분 |
| B3 | XGBoost + SHAP — 피처 기여도 (의료기기/가글 분리) | 1~2시간 |
| B4 | 외부 증거 추가 (Wayne 키 받으면) → H14 통합 | 30분 |

### Phase C — 바디닥터K 진단 + 컨설팅 (Week 2~3)

| # | 산출물 | 근거 |
|---|-------|-----|
| C1 | `consulting/diagnosis/bodydoctor_k_2026-05-XX.md` — F1~F6 breakdown + SHAP 상위 3개 개선 포인트 | Sixthshop 59점 + 모델 결과 |
| C2 | 경쟁사 벤치마크 표 (18 브랜드) | brand_aggregated_features.jsonl |
| C3 | Before/After 시뮬레이션 | JSON-LD 추가 등 개선 조치 → 예상 Sixthshop + SHAP 예측 추천 확률 변화 |
| C4 | 우선순위 액션 리스트 (P0/P1/P2) | action_roadmap.md 와 연계 |

### Phase D — GN 전달용 최종 산출물 (Week 3 말)

- D1. 1페이지 executive summary
- D2. `consulting/reports/improvement_playbook.md` (실행 매뉴얼)
- D3. 경쟁사 벤치마크 시각화 (md or xlsx)
- D4. `gn_requests.md` 업데이트 — 현재 P0 "바디닥터 실제 제조사 확인" + 추가 요청(stopyo 실재 여부, 프로폴린스 채널 전략 등)

### Phase E — 산공통 재개 (보류 해제 시점)

- 54페이지 재렌더 → 파일럿 → 본실험 → H1~H15 검정 → 2차 발표 Week 6

## 한계 / 개선 여지

1. **propolinse/perio 1 SKU 각각만 확보** — JS 렌더 필요, variance 추정 어려움. 데마 모델에서 가중치 낮춤 or SKU matching으로 brand-level 대표값 사용.
2. **NAVER 키 대기** — H14 관측형 외부 증거 자동 수집 불가. 수동 fallback 또는 Google Trends 대체 가능.
3. **인과 주장은 관측형 수준**. "F 요인 → 추천 확률" 주장은 산공통 L54 결과 없이는 관측형 상관으로만 표현. 발표에선 "관측형 분석 + 향후 통제 실험으로 검증" 구조로 제시.
4. **stopyo 처리** — Wayne 결정 없으면 N=14 → N=13 (공산품 7개)으로 축소 가능.

## 트레이드오프 (왜 이 순서인가)

- 데마/컨설팅 우선 이유: 실측 기반 → GN 임팩트 빠름, 3주 안에 개선안 전달 가능
- 산공통 보류 비용: 인과 검정 없이 관측형만 → 데마 발표 시 "왜 관측형인가" 답변 필요
- 그러나 데마 프로젝트 평가 기준은 **예측 성능 + SHAP 해석 + 버티컬 비교**로 충족 가능 (인과 추론 요구 낮음)

## 다음 실행

Phase B1 (관측형 호출) 바로 진행 가능. gpt-5.4-nano 기준 $1.20, 30분.
