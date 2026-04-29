# consulting/ — 컨설팅 산출물·도구

GN그룹/바디닥터 측 컨설팅 트랙. 데마(`ml/`)·산공통(`stats/`)과 별개로 운영.

## 구성

| 항목 | 설명 |
|-----|----|
| `action_roadmap.md` | 바디닥터 AiEO 실제 개선 액션 로드맵 (Profound·Alhena·체인시프트 참조) |
| `gn_requests.md` | GN 본사 요청 리스트 (P0: 바디닥터 실제 제조사 확인 등) |
| `dashboard_upgrade_spec.md` | 친구 대시보드 기반 업그레이드 spec |
| `diagnosis/` | 브랜드별 페이지 실측 진단 JSON (furun, listerine 등) |
| `reports/` | 최종 컨설팅 리포트 (앞으로) |
| **`aao-gn/`** | **상균이 운영 GEO 감사 파이프라인 + Next.js 대시보드** (별도 트랙) |

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
