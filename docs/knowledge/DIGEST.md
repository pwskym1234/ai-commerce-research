# DIGEST — AiEO 프로젝트 현재 상태

> 한눈에 보는 프로젝트의 *지금*. 매주 금요일 갱신.
> 모든 발견을 한 줄씩. 상세는 `findings/`, `competitors/`, `methods/` 참조.
> 이 파일이 항상 최신이면, Claude는 이것만 읽고도 작업 가능. (Ragless 핵심)

**마지막 갱신**: 2026-04-23 (1차 경쟁사 조사 완료)

---

## 🎯 현재 단계
- 주차: **0주차 (셋업)**
- 다음 마일스톤: 1주차 — 의료기기 경쟁사 조사 + 요인 확정 / 크롤링 시작
- 미확정 핵심: [PROJECT_MASTER.md §10](../PROJECT_MASTER.md) 참조

---

## 📊 핵심 수치 (현재)

| 지표 | 값 | 출처 | 갱신일 |
|------|-----|------|--------|
| 가상 페이지 제작 수 | 0 / 18~36 | — | — |
| 본실험 API 호출 수 | 0 | — | — |
| 크롤링 SKU 수 (의료기기) | 0 (경쟁사 stub 3개 작성됨) | competitors/ | 2026-04-23 |
| 크롤링 SKU 수 (가글) | 0 (경쟁사 stub 5개 작성됨) | competitors/ | 2026-04-23 |
| 바디닥터K 카테고리 추천율 (Before) | 14.5% | 사전 추정치 | — |
| 바디닥터K 카테고리 추천율 (After) | — | 미측정 | — |

---

## 🧪 가설 상태 (마스터 §4.4)

| ID | 내용 한줄 | 상태 |
|----|----------|------|
| H1 | HTML 포맷이 파싱 정확도 영향 | 🟡 미검정 |
| H2 | JSON-LD 스키마가 파싱 정확도 영향 | 🟡 미검정 |
| H3 | F1×F2 교호작용 | 🟡 미검정 |
| H4 | 수치 구체성이 파싱 정확도 영향 | 🟡 미검정 |
| H5 | 인증 명시가 추천 확률 ↑ | 🟡 미검정 |
| H6 | 인증 명시가 Y4 회피 ↓ | 🟡 미검정 |
| H7 | 임상 인용 > 사용자 후기 | 🟡 미검정 |
| H8 | Y1 ≠ Y2 (GEO ≠ AiEO) | 🟡 미검정 |
| H9 | 경쟁 상황에서 구조화 효과 ↑ | 🟡 미검정 |

상태 범례: 🟡 미검정 / 🟢 지지 / 🔴 기각 / ⚪ 결과 mixed

---

## 🏢 경쟁사 진단 (F1~F6 기준)

> 1차 조사 결과 (2026-04-23). 페이지 직접 진단은 2주차 크롤링 후 갱신.

### 의료기기 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F4 인증위치 | F5 인증상세 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|------------|------------|--------|------------|
| [바디닥터](competitors/) (우리) | ? | ? | ? | ? | ⚠️ 등급 미정* | ? | anchor |
| [이지케이](competitors/easyk.md) | ? | ? | partial | ? | partial (GMP만) | user_reviews | 필수 |
| (식약처 검색 OEM 1~2종) | — | — | — | — | — | — | 강 권장 |
| [애플힙](competitors/applehip.md) (노이즈) | ? | ? | ambiguous | ? | none(추정) | — | 옵션 (별도 분석) |

*인증 등급 마스터 §2.2와 검색 결과 불일치 → Active Conflicts 참조.

### 가글 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|--------|------------|
| [프로폴린스](competitors/propolinse.md) (우리) | image_heavy | none | explicit | visual_demo (텍스트 약) | anchor |
| [리스테린](competitors/listerine.md) | ? | ? | explicit (4 oils) | brand_authority | 필수 |
| [가그린](competitors/garglin.md) | ? | ? | ambiguous(추정) | legacy(1982 국내 최초) | 필수 |
| [2080](competitors/2080.md) | ? | ? | ambiguous(추정) | brand_recognition | 필수 |
| [페리오](competitors/perio.md) | ? | ? | ambiguous(추정) | total_oral_care | 권장 |

---

## 📝 최근 발견 (Findings)

> 최신 5개만. 전체는 `findings/` 디렉토리.

- 2026-04-23: [F2026-04-23_competitor_initial_research.md](findings/F2026-04-23_competitor_initial_research.md) — 1차 경쟁사 조사 + 의료기기 시장 2층 구조(의료기기 vs 비의료기기 운동도구) 발견 + 바디닥터 인증 등급 마스터와 불일치 (★ Wayne 검증 필요)

---

## 🔴 Active Conflicts (모순/미해결)

> 두 발견이 충돌하는 경우 여기 표시. 다음 의식 때 결정.

- **★ P0 — 바디닥터 인증 등급 불일치**: 마스터 §2.2 "식약처+FDA 2등급" vs 외부 검색 "식약처 3등급(최고), FDA 1+2등급". 산공통 F4/F5 가상 페이지 설계의 신뢰성 직결. Wayne이 GN그룹 측 확인 + 식약처 emed.mfds.go.kr 교차 검증 → 정정 PR 필요. 출처: [F2026-04-23_competitor_initial_research §3](findings/F2026-04-23_competitor_initial_research.md)
- **이지케이 공식 사이트 접근**: easyk.kr 현재 fetch 실패 (ECONNREFUSED). HTTPS 미지원 또는 일시적. Wayne 브라우저로 검증 후 결과 공유.
- **"닥터케이" 정체 미확정**: 단일 브랜드로 검색 안 잡힘. Wayne 메모 정확성 또는 변형명("닥터케겔") 확인.

---

## 🛠️ 적용된 방법 / 템플릿

> `methods/`에 정착된 재사용 절차들.

- (아직 없음 — 1주차에 직교배열 L18 결정 시 첫 method 추가 예정)

---

## 🚧 다음 액션 (Wayne / 팀)

| 항목 | 책임 | 마감 | 상태 |
|------|------|------|----|
| ★ 바디닥터 인증 등급 GN그룹 측 확인 + 마스터 §2.2 정정 | Wayne | P0 즉시 | 🔴 진행 |
| 식약처 emed.mfds.go.kr "골반저근자극기/요실금치료기" 검색 → OEM 후보 | Wayne | 1주차 內 | ⏳ |
| "닥터케이" URL 공유 또는 후보 제외 결정 | Wayne | 1주차 內 | ⏳ |
| 의료기기 경쟁사 본실험 최종 리스트 확정 (권고: 바디닥터+이지케이+OEM 1~2종) | Wayne | 1주차 금요일 | ⏳ |
| 가글 경쟁사 본실험 최종 리스트 확정 (권고: 프로폴린스+리스테린+가그린+2080+페리오) | Wayne | 1주차 금요일 | ⏳ |
| EXPLORATORY_NEW1/2 (의료기기 vs 비의료기기 구분 가설) 산공통 사전 가설 추가 여부 | Wayne | 1주차 內 | ⏳ |
| 직교배열 L18 vs L36 결정 | Wayne | 1주차 | ⏳ |
| 바디닥터 자사 페이지 직접 크롤링 + F1~F6 1차 진단 | 데마 팀 | 1주차 | ⏳ |
| 가그린/페리오/2080 공식몰 fetch + competitors/ 보강 | 데마 팀 | 2주차 | ⏳ |
| 첫 갱신 의식 시도 | Wayne | 1주차 금요일 | ⏳ |

---

## 📚 빠른 링크

- 프로젝트 전체: [PROJECT_MASTER.md](../PROJECT_MASTER.md)
- 작업 가이드: [CLAUDE.md](../../CLAUDE.md)
- 트렌드 적용 설계: [trends_2026/APPLICATION.md](../trends_2026/APPLICATION.md)
- 워크플로우 템플릿: [workflows/README.md](../workflows/README.md)
- 용어: [glossary.md](glossary.md)
