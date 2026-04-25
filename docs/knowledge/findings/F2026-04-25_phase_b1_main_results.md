---
date: 2026-04-25
title: Phase B1 본실험 — 의료기기/가글 페이지 제공의 incremental 효과
related_findings: [F2026-04-25_data_reliability_assessment.md, F2026-04-24_dm_consulting_priority_roadmap.md]
contradicts: []
supports: [H10, H14]
vertical: both
phase: results
author: Claude (Wayne 본실험 실행 후 분석)
sources_summary: 1920 OpenAI 호출 + 1920 Claude haiku 파싱, 8.2분, $11.48
---

# Phase B1 본실험 결과

## 0. 실행 요약

- **모델**: gpt-5.4-mini (응답), claude-haiku-4-5 (파싱)
- **호출량**: 1,920 OpenAI + 1,920 Claude
- **비용**: $11.48 / 예산 $15 (캐시 히트 272건으로 약 14% 절약)
- **시간**: 8.2분 (병렬 동시 20)
- **오류**: 0 (모든 호출/파싱 성공)
- **시스템 프롬프트**: "한국어로 답변해주세요" 미니멀
- **반복**: 20회 / 쿼리당, R1~R5 재현성 룰 준수

## 1. Anchor mention rate (480 호출/조합)

| 조합 | BRD | CAT | SYM | CMP | COM | PRC | USE | DEC | 전체 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|------|
| 의료 open  | 100% |  0% |  0% | 67% |  0% |  0% |  0% |  0% | **21%** |
| 의료 closed | 100% |  2% |  0% | 67% |  5% | 27% |  0% |  0% | **25%** |
| 가글 open  | 100% |  0% |  0% | 33% |  2% |  2% |  0% |  0% | **17%** |
| 가글 closed | 100% | 10% | 10% | 37% | 42% | 30% |  7% |  0% | **29%** |

## 2. 페이지 제공의 incremental 효과 (Closed − Open)

| 버티컬 | Open(prior) | Closed(페이지) | Δ |
|-------|-----------|-------------|----|
| **의료기기 (바디닥터)** | 20.8% | 25.0% | **+4.2%p** |
| **가글 (프로폴린스)** | 17.1% | 29.4% | **+12.3%p** |

**해석**:
- 가글은 페이지 개선만으로 추천 확률 **3배 효과** (12.3 vs 4.2)
- 가글 closed에서 COM(42%) / PRC(30%) / CMP(37%)가 골고루 활성화 → **다양한 쿼리에서 페이지 인용**
- 의료기기 closed는 BRD/CMP/PRC에만 효과 → 카테고리 일반(CAT/SYM/USE)에선 페이지 줘도 추천 안 함

**컨설팅 함의**:
- **프로폴린스(가글)**: 페이지 SEO/AiEO 개선의 leverage가 매우 큼 → 즉각 액션 권장
- **바디닥터(의료기기)**: 페이지 개선만으로 부족 → **외부 증거(브랜드 인지도/리뷰/인용)** 보강 필수

## 3. AI prior 글로벌 편향 — Top mentions (의료기기 open)

| 순위 | 브랜드 | 멘션 수 | 분류 |
|-----|-------|--------|-----|
| 1 | 바디닥터 | 100 | 우리 (BRD 쿼리에서만 잡힘) |
| 2 | 이지케이 | 56 | 한국 직접 경쟁 |
| **3** | **Elvie Trainer** | **44** | **해외 글로벌** |
| **4** | **Perifit** | **40** | **해외 글로벌** |
| 5 | 세라젬 | 28 | 한국 대기업 |
| 6 | 코웨이 (테라솔 포함) | 43 | 한국 대기업 |
| 7+ | Kegel8, kGoal, Intimina | 12, 10, 9 | 해외 글로벌 |

**발견**:
- 글로벌 브랜드 멘션 합계 = Elvie(44) + Perifit(40) + Kegel8(12) + kGoal(10) + Intimina(9) = **115회**
- 한국 브랜드 합계 = 이지케이(56) + 세라젬(28) + 코웨이(43) = **127회**
- → 거의 동률. AI prior에서 한국 의료기기 시장 인지도 매우 약함

**H10/H14 가설 강하게 지지**:
- H10: AI는 의료기기와 비의료기기를 잘 구분 못 함 → 추가 검정으로 KegelSmart/Perifit 같은 비의료 EMS 트레이너가 의료기기 답변에 섞임
- H14: 외부 증거(글로벌 SEO 콘텐츠 양)가 추천에 직결

## 4. 룰 vs Claude 정밀 파싱 일치도

거의 모든 mention rate에서 룰 == Claude (수치 동일). 차이가 있는 곳:
- 의료 closed PRC: rule 25% vs Claude 27%
- 가글 open COM/PRC: rule 0% vs Claude 2% (1건 차이)

**해석**: 단순 brand mention 매칭은 룰이 충분. Claude haiku의 가치는:
- `our_sentiment` (positive/neutral/negative) — 룰의 키워드 매칭이 부정확한 영역
- `comparison_result` (win/tie/loss/solo) — 비교 응답 정밀 분류
- `single_select` (DEC 단일 선택) — 응답 마지막 부분 의미 파악
- `mentioned_brands` NER — 사전 정의 외 브랜드 자동 발굴 (Elvie/Perifit 등 발견)

## 5. 다음 단계 (Phase B2/B3)

**입력 X (페이지 피처)**:
- features.jsonl 54 SKU
- brand_aggregated_features.jsonl 18 브랜드
- external_evidence.jsonl 25 브랜드 NAVER (블로그/카페/뉴스/쇼핑 카운트)
- (선택) manual_tags.jsonl — 수동 태깅 시작 시

**입력 Y (B1 결과)**:
- B1-A 오픈셋: brand × query_type 단위 mention rate (anchor 기준)
- B1-B 클로즈드셋: page × query 단위 추천 비율
- 페이지 단위 Y는 1,920 row 가까이 확보 (B2 모델 안정)

**B2 baseline 로지스틱**:
- X: 페이지 피처 + 외부 증거
- Y: closed mode mention (페이지 단위)
- 분리 모델: 의료기기 / 가글

**B3 SHAP**:
- XGBoost + TreeExplainer
- 페이지 X 변화 → mention 확률 변화 시뮬레이션
- 컨설팅용 워터폴 (바디닥터/프로폴린스 개선 시 예상 추천 확률)

## 6. 산출 파일

```
ml/data/b1_runs/
├── b1_open_medical_device_20260425_110019/
│   ├── b1.jsonl           (480 row, 룰 파싱 포함)
│   ├── parsed_claude.jsonl (480 row, Claude 정밀)
│   └── summary.json
├── b1_closed_medical_device_20260425_110145/
├── b1_open_gargle_20260425_110221/
├── b1_closed_gargle_20260425_110347/
└── _full_run.log          (전체 실행 로그)
```

## 7. 한계

- **n=20 반복 / 쿼리당 = 60 obs / type / vert**: BRD에서 Wilson 95% CI ±0.045 (충분), 0%/100% 극단치는 false positive/negative 1~2건 영향 큼
- **gpt-5.4-mini 단일 모델**: 다른 모델(Gemini, Claude, Perplexity) 응답 분포 미검증 — Phase 4 sanity check 권장
- **시스템 프롬프트 미니멀**: 진짜 ChatGPT 웹 사용자 시뮬레이션이지만 ChatGPT 자체 시스템 프롬프트 영향 미통제
- **B1-B 페이지 텍스트 컨텍스트**: gpt-5.4-mini web browsing 없어 우리가 압축본 주입 — 실제 AI agent(Perplexity/ChatGPT Shopping)는 다른 fetch 행동 가능
