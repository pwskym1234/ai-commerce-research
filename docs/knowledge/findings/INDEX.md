# Findings 인덱스

> 모든 finding을 트랙·날짜 별로 분류. 신규 finding 추가 시 본 인덱스도 갱신.

## 데마 트랙 (ml/)

| 날짜 | 파일 | 한 줄 |
|-----|----|----|
| 2026-04-25 | [F2026-04-25_phase_b1_main_results.md](F2026-04-25_phase_b1_main_results.md) | ★ Phase B1 본실험 결과 — 페이지 제공의 incremental 효과 (가글 +12.3%p, 의료 +4.2%p) |
| 2026-04-25 | [F2026-04-25_data_reliability_assessment.md](F2026-04-25_data_reliability_assessment.md) | 47 SKU 표본 한계·보완책 (Bootstrap CI, 추가 크롤 권장) |
| 2026-04-24 | [F2026-04-24_friend_dashboard_review.md](F2026-04-24_friend_dashboard_review.md) | 친구 대시보드 NER 교훈 — Y2a 5분화·가글 풀 확장 근거 |
| 2026-04-24 | [F2026-04-24_dema_order_correction.md](F2026-04-24_dema_order_correction.md) | 데마 분석 순서 정정 (관측형 호출 → SHAP 모델링) |
| 2026-04-24 | [F2026-04-24_listerine_furun_selfmall_measured.md](F2026-04-24_listerine_furun_selfmall_measured.md) | curl_cffi 4차 WAF 우회 — 리스테린·퓨런 자사몰 실측 |
| 2026-04-24 | [F2026-04-24_feature_comparison.md](F2026-04-24_feature_comparison.md) | Playwright + 11 피처 실측 비교 |
| 2026-04-24 | [F2026-04-24_mfds_oem_pool.md](F2026-04-24_mfds_oem_pool.md) | 식약처 API endpoint 확정 + 13 OEM 풀 |
| 2026-04-23 | [F2026-04-23_competitor_initial_research.md](F2026-04-23_competitor_initial_research.md) | 1차 경쟁사 조사 + 의료기기 2층 구조 |
| 2026-04-23 | [F2026-04-23_empty_product_pages.md](F2026-04-23_empty_product_pages.md) | 바디닥터·이지케이 단독 페이지 등급/허가/임상 정보 부재 |
| 2026-04-23 | [F2026-04-23_same_grade_competition.md](F2026-04-23_same_grade_competition.md) | 식약처 3등급 동급 경쟁군 N=6 권고 |
| 2026-04-24 | [F2026-04-24_listerine_furen_status.md](F2026-04-24_listerine_furen_status.md) | (구버전 — measured.md 로 대체됨) |

## 산공통 트랙 (stats/) — 보류 중

| 날짜 | 파일 | 한 줄 |
|-----|----|----|
| 2026-04-24 | [F2026-04-24_hypothesis_upgrade.md](F2026-04-24_hypothesis_upgrade.md) | 업계 리서치 반영 F/가설 고도화 (→ experiment_design 확정) |
| 2026-04-24 | [F2026-04-24_first_presentation_feedback_analysis.md](F2026-04-24_first_presentation_feedback_analysis.md) | 1차 발표 피드백 50+ 전수 분류 (P0/P1/P2) |

## 컨설팅 트랙 (consulting/)

| 날짜 | 파일 | 한 줄 |
|-----|----|----|
| 2026-04-24 | [F2026-04-24_wayne_diagnostic_vs_roadmap.md](F2026-04-24_wayne_diagnostic_vs_roadmap.md) | Wayne 진단 1,000건 실측 vs action_roadmap 비교 |

## 종합·로드맵 트랙

| 날짜 | 파일 | 한 줄 |
|-----|----|----|
| 2026-04-24 | [F2026-04-24_dm_consulting_priority_roadmap.md](F2026-04-24_dm_consulting_priority_roadmap.md) | 데마+컨설팅 우선 로드맵 (산공통 보류 결정) |
| 2026-04-24 | [F2026-04-24_both_projects_pivot.md](F2026-04-24_both_projects_pivot.md) | 본실험 설계 확정 후 산공통/데마 두 프로젝트 변경점 |
| 2026-04-24 | [F2026-04-24_week3_execution_plan.md](F2026-04-24_week3_execution_plan.md) | Week 3 실행 일정 (파일럿+본실험), critical path |

## 외부 리서치·landscape

| 파일 | 한 줄 |
|-----|----|
| [AiEO_경쟁사_리서치.md](AiEO_경쟁사_리서치.md) | AiEO 경쟁사 리서치 |
| [ai_product_visibility_landscape_2026-04-24.md](ai_product_visibility_landscape_2026-04-24.md) | AI 상품 가시성 landscape (Profound/Alhena/체인시프트) |

---

## 트랙별 신규 finding 추가 가이드

- 파일명: `F<YYYY-MM-DD>_<short_topic>.md`
- frontmatter `vertical:` 와 `phase:` 필수 (관례)
- 추가 후 본 INDEX.md 에 한 줄 추가
- 데마 팀원이 봐야 할 finding은 [ml/README.md](../../../ml/README.md) 의 "데마 결과 finding" 섹션도 같이 갱신
