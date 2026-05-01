# consulting/ — 컨설팅 산출물·도구

GN그룹/바디닥터 측 컨설팅 트랙. 데마(`ml/`)·산공통(`stats/`)과 별개로 운영.

## 구성

| 항목 | 설명 |
|-----|----|
| `action_roadmap.md` | ★ 바디닥터 AiEO 12주 실제 개선 액션 로드맵 (Profound·Alhena·체인시프트 참조 + Stage 1~6) |
| `dashboard_upgrade_spec.md` | 친구 대시보드 기반 업그레이드 spec |
| **`personas/`** | ★ 핵심 유저 페르소나 정의 (산후 회복기 / 갱년기 / 잇몸 약함 / 모유수유 등) |
| **`gn_communication/`** | GN 본사 커뮤니케이션 — 요청 리스트·승인 메일·FAQ 자료 요청 |
| `diagnosis/` | 브랜드별 페이지 실측 진단 + 바디닥터 JSON-LD 풀스키마 + PDP 카피 초안 (의료·가글) |
| `reports/` | 최종 컨설팅 리포트 (앞으로) |
| **`aao-gn/`** | **상균이 운영 GEO 감사 파이프라인 + Next.js 대시보드** (별도 트랙) |

## 🎯 어디부터 봐야?

| 목적 | 시작 |
|---|---|
| 컨설팅 큰 그림 + 12주 일정 | `action_roadmap.md` |
| 바디닥터 페이지 개선안 | `diagnosis/bodydoctor_pdp_copy_초안.md` + `diagnosis/bodydoctor_jsonld.json` |
| 프로폴린스 시딩 캠페인 | `diagnosis/propolinse_pdp_copy_초안.md` (30/60일 맘카페 시딩 plan) |
| GN 본사에 보낼 메일 | `gn_communication/gn_requests_FAQ_data.md` (FAQ 자료 요청) |
| 페르소나 (PDP·FAQ·시딩 디자인 기준) | `personas/핵심_페르소나.md` |

## 정책 차이 — 데마 vs aao-gn

| | 데마 (`ml/`) | aao-gn (`consulting/aao-gn/`) |
|--|----------|----|
| 모델 | `gpt-5.4-mini` (web browsing X) | `gpt-4o-search-preview` (web search 활성) |
| 페이지 입력 방식 | 우리가 직접 페이지 텍스트 컨텍스트 주입 | 모델 자체 web search로 fetch (실제 AI agent 동작) |
| 반복 횟수 | **20회** (CLAUDE.md §4 R1 통계 안정성) | **REPEAT_COUNT=2** (컨설팅 baseline 측정용, 비용·속도 우선) |
| 두 모드 (open/closed) | ✅ 둘 다 | closed만 (web search로) |
| Y 변수 | mention/sentiment/wintieloss/rank 등 멀티 | NEUTRAL 랭킹·H2H·COMP_ONLY 카테고리별 비율 |
| 분석 단위 | 페이지 단위 X-Y 매트릭스 | 브랜드 단위 카테고리별 점유율 |
| 용도 | 학기 학술 분석 모델·SHAP·Tier | GN 측 컨설팅 baseline·대시보드 보고 |

→ **두 트랙은 같은 brand 데이터를 보지만 분석 목적·통계 정책이 달라 서로 직접 비교 X**.
교차 분석은 별도 finding으로 (예: "데마 SHAP top X ↔ aao-gn NEUTRAL 랭킹 일관성").

## aao-gn 사용

```bash
cd consulting/aao-gn
cat README.md  # 자세한 사용법
```

자세히는 `consulting/aao-gn/README.md` 와 `consulting/aao-gn/docs/` 참조.

미정 후속 (commit 메시지 기록):
- `pipeline/config.py` 패턴 → 루트 `.env` + python-dotenv 마이그레이션 검토
- 데마 R1=20과 aao-gn REPEAT_COUNT=2 정합성 — 현재는 별도 운용
