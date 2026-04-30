# DIGEST — AiEO 프로젝트 현재 상태

> **이것만 봐도 됨**. 한눈에 보는 프로젝트의 *지금*.
> 매주 금요일 갱신. Wayne·팀이 재시작 시 가장 먼저 읽는 파일.
> 모든 발견을 한 줄씩 — 상세는 `findings/`, `competitors/`, `methods/`, `consulting/` 참조.

**마지막 갱신**: 2026-04-30 — 경쟁사 풍경 갱신·NAVER 검색 매핑·자동화 인프라(Notion 적층 + 모니터링 cron) 구축·PDP 카피 초안·페르소나 정의·팀 네이밍 규칙 신설·Rule 6 (최신=최종 라벨) 일괄 적용. NAVER 키 *확보* 확정 (이전 "키 대기" 잘못된 표기 정정), Phase B1 결과 반영, 9개 경쟁사 추가 적층, 자동화 hook + 페르소나 정의 신설.

---

## 🎯 현재 최신본 인덱스 — 이것만 보면 됨

각 산출물의 *최신* 파일·상태. 옛 버전은 *보존만*, 참조는 항상 최신 사용.

### 산공통/데마 본실험

| 산출물 | 최신 파일 | 상태 | 비고 |
|---|---|---|---|
| **의료기기 쿼리셋 (최종, 본실험 재실행용)** | [queries_medical_최종.yaml](../../experiments/prompts/queries_medical_최종.yaml) | ✅ 페르소나 stratified 32 쿼리 | PRIMARY 16 + SECONDARY 8 + TERTIARY 8 |
| 의료기기 쿼리셋 (B1 정합 보존) | [queries_medical_B1보존.yaml](../../experiments/prompts/queries_medical_B1보존.yaml) | ✅ 동결 (B1 완료) | 데마 B1에 사용된 그대로, 재현용 보존 |
| 의료기기 쿼리셋 (NAVER 보강) | [queries_medical_네이버검색반영.yaml](../../experiments/prompts/queries_medical_네이버검색반영.yaml) | ✅ 중간 단계 보존 | EASY-K 영문·복압성·갱년기·글로벌·산후 회복 보강 |
| **가글 쿼리셋 (최종, 본실험 재실행용)** | [queries_gargle_최종.yaml](../../experiments/prompts/queries_gargle_최종.yaml) | ✅ 페르소나 stratified 32 쿼리 | 잇몸 약함 PRIMARY + 모유수유 SECONDARY + 어린이/흡연자 TERTIARY |
| 가글 쿼리셋 (B1 정합 보존) | [queries_gargle_B1보존.yaml](../../experiments/prompts/queries_gargle_B1보존.yaml) | ✅ 동결 | B1에 사용된 그대로 |
| 가글 쿼리셋 (NAVER 보강) | [queries_gargle_네이버검색반영.yaml](../../experiments/prompts/queries_gargle_네이버검색반영.yaml) | ✅ 중간 단계 보존 | 프로폴리스 가글 / 잇몸 가글 / 충치예방 / 2080 비교 보강 |
| 직교배열 설계 | [methods/orthogonal_array_L54.md](methods/orthogonal_array_L54.md) | ✅ 확정 (현재 사용) | L18·L36은 이전 버전 |
| 가상 페이지 | `experiments/synthetic_pages/` (54개) | ⚠️ hero rating C 재렌더 필요 | 산공통 보류 해제 시 점검 |
| 본실험 러너 | [experiments/runner.py](../../experiments/runner.py) | ✅ R1~R10 강제 | OpenAI 키·gpt-5.4 핀 |
| 본실험 결과 (B1) | `ml/data/b1_runs/` (4 runs) | ✅ 1,920 호출 완료 | [F2026-04-25_phase_b1_main_results.md](findings/F2026-04-25_phase_b1_main_results.md) 참조 |

### 컨설팅 산출물

| 산출물 | 최신 파일 | 상태 | 비고 |
|---|---|---|---|
| 12주 실행 로드맵 | [consulting/action_roadmap.md](../../consulting/action_roadmap.md) | ✅ 2026-04-30 갱신 | §1.6·§2.5·§4.1 신설 |
| 바디닥터 PDP 카피 | [bodydoctor_pdp_copy_초안.md](../../consulting/diagnosis/bodydoctor_pdp_copy_초안.md) | ⚠️ 초안 (TBD 5개) | GN P0 응답 후 본문 |
| 프로폴린스 PDP + 시딩 | [propolinse_pdp_copy_초안.md](../../consulting/diagnosis/propolinse_pdp_copy_초안.md) | ⚠️ 초안 | 30/60일 캠페인 포함 |
| **핵심 페르소나** | [consulting/personas/핵심_페르소나.md](../../consulting/personas/핵심_페르소나.md) | ✅ Wayne 정의 (2026-04-30) | GN 인터뷰 회신 후 갱신 |
| GN P0 요청 (기존) | [consulting/gn_requests.md](../../consulting/gn_requests.md) | ⏳ 응답 대기 | 허가번호·FDA·임상 |
| FAQ 자료 요청 메일 | [consulting/gn_requests_FAQ_data.md](../../consulting/gn_requests_FAQ_data.md) | ⏳ 발송 대기 | 회신 목표 2026-05-17 |
| JSON-LD 풀스키마 | [consulting/diagnosis/bodydoctor_jsonld.json](../../consulting/diagnosis/bodydoctor_jsonld.json) + [snippet.html](../../consulting/diagnosis/bodydoctor_jsonld_snippet.html) | ⚠️ TBD 5개 | GN P0 응답 후 v1 |

### 데이터·인프라

| 산출물 | 최신 파일 | 상태 |
|---|---|---|
| NAVER 검색 데이터 | [data/processed/naver_search_volume.json](../../data/processed/naver_search_volume.json) + [.md](../../data/processed/naver_search_volume.md) | ✅ 60+ 키워드 매핑 (2026-04-30) |
| NAVER 인사이트 | [F2026-04-30_naver_search_insights.md](findings/F2026-04-30_naver_search_insights.md) | ✅ 7개 충격적 발견 |
| 외부 증거 (H14) | `ml/data/external_evidence/` | 🔴 NAVER 키 확보, 수집 실행 대기 (D2) |
| 노션 적층 | [scripts/notion_log_commit.py](../../scripts/notion_log_commit.py) | ✅ git commit 후 자동 발화. 11 카드 적층 완료 |
| 주간 모니터링 | [scripts/monitor_aieo.py](../../scripts/monitor_aieo.py) + [plist](../../scripts/com.aieo.monitor.plist) | ⚠️ 미설치 (Wayne launchctl load 대기) |

### 지식·규칙

| 문서 | 상태 |
|---|---|
| [docs/PROJECT_MASTER.md](../PROJECT_MASTER.md) | 학술 정합성 마스터 |
| [CLAUDE.md](../../CLAUDE.md) | 작업 가이드 (R1~R10 정의) |
| [glossary.md](glossary.md) | ✅ 2026-04-30 보강 (BRD/F1-F6/H1-H15/R1-R10/Phase 개별) |
| [팀_네이밍_규칙.md](팀_네이밍_규칙.md) | ✅ 신설 — 신규 팀원 5분 이해 목표 |
| [F2026-04-30_competitor_landscape_update.md](findings/F2026-04-30_competitor_landscape_update.md) | ✅ Profound 유니콘·JP/CN·healthcare 갭 |

---

## 📊 핵심 수치 (현재)

| 지표 | 값 | 출처 | 갱신일 |
|---|---|---|---|
| **현재 우선순위** | 데마 + 컨설팅 (Phase A~D). 산공통 보류 | Wayne 결정 2026-04-24 | 2026-04-24 |
| **경쟁군** | 의료기기 N=13 + 가글 N=5 (자체 페이지 9 신규 추가됨) | runner.py L81 + competitors/ | 2026-04-30 |
| 크롤링 SKU | **47** (스탑요 Akamai 차단 → 레이블만) | data/processed/sixthshop_scores.jsonl | 2026-04-24 |
| 브랜드 집계 | **18 브랜드** | brand_aggregated_features.jsonl | 2026-04-24 |
| Sixthshop 바디닥터 (gncosshop) | **59/100** (A25/B13/C6/D15) | sixthshop_scores.jsonl | 2026-04-24 |
| Phase B1 본실험 | ✅ 1,920 호출 / $11.48 / 2026-04-25 완료 | ml/data/b1_runs/ | 2026-04-25 |
| **B1 결과 — 의료기기 페이지 incremental** | **+4.2%p** (open 21% → closed 25%) | F2026-04-25_phase_b1_main_results | 2026-04-25 |
| **B1 결과 — 가글 페이지 incremental** | **+12.3%p** (open 17% → closed 29%) | (3배 효과 — 가글 시급성 ↑) | 2026-04-25 |
| 산공통 본실험 예정 비용 (보류) | $108 (gpt-5.4 8,640 호출) + $3.4 파일럿 | experiment_design.md | — |
| **NAVER 외부 증거 (H14)** | ✅ **키 확보 + 60 키워드 매핑 완료** (이전 "키 대기" 정정) | data/processed/naver_search_volume.json | 2026-04-30 |
| 노션 자동 적층 | ✅ 11 카드 (PostToolUse hook) | .claude/.notion_logged_commits.txt | 2026-04-30 |

---

## 🧪 가설 상태

| ID | 한 줄 요약 | 상태 |
|---|---|---|
| H1 | HTML 포맷이 파싱 정확도 | 🟡 미검정 |
| H2 | JSON-LD가 파싱 정확도 | 🟡 미검정 |
| H3 | F1×F2 교호작용 | 🟡 미검정 |
| H4 | 수치 구체성이 파싱 | 🟡 미검정 |
| **H5** | **인증 명시가 추천 ↑** | 🟡 미검정 — **kGoal "인증 0인데 LLM 10 mention" 반례 자료** (2026-04-30 발견) |
| H6 | 인증 명시가 Y4 회피 ↓ | 🟡 미검정 |
| H7 | 임상 인용 > 후기 | 🟡 미검정 |
| H8 | Y1 ≠ Y2 (GEO ≠ AiEO) | 🟡 미검정 |
| H9 | 경쟁 상황에서 구조화 ↑ | 🟡 미검정 |
| **H10** | AI는 의료/비의료 구분 못 함 | 🟢 **Phase B1 강력 지지** (Elvie 한국 18 vs LLM 44) |
| H11 | "의료기기" 명시 시 카테고리 좁힘 | 🟡 미검정 |
| H12 | Rufus SPN (USE × F6) 교호작용 | 🟡 미검정 |
| ~~H13~~ | (드롭) Rich card | ❌ |
| **H14** | 외부 증거가 추천 ↑ | 🟢 **B1 강력 지지** (글로벌 mention 한국 검색 481배 격차) |
| H15 | 쿼리 × F 교호작용 | 🟡 미검정 |

---

## 🏢 경쟁사 진단 (직접 경쟁 = 같은 효능)

> 식약처 등급 무관, *같은 효능을 주는 모든 제품* 이 직접 경쟁 (Wayne 정의).
> 자체 페이지 생성된 9개 + 풀 메타에만 있는 것 1줄.

### 의료기기 vertical (바디닥터K anchor)

| 브랜드 | 자체 페이지 | 식약처 | 같은 효능? | 본실험 우선순위 |
|---|---|---|---|---|
| 바디닥터 (anchor) | [bodydoctor.md](competitors/bodydoctor.md) | 3등급 | anchor | anchor |
| 이지케이 (EASY-K) | [easyk.md](competitors/easyk.md) | 3등급 (제허 15-329) | ✅ | 필수 |
| 코웨이 테라솔 | [coway_therasol.md](competitors/coway_therasol.md) | 3등급 (제허 25-725) | ✅ | 필수 (현재 검색 미정착) |
| **세라젬 이너핏 (NEW)** | [ceragem_innerfit.md](competitors/ceragem_innerfit.md) | 검증 필요 | ✅ | **필수 (대기업 인지도 강)** |
| 퓨런헬스케어 | [furun.md](competitors/furun.md) | 3등급 (제허 21-492) | ✅ but 자사몰 B2B | EXPLORATORY |
| 글로벌 4종 | | | | |
| Elvie Trainer | [elvie.md](competitors/elvie.md) | FDA Class II | ✅ | 한국 검색 zero, LLM mention 강 (H10) |
| Perifit | [perifit.md](competitors/perifit.md) | FDA 510(k) K221476 | ✅ | LLM mention 강 (H10) |
| Kegel8 | [kegel8.md](competitors/kegel8.md) | UK CE Class IIa | ✅ | secondary |
| **kGoal** | [kgoal.md](competitors/kgoal.md) | **FDA general wellness — 의료기기 아님** | ✅ (효능 같음) | **★ H5 반례 자료** |
| 비의료 노이즈 | | | | |
| 페로니언 (NEW) | [peroneun.md](competitors/peroneun.md) | 미등록 | ✅ (마케팅) | H10 검정 |
| 애플힙 | [applehip.md](competitors/applehip.md) | 미등록 | ✅ (마케팅) | H10 검정 |
| 훌스 | [hools.md](competitors/hools.md) | 미등록 | ✅ (마케팅) | H10 검정 |
| 스탑요 | [stopyo.md](competitors/stopyo.md) | 미등록 | ✅ (마케팅) | H10 검정 (크롤 차단) |
| 풀 메타 | [_medical_device_oem_pool.md](competitors/_medical_device_oem_pool.md) / [_non_medical_products_pool.md](competitors/_non_medical_products_pool.md) | — | — | 메타 분류 정보 |

### 가글 vertical (프로폴린스 anchor)

| 브랜드 | 자체 페이지 | 같은 효능? | 한국 진출 |
|---|---|---|---|
| 프로폴린스 (anchor) | [propolinse.md](competitors/propolinse.md) | anchor | anchor |
| 리스테린 | [listerine.md](competitors/listerine.md) | ✅ | 정식 |
| 가그린 | [garglin.md](competitors/garglin.md) | ✅ | 한국 브랜드 |
| 페리오 | [perio.md](competitors/perio.md) | ✅ | 한국 브랜드 |
| 2080 | [2080.md](competitors/2080.md) | ✅ | 한국 브랜드 (가장 강자, NAVER 559k) |
| **테라브레스 (NEW)** | [therabreath.md](competitors/therabreath.md) | ✅ | **한국판 = 가그린 처방으로 변형** (해외판 OXYD-8 식약처 미허가) |
| **콜게이트 플렉스 (NEW)** | [colgate_plax.md](competitors/colgate_plax.md) | ✅ | **한국 정식 진출 0** (모두 병행수입) |

### 가설 검증 실패 finding
- [F2026-04-30_awesome_cool_verification_failure.md](findings/F2026-04-30_awesome_cool_verification_failure.md) — 어썸쿨이 "글로벌 가글" 가설 거짓, 실제 (주)스터너즈 한국 D2C 신생. 메모리 룰 확장 사례.

---

## 📝 최근 발견 (2026-04-30 추가)

> 최신 6개. 전체는 `findings/` + INDEX.md.

- **2026-04-30**: [F2026-04-30_naver_search_insights.md](findings/F2026-04-30_naver_search_insights.md) — ★★★ NAVER 60 키워드 매핑 + 7개 충격 발견 (EASY-K 44배·코웨이 zero·바디닥터 481배·프로폴린스 267배 등)
- **2026-04-30**: [F2026-04-30_competitor_landscape_update.md](findings/F2026-04-30_competitor_landscape_update.md) — Profound 유니콘·Bluefish Fortune 500·JP/CN 신규 스캔·healthcare 글로벌 갭·인과 vs 관찰 framing
- **2026-04-30**: [F2026-04-30_awesome_cool_verification_failure.md](findings/F2026-04-30_awesome_cool_verification_failure.md) — 카테고리 가설 검증 실패 케이스
- 2026-04-25: [F2026-04-25_phase_b1_main_results.md](findings/F2026-04-25_phase_b1_main_results.md) — ★★★ B1 본실험 결과 (가글 +12.3%p / 의료 +4.2%p)
- 2026-04-25: [F2026-04-25_data_reliability_assessment.md](findings/F2026-04-25_data_reliability_assessment.md) — 데이터 신뢰도 평가
- 2026-04-24: [F2026-04-24_listerine_furun_selfmall_measured.md](findings/F2026-04-24_listerine_furun_selfmall_measured.md) — curl_cffi 크롤 성공

---

## 🤖 자동화 인프라 (2026-04-30 신설)

| 인프라 | 파일 | 상태 |
|---|---|---|
| Notion 자동 적층 | [scripts/notion_log_commit.py](../../scripts/notion_log_commit.py) + .claude/settings.json hook | ✅ 작동 (PostToolUse hook). 모든 git commit 자동 Work Log 카드 |
| 주간 AiEO 모니터링 | [scripts/monitor_aieo.py](../../scripts/monitor_aieo.py) | ⚠️ 미설치 (수동 실행 가능 / launchd 미등록) |
| launchd 정의 | [scripts/com.aieo.monitor.plist](../../scripts/com.aieo.monitor.plist) | ⚠️ 미설치 — `launchctl load ~/Library/LaunchAgents/com.aieo.monitor.plist` 으로 활성 |

---

## 🔴 Active Conflicts (모순/미해결)

- ✅ 해결: 바디닥터 인증 등급 (식약처 3등급 + FDA 1+2)
- ✅ 해결: 이지케이 = 알파메딕 EASY-K
- ✅ 해결: NAVER 키 확보 + 매핑 완료 (이전 "키 대기" 정정)
- ⚠️ **세라젬 이너핏 허가번호 매칭 미확정** — 제허 23-785 (2023-07-17) vs 출시일 2024-04-16. udiportal 재조회 필요
- ⚠️ 식약처 OpenAPI endpoint 일부 endpoint 500 — Wayne 추가 발급 권장

---

## 🛠️ 적용된 방법

- [orthogonal_array_L54.md](methods/orthogonal_array_L54.md) ★ — L54 직교배열 확정 (현재 사용)
- [experiment_design.md](methods/experiment_design.md) ★ — 본실험 설계
- ~~orthogonal_array_L36.md~~ — L54로 대체됨 (이전 버전)
- [sample_size_justification.md](methods/sample_size_justification.md)
- [synthetic_pages_design.md](methods/synthetic_pages_design.md)

---

## 🚧 Active Actions (Wayne / 팀)

### 🔴 P0 — 즉시 (Wayne 24~48시간)
- [ ] **노션 11개 카드 확인** (이번 세션 자동 적층 결과)
- [ ] **FAQ 자료 요청 메일 발송** ([gn_requests_FAQ_data.md](../../consulting/gn_requests_FAQ_data.md)) — 모든 컨설팅 후속의 트리거
- [ ] **세라젬 이너핏 허가번호 udiportal 재조회** — 30분 작업
- [ ] **기존 GN P0 응답 follow-up** ([gn_requests.md](../../consulting/gn_requests.md))

### 🟡 P1 — 1주 내
- [ ] PDP 카피 v1 (TBD 채워넣기) — GN P0 응답 후
- [ ] external_evidence 25 브랜드 수집 실행 (D2) — NAVER 키 OK이므로 즉시
- [ ] 의료감수 파트너 섭외
- [ ] 시딩 캠페인 예산 GN 협의

### 🟠 P2 — 다음 결정 분기점
- [ ] **산공통 보류 해제 여부 결정** — 학기 우선순위 + GN timing
- [ ] propolinse / perio / stopyo 처리 결정
- [ ] kGoal "인증 0 + LLM 10 mention" 사례를 H5 분석에 명시 포함

### 🔵 인프라·유지보수
- [ ] DIGEST.md 매주 금요일 갱신 의식 (자동 스케줄 검토)
- [ ] 모니터링 cron launchd 설치 (`launchctl load ~/Library/LaunchAgents/com.aieo.monitor.plist`)
- [ ] **분기 모니터링 2026-07-30**: 코웨이 테라솔 검색량 / AMP·ACP / Conductor MCP / 한국 healthcare GEO 신규 entry

---

## 📚 빠른 링크

- **이거 다 읽고 시작 → [CLAUDE.md](../../CLAUDE.md)** (작업 가이드)
- 학술 마스터: [PROJECT_MASTER.md](../PROJECT_MASTER.md)
- **컨설팅 12주 로드맵**: [consulting/action_roadmap.md](../../consulting/action_roadmap.md) ★
- **핵심 페르소나** (NEW): [consulting/personas/핵심_페르소나.md](../../consulting/personas/핵심_페르소나.md) ★
- **팀 네이밍 규칙** (NEW): [팀_네이밍_규칙.md](팀_네이밍_규칙.md) ★ — 신규 팀원 첫 5분
- 용어: [glossary.md](glossary.md)
- GN 요청 리스트: [consulting/gn_requests.md](../../consulting/gn_requests.md) + [gn_requests_FAQ_data.md](../../consulting/gn_requests_FAQ_data.md)
- 갱신 의식 워크플로우: [workflows/weekly_digest_update.md](../workflows/weekly_digest_update.md)
- 트렌드 적용 설계: [trends_2026/APPLICATION.md](../trends_2026/APPLICATION.md)
- 업계 리서치: [F2026-04-30_competitor_landscape_update.md](findings/F2026-04-30_competitor_landscape_update.md) (최신) + [AiEO_경쟁사_리서치.md](findings/AiEO_경쟁사_리서치.md) (선행)
- NAVER 검색 인사이트: [F2026-04-30_naver_search_insights.md](findings/F2026-04-30_naver_search_insights.md)
