# DIGEST — AiEO 프로젝트 현재 상태

> 한눈에 보는 프로젝트의 *지금*. 매주 금요일 갱신.
> 모든 발견을 한 줄씩. 상세는 `findings/`, `competitors/`, `methods/` 참조.
> 이 파일이 항상 최신이면, Claude는 이것만 읽고도 작업 가능. (Ragless 핵심)

**마지막 갱신**: 2026-04-23 (LLM=1 결정 + 단독 페이지 정밀 진단 + 가상 페이지 method + 데마 크롤러 골격 작동 확인)

---

## 🎯 현재 단계
- 주차: **0주차 (셋업)**
- 다음 마일스톤: 1주차 — 의료기기 경쟁사 조사 + 요인 확정 / 크롤링 시작
- 미확정 핵심: [PROJECT_MASTER.md §10](../PROJECT_MASTER.md) 참조

---

## 📊 핵심 수치 (현재)

| 지표 | 값 | 출처 | 갱신일 |
|------|-----|------|--------|
| 가상 페이지 제작 수 | 0 / 36 (L36 확정) | methods/orthogonal_array_L36.md | 2026-04-23 |
| 본실험 API 호출 수 (예정) | 0 / 2,880 (36×4×20×1, ChatGPT만) | methods/sample_size_justification.md | 2026-04-23 |
| 크롤링한 SKU 수 | 4 (gncosshop 바디닥터 핵심) | crawler/scripts/scrape_gncosshop.py | 2026-04-23 |
| 추출한 피처 수 | 1차 EDA 가능 수준 (text length, JSON-LD, 인증/임상 키워드, 수치 비율, 가격) | data/processed/features.jsonl | 2026-04-23 |
| 비교군 N | 의료기기 6 / 가글 6 (확정) | F2026-04-23_same_grade_competition + methods/sample_size_justification | 2026-04-23 |
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
| H10 | AI는 의료기기/비의료기기 구분 못해 의료기기 점유율 희석 | 🟡 미검정 (사전등록 2026-04-23) |
| H11 | 쿼리에 "의료기기" 명시 시 카테고리 좁혀짐 | 🟡 미검정 (사전등록 2026-04-23) |

상태 범례: 🟡 미검정 / 🟢 지지 / 🔴 기각 / ⚪ 결과 mixed

---

## 🏢 경쟁사 진단 (F1~F6 기준)

> 1차 조사 결과 (2026-04-23). 페이지 직접 진단은 2주차 크롤링 후 갱신.

### 의료기기 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F4 인증위치 | F5 인증상세 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|------------|------------|--------|------------|
| [바디닥터](competitors/bodydoctor.md) (우리) | paragraph(추정) | none | partial(99단계) | bottom/none | none | marketing | anchor (식약처 3등급, FDA 1+2) |
| [이지케이/EASY-K](competitors/easyk.md) (알파메딕 제조) | unknown | unknown | explicit (99단+5단) | unknown | partial | user_reviews+celeb | 필수 (식약처 3등급, 제허15-329호) |
| (식약처 API로 OEM 2종 추출) | — | — | — | — | — | — | 강 권장 (인증 받은 표본 확보) |
| [애플힙](competitors/applehip.md) (노이즈) | ? | ? | ambiguous | ? | none(추정) | — | 옵션 (EXPLORATORY_NEW1 검정용) |
| (해외 1종, Elvie 권장) | — | — | — | — | — | — | 권장 (글로벌 학습 편향 측정) |

### 가글 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|--------|------------|
| [프로폴린스](competitors/propolinse.md) (우리) | image_heavy | none | explicit | visual_demo (텍스트 약) | anchor |
| [리스테린](competitors/listerine.md) | ? (listerine.kr fetch 차단) | ? | **explicit** (99.9%/30초/12hr/4성분) | brand_authority + 5배 비교 인용 | 필수 |
| [가그린](competitors/garglin.md) | PARAGRAPH 50% / BULLET 30% | none | ambiguous (CPC·불소 명시, 함량 X) | legacy(1982 최초, 갤럽 No.1) | 필수 |
| [2080](competitors/2080.md) | 자사몰 약함 (마트 분산) | none(추정) | partial (무SLS/무파라벤) | 가성비 + 마케팅 중심 | 필수 |
| [페리오](competitors/perio.md) | PARAGRAPH 위주 | none | ambiguous (12hr 단일 수치) | 치약 중심, 가글 약함 | 권장 |
| (해외 1종, 콜게이트/테라브레스 권장) | — | — | — | — | Wayne 결정 |

---

## 📝 최근 발견 (Findings)

> 최신 5개만. 전체는 `findings/` 디렉토리.

- 2026-04-23: [F2026-04-23_empty_product_pages.md](findings/F2026-04-23_empty_product_pages.md) — ★★★ 바디닥터·이지케이 단독 페이지에 등급/허가번호/임상 모두 없음. 컨설팅 임팩트 결정타. (단, 크롤러 검증 후 정정: 텍스트는 있지만 의료기기 특화 정보 없음)
- 2026-04-23: [F2026-04-23_same_grade_competition.md](findings/F2026-04-23_same_grade_competition.md) — ★★ 바디닥터·이지케이 모두 식약처 3등급. H5/H6/H7의 진짜 의미가 "같은 3등급 안에서 페이지 표기 방식이 추천에 영향" 으로 정밀화. 본실험 비교군 N=6 권고.
- 2026-04-23: [F2026-04-23_competitor_initial_research.md](findings/F2026-04-23_competitor_initial_research.md) — 1차 경쟁사 조사 + 의료기기 시장 2층 구조 발견 + 바디닥터 인증 등급 정정 (식약처 3등급 + FDA 1+2)

---

## 🔴 Active Conflicts (모순/미해결)

> 두 발견이 충돌하는 경우 여기 표시. 다음 의식 때 결정.

- ✅ **해결: 바디닥터 인증 등급** (2026-04-23): 식약처 **3등급** 조합 의료기기, FDA **1+2등급** 모두 등록으로 확정. 마스터 §2.2 정정 완료. 출처: 서울신문 2024-12-26 + GN코스몰 카테고리. 단, 정확한 식약처 허가번호는 공공데이터 API로 별도 조회 예정.
- ✅ **해결: 이지케이 = 알파메딕 EASY-K** (2026-04-23)
- ✅ **해결: "닥터케이" = "바디닥터K" 약어 중복** (2026-04-23) — Wayne 추측 수용, 마스터 표기 통일 완료
- ⚠️ **식약처 OpenAPI endpoint 미해결**: 키는 발급됨(.env). 5개 추정 endpoint(MdcInQrySrvc, MedDevPrmsnInfoService 등) 모두 500 "Unexpected errors". 식약처 통합정보시스템(udiportal)은 OAuth2 별도 인증. → Wayne이 [data.go.kr 마이페이지](https://www.data.go.kr) → 활용신청 내역 → 데이터셋 15057456 상세 → "샘플 코드/가이드 다운로드"에서 정확한 endpoint 추출 필요

---

## 🛠️ 적용된 방법 / 템플릿

> `methods/`에 정착된 재사용 절차들.

- [orthogonal_array_L36.md](methods/orthogonal_array_L36.md) — 본실험 가상 페이지 36개 설계 표 (Taguchi L36). L18/L26과의 비용·효용 비교.
- [sample_size_justification.md](methods/sample_size_justification.md) — N=6 + 반복 20회 + LLM=1 (2,880 호출) 표본 정당화. 발표 대응 스크립트 포함.
- [synthetic_pages_design.md](methods/synthetic_pages_design.md) — 가상 페이지 36개 제작 표준 가이드. F1~F6 수준별 마크업 패턴 + Jinja2 템플릿 골격 + 검증 체크리스트.

---

## 🚧 다음 액션 (Wayne / 팀)

| 항목 | 책임 | 마감 | 상태 |
|------|------|------|----|
| ✅ 바디닥터 인증 등급 확정 (식약처 3등급 + FDA 1+2) + 마스터 §2.2 정정 | Claude | 2026-04-23 | 🟢 완료 |
| ✅ N=6 확정 (의료기기 6 + 가글 6) | Wayne | 2026-04-23 | 🟢 완료 |
| ✅ 직교배열 L36 확정 | Wayne | 2026-04-23 | 🟢 완료 |
| ✅ EXPLORATORY → H10/H11 사전등록 | Wayne | 2026-04-23 | 🟢 완료 |
| ✅ "닥터케이" = "바디닥터K" 약어 중복 추정 → 마스터 표기 통일 (모두 "바디닥터") | Wayne | 2026-04-23 | 🟢 완료 |
| ✅ data.go.kr API 키 발급 + .env 저장 | Wayne | 2026-04-23 | 🟢 완료 |
| ⚠️ data.go.kr **마이페이지에서 정확한 endpoint URL 확인 필요** (5개 추정 endpoint 모두 500. 식약처 통합정보시스템(udiportal)은 OAuth2 인증 별도) | Wayne | 1주차 內 | 🔴 진행 |
| 반복 횟수 20 vs 30 결정 (파일럿 후) | Wayne | 3주차 (파일럿 후) | ⏳ |
| 해외 1종 후보 결정 (의료기기 Elvie 권장 / 가글 콜게이트 또는 테라브레스) | Wayne | 1주차 內 | ⏳ |
| easyk.kr 자사몰 직접 fetch + F1~F6 정밀 진단 | Claude (다음 task) | 1주차 內 | ⏳ |
| 바디닥터 단독 모델 가격 + 자사몰 상세 페이지 fetch | Claude (다음 task) | 1주차 內 | ⏳ |
| 가글 4종(가그린/페리오/2080/리스테린) 공식 페이지 fetch 보강 | 데마 팀 / Claude | 2주차 | ⏳ |
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
