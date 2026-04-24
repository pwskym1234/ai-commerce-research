# DIGEST — AiEO 프로젝트 현재 상태

> 한눈에 보는 프로젝트의 *지금*. 매주 금요일 갱신.
> 모든 발견을 한 줄씩. 상세는 `findings/`, `competitors/`, `methods/` 참조.
> 이 파일이 항상 최신이면, Claude는 이것만 읽고도 작업 가능. (Ragless 핵심)

**마지막 갱신**: 2026-04-24 v2.7 — 의료기기 경쟁군 **N=13 확정** (Elvie 제외, Wayne 결정 2026-04-24). 스탑요 쿠팡 URL 확정(itemId 8637377284) but Akamai 차단 — 페이지 피처 없이 레이블만 유지. 가글 버티컬은 N=5 별도 유지 (프로폴린스 anchor + 리스테린/가그린/페리오/2080). 데마+컨설팅 Phase A 완료.

---

## 🎯 현재 단계
- 주차: **0주차 (셋업)**
- 다음 마일스톤: 1주차 — 의료기기 경쟁사 조사 + 요인 확정 / 크롤링 시작
- 미확정 핵심: [PROJECT_MASTER.md §10](../PROJECT_MASTER.md) 참조

---

## 📊 핵심 수치 (현재)

| 지표 | 값 | 출처 | 갱신일 |
|------|-----|------|--------|
| **현재 우선순위** | 데마 + 컨설팅 (Phase A~D). 산공통 L54/본실험 **보류** | 2026-04-24 v2.6 결정 | 2026-04-24 |
| **경쟁군 확정** | **의료기기 N=13** (anchor + 12 경쟁, Elvie 제외) / **가글 N=5** | runner.py L81 | 2026-04-24 |
| 크롤링한 SKU 수 | **47** (스탑요는 Akamai 차단 → 레이블만 유지) | data/processed/sixthshop_scores.jsonl | 2026-04-24 |
| 경쟁군 브랜드 집계 | **18 브랜드** (elvie 포함, 모델 학습 시 11~12 브랜드로 조정) | brand_aggregated_features.jsonl | 2026-04-24 |
| Sixthshop 바디닥터 (gncosshop) | **59/100** (A25/B13/C6/D15) | sixthshop_scores.jsonl | 2026-04-24 |
| Sixthshop Top 3 (의료기기) | 페로니언 11st **73**, 애플힙 kakao **75**, 코웨이 테라솔 P **51** | 2026-04-24 |
| Sixthshop Top 3 (가글) | 2080 SSG **82**, 가글린 dmall **74**, 리스테린 gum-care **43** | 2026-04-24 |
| Sixthshop 신규 (이번 세션) | 훌스 하이리빙 **31**, Elvie Shopify **57**, 코웨이 테라솔 P **51** | 2026-04-24 |
| 가상 페이지 제작 수 (산공통) | 54/54 생성됨 (hero rating C 재렌더 필요 확인) | experiments/synthetic_pages/ | 2026-04-24 |
| 본실험 예정 비용 (산공통 보류 중) | $27 (gpt-5.4-nano 25,920 호출) | experiment_design_v2 | — |
| 외부 증거(H14) 수집 상태 | **Wayne NAVER API 키 대기** (스크립트 준비됨) | crawler/scripts/collect_external_evidence.py | 2026-04-24 |
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
| **H12** | Rufus SPN (USE 쿼리 × F6) 교호작용 | 🟡 미검정 (사전등록 2026-04-24) |
| ~~H13~~ | ~~Rich card rendering~~ | ❌ 드롭 (API 구조 파싱 한계) |
| **H14** | 외부 증거(리뷰·인용·커뮤니티)가 추천 ↑ | 🟡 미검정 (관찰형, 사전등록 2026-04-24) |
| **H15** | 쿼리 × F 교호작용 | 🟡 미검정 (사전등록 2026-04-24, L54 근거) |

상태 범례: 🟡 미검정 / 🟢 지지 / 🔴 기각 / ⚪ 결과 mixed

---

## 🏢 경쟁사 진단 (F1~F6 기준)

> 1차 조사 결과 (2026-04-23). 페이지 직접 진단은 2주차 크롤링 후 갱신.

### 의료기기 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F4 인증위치 | F5 인증상세 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|------------|------------|--------|------------|
| [바디닥터](competitors/bodydoctor.md) (우리) | ★ 확정 (크롤링 완료) | Product | partial | bottom/none | none | marketing | anchor (제조사 불명 — 화이트라벨 가능) |
| [이지케이/EASY-K](competitors/easyk.md) | unknown | unknown | explicit | unknown | partial | user_reviews+celeb | 필수 (알파메딕, 제허 15-329 호, 허가일 2015-03-10) |
| [**코웨이 테라솔 U**](competitors/coway_therasol.md) ★★ 신규 | unknown | unknown | unknown | unknown | unknown | unknown | **필수 (제허 25-725, 2025 등록 대기업 — 가장 위협적 경쟁자)** |
| [**(주)세라젬**](competitors/_medical_device_oem_pool.md) | unknown | unknown | unknown | unknown | unknown | unknown | 권고 (제허 23-785 호, 대기업) |
| [**(주)퓨런헬스케어**](competitors/furun.md) ★실측 | BULLET | **none** | machine_spec_only (0.375) | **bottom** (0.807) | **CE+GMP만, 식약처/제허 언급 0** | none | 제외 검토 (코웨이 추가 시) |
| [**공산품 노이즈 풀**](competitors/_non_medical_products_pool.md) ★ | — | — | — | — | — | — | 페로니언 or 닥터케이 1종 (H10 검정 노이즈) |
| [애플힙](competitors/applehip.md) (노이즈) | ? | ? | ambiguous | ? | none(추정) | — | 옵션 (H10 검정용) |
| (해외 1종, Elvie 권장) | — | — | — | — | — | — | 권장 (글로벌 학습 편향 측정) |

### 가글 버티컬

| 브랜드 | F1 HTML | F2 JSON-LD | F3 수치 | F6 근거 | 본실험 우선순위 |
|--------|--------|-----------|--------|--------|------------|
| [프로폴린스](competitors/propolinse.md) (우리) | image_heavy | none | explicit | visual_demo (텍스트 약) | anchor |
| [리스테린](competitors/listerine.md) ★실측 | BULLET (SPA, JS 렌더 전) | **none** (Product/AggregateRating 0) | **explicit** (0.517: 30초/99%/130년/52%/30%) | **brand_authority** + Bazaarvoice 리뷰 위젯 | 필수 |
| [가그린](competitors/garglin.md) | PARAGRAPH 50% / BULLET 30% | none | ambiguous (CPC·불소 명시, 함량 X) | legacy(1982 최초, 갤럽 No.1) | 필수 |
| [2080](competitors/2080.md) | 자사몰 약함 (마트 분산) | none(추정) | partial (무SLS/무파라벤) | 가성비 + 마케팅 중심 | 필수 |
| [페리오](competitors/perio.md) | PARAGRAPH 위주 | none | ambiguous (12hr 단일 수치) | 치약 중심, 가글 약함 | 권장 |
| (해외 1종, 콜게이트/테라브레스 권장) | — | — | — | — | Wayne 결정 |

---

## 📝 최근 발견 (Findings)

> 최신 5개만. 전체는 `findings/` 디렉토리.

- 2026-04-24: [F2026-04-24_listerine_furun_selfmall_measured.md](findings/F2026-04-24_listerine_furun_selfmall_measured.md) — ★★★ curl_cffi 4차 시도로 WAF 우회 성공. 리스테린·퓨런 자사몰 F1~F6 실측 완료. 두 브랜드 모두 JSON-LD 0건. 퓨런 정식 URL `furun.kr`로 정정.
- 2026-04-24: [F2026-04-24_week3_execution_plan.md](findings/F2026-04-24_week3_execution_plan.md) — ★ Week 3 실행 일정 (파일럿+본실험), critical path, 예산 $150 확정
- 2026-04-24: [F2026-04-24_listerine_furen_status.md](findings/F2026-04-24_listerine_furen_status.md) — ~~리스테린·퓨런 크롤링 3차 시도 모두 WAF 차단~~. **2026-04-24 오후 curl_cffi로 4차 시도 성공 — 이 finding은 measured 파일로 수정됨**
- 2026-04-24: [F2026-04-24_both_projects_pivot.md](findings/F2026-04-24_both_projects_pivot.md) — ★★★ v2 설계 확정 후 산공통/데마 두 프로젝트의 변경점 정리 (L54, 쿼리 8유형, Y7 감성, H12/14/15 사전등록, Sixthshop 점수 통합).
- 2026-04-24: [F2026-04-24_wayne_diagnostic_vs_roadmap.md](findings/F2026-04-24_wayne_diagnostic_vs_roadmap.md) — ★★★ Wayne 진단 리포트(1,000건 실측)와 action_roadmap 비교. 닥터케이 실재 확인, 공식 인용 7%만(external evidence war 증거), 쿼리 COM 신규 반영 필요.
- 2026-04-24: [F2026-04-24_hypothesis_upgrade.md](findings/F2026-04-24_hypothesis_upgrade.md) — 업계 리서치 반영 F/가설 고도화 초안 (→ experiment_design_v2.md로 확정).
- 2026-04-24: [F2026-04-24_feature_comparison.md](findings/F2026-04-24_feature_comparison.md) — ★★★ Playwright 크롤링 + 11+ 피처 실측 비교. 의료기기: 이지케이가 바디닥터보다 text 4배·explicit num 무한배 우위. 가글: 프로폴린스가 가그린·2080 대비 JSON-LD 없음.
- 2026-04-24: [F2026-04-24_mfds_oem_pool.md](findings/F2026-04-24_mfds_oem_pool.md) — ★★★ 식약처 API endpoint 확정 + 13개 OEM 전체 추출. 바디닥터 DB 미등록 → 화이트라벨 가능성. 본실험 경쟁군: 알파메딕+세라젬+퓨런헬스케어 권고
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

- **[orthogonal_array_L54.md](methods/orthogonal_array_L54.md)** ★ — **L54 실제 구현안 (L27×2 복제) + 직교성 실측 검증 + Jinja2 템플릿 연결**
- **[experiment_design_v2.md](methods/experiment_design_v2.md)** ★ — v2 본실험 설계 전체 (L54, 쿼리 8유형, Y 7개, H12~H15). gpt-5.4 비용 추론 포함.
- [orthogonal_array_L36.md](methods/orthogonal_array_L36.md) — v1 (L36). L54로 대체됨.
- [sample_size_justification.md](methods/sample_size_justification.md) — N=6 표본 정당화.
- [synthetic_pages_design.md](methods/synthetic_pages_design.md) — 가상 페이지 제작 가이드.

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
| ✅ 식약처 API endpoint 확정 + 13개 OEM 풀 추출 | Claude | 2026-04-24 | 🟢 완료 |
| ★ 바디닥터 실제 제조사 확인 — GN 본사에 정식 질문 (consulting/gn_requests.md P0 항목) | Wayne | 1주차 內 | 🔴 P0 |
| ✅ 본실험 경쟁군 3·4번 확정 — **세라젬 + 퓨런헬스케어** | Wayne | 2026-04-24 | 🟢 완료 |
| **[업계 리서치 반영] F 요인/가설 고도화 결정** — 쿼리 7유형? Y2 이중? H12~H15 사전등록? | Wayne | 1주차 內 | 🔴 P0 |
| 실제 개선 액션 로드맵 실행 시작 (consulting/action_roadmap.md) — Stage 1~2 (Ingest+Evaluate) | Wayne | 1~2주차 | ⏳ |
| 반복 횟수 20 vs 30 결정 (파일럿 후) | Wayne | 3주차 (파일럿 후) | ⏳ |
| 해외 1종 후보 결정 (의료기기 Elvie 권장 / 가글 콜게이트 또는 테라브레스) | Wayne | 1주차 內 | ⏳ |
| easyk.kr 자사몰 직접 fetch + F1~F6 정밀 진단 | Claude (다음 task) | 1주차 內 | ⏳ |
| 바디닥터 단독 모델 가격 + 자사몰 상세 페이지 fetch | Claude (다음 task) | 1주차 內 | ⏳ |
| ✅ 리스테린 자사몰 fetch + F1~F6 실측 (curl_cffi로 Cloudflare 우회) | Claude | 2026-04-24 | 🟢 완료 |
| ✅ 퓨런헬스케어 자사몰 fetch + F1~F6 실측 (furun.kr 확정) | Claude | 2026-04-24 | 🟢 완료 |
| 가글 3종(가그린/페리오/2080) 공식 페이지 fetch 보강 | 데마 팀 / Claude | 2주차 | ⏳ |
| ★ 의료기기 경쟁사 본실험 최종 리스트 확정 — **퓨런 자사몰 B2B로 판명, EXPLORATORY 이동** 권고. N=6 대체 후보(쉬엔비/리모트솔루션/비엠씨/유진플러스) 검토 | Wayne | 1주차 금요일 | 🔴 P0 |
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
- **GN 요청 리스트**: [consulting/gn_requests.md](../../consulting/gn_requests.md) ★
- **실제 개선 로드맵**: [consulting/action_roadmap.md](../../consulting/action_roadmap.md) ★
- 업계 리서치 1 (경쟁사): [AiEO_경쟁사_리서치.md](findings/AiEO_경쟁사_리서치.md)
- 업계 리서치 2 (landscape): [ai_product_visibility_landscape_2026-04-24.md](findings/ai_product_visibility_landscape_2026-04-24.md)
