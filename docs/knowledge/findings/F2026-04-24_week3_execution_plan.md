---
date: 2026-04-24
title: Week 3 실행 일정 확정 (파일럿 + 본실험 + 분석 착수)
related_findings: [F2026-04-24_both_projects_pivot]
contradicts: []
supports: []
vertical: both
phase: execution
author: Claude
---

# Week 3 실행 일정

## 0. 현재 상태 (Week 1 종료 시점)

### 완성된 산출물
- ✅ L54 설계 매트릭스 (54 runs, 직교성 검증 완료)
- ✅ Jinja2 템플릿 + 54개 HTML 가상 페이지 생성
- ✅ API 러너 (gpt-5.4 기본, 캐시, R1~R10 강제)
- ✅ 경쟁사 N=6 확정 (바디닥터/이지케이/세라젬/퓨런/닥터케이/Elvie)
- ✅ Sixthshop 점수 baseline 15페이지 실측
- ✅ 업계 리서치 반영 가설 확장 (H12/H14/H15)

### 대기 중
- ⏳ GN P0 3개 응답 (허가번호·FDA·임상)
- ⏳ 닥터케이/퓨런 추가 URL 확보 (데마 보강)

## 1. Week 2 (2026-04-25 ~ 05-01): 준비 마감

### 산공통 팀
- [ ] 가상 페이지 54개 시각 검수 (브라우저로 열어서 조건부 렌더 확인)
- [ ] 쿼리 8개 실제 문구 다듬기 (Wayne 검수)
- [ ] GN 응답 받으면 `_product.json`의 kfda_number·fda_number 실제 값 반영
- [ ] 가설 H1~H15 검정 계획 문서화 (statsmodels 코드 골격)

### 데마 팀
- [ ] 쿠팡/SSG에서 리스테린·퓨런 SKU URL 확보 → 재크롤링
- [ ] 닥터케이 11번가 페이지 크롤링 (https://www.11st.co.kr/products/2444307960)
- [ ] Sixthshop 점수 모든 경쟁사 완비
- [ ] external evidence 변수 수집 계획 (리뷰 수·외부 언급)

### Wayne
- [ ] GN 회의 — P0 3개 답변 수신
- [ ] .env에 `OPENAI_API_KEY` 확정 입력 + `OPENAI_MODEL_VERSION=gpt-5.4`
- [ ] 해외 1종 최종 (Elvie Trainer로 결정)

## 2. Week 3 (2026-05-02 ~ 05-08): 파일럿 + 본실험 실행

### Day 1 (월)
```bash
# 파일럿 실행
python experiments/runner.py --mode pilot --dry-run
# → 예상 호출 270, 비용 ~$3.4 확인
python experiments/runner.py --mode pilot
```
- 결과: `experiments/api_runs/pilot_YYYYMMDD_HHMMSS/responses.jsonl`
- 검증:
  - 응답 파싱 성공률 ≥ 95%
  - Y2a(멘션) 비율이 경쟁군 N 수준에 합리적
  - R1~R10 룰 준수 (jsonl 메타데이터 확인)
  - 캐시 히트율 0% (cold start)

### Day 2 (화)
- 파일럿 변동성 측정 → 본실험 반복 횟수 최종 결정 (20 유지 vs 30 증가)
- 문제 발견 시 runner 수정 + 재돌리기

### Day 3~4 (수~목)
```bash
# 본실험 실행
python experiments/runner.py --mode main --dry-run
# → 예상 호출 8,640, 비용 ~$108 확인
python experiments/runner.py --mode main
```
- 예상 실행 시간: 2~4시간 (API rate limit 고려)
- 중간 실패 시 jsonl은 append되어 있어 재개 가능
- 완료 후 summary.json 자동 생성

### Day 5 (금)
- 본실험 raw 응답 검증
- data/processed/ 에 분석 데이터 정리

## 3. Week 4 (2026-05-09 ~ 05-15): 분석

### 산공통
- 로지스틱 회귀 (Y2a ~ F1+F2+...+F6 + Q + F:Q interactions)
- H1~H3, H15 교호작용 검정
- Wilson 95% CI forest plot
- effect size + odds ratio 산출

### 데마
- 피처 추출 최종 (Sixthshop 점수 + external evidence 포함)
- 로지스틱 회귀 baseline + XGBoost
- SHAP 분석 (global + individual SKU 워터폴)
- 버티컬 비교 (의료기기 vs 가글 드라이버)

### 공통
- 두 결과 결합 → 컨설팅 Before/After 시뮬레이터 초안
- 바디닥터 실제 페이지 F 수준 확정 후 예측값 산출

## 4. Week 5 (2026-05-16 ~ 05-22): 외적 타당성

- Phase 4: 바디닥터 실제 페이지 개선 전후 측정
- 실제 페이지 변경 (GN 권한 확보 전제) 또는 변경 시뮬레이션 페이지로 대체
- 같은 쿼리셋으로 재측정

## 5. Week 6 (2026-05-23 ~ 05-29): 발표 준비

- 슬라이드 초안 (학술 구조: 연구 질문 → 가설 → 실험 → 결과 → 결론)
- 예상 질문 리허설 (마스터 §9.4 + Wayne 진단 리포트 신뢰도 이슈)
- So What 슬라이드 (바디닥터 Before/After 본실험 결과 기반)

## 6. Week 7 (2026-05-30 ~): 발표

## 7. Critical Path (차질 시 영향)

| 블로커 | 영향 |
|--------|------|
| GN P0 응답 지연 | F5 수준 "Full"의 실제 허가번호 허구 사용 → 외적 타당성 ↓ |
| OpenAI API 키 미확보 | 본실험 실행 불가 — Week 3 자체 중단 |
| 닥터케이 URL 미확보 | 경쟁군 5종만 (6 → 5). H10 검정 약화 |
| bot 차단으로 쿠팡 크롤링 실패 | 데마 데이터 축소 — H14 관찰형 약화 |

## 8. 예산 요약

- 본실험 API: ~$108
- 파일럿: ~$3.4
- Codex/Plus 구독: $20/월 × 2개월 = $40
- **총: ~$150 (₩21만)**

## 9. Wayne 다음 액션

1. **Week 2 내로 OpenAI API 키 + .env 확정**
2. **GN P0 3개 응답 수신 (최대한 빨리)**
3. **닥터케이 11번가 URL로 페이지 크롤링 요청 (또는 Wayne 수동 fetch)**
4. **리스테린·퓨런 쿠팡 URL 공유**
