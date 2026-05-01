# AiEO 프로젝트

> AI 에이전트가 상품을 추천할 때, 상품 페이지의 어떤 요소가 추천에 영향을 미치는가?

산업공학통계 + 데이터마이닝 두 과목의 팀 프로젝트를 AiEO(AI Engine Optimization) 연구 파이프라인으로 통합 진행하는 레포. 실제 고객사: GN그룹/바디닥터.

---

## 🚀 빠른 시작 — 새 팀원 5분 가이드

| # | 무엇을 | 어디 |
|:-:|---|---|
| 1 | **현재 상태·최신본** 파악 | [docs/knowledge/DIGEST.md](docs/knowledge/DIGEST.md) ★ |
| 2 | **프로젝트 마스터** (학술 정합) | [docs/PROJECT_MASTER.md](docs/PROJECT_MASTER.md) |
| 3 | **작업 가이드 + 재현성 룰** | [CLAUDE.md](CLAUDE.md) |
| 4 | **네이밍 규칙** (v0.1·BRD·F2 같은 코드 해석) | [docs/knowledge/팀_네이밍_규칙.md](docs/knowledge/팀_네이밍_규칙.md) ★ |
| 5 | **용어 사전** | [docs/knowledge/glossary.md](docs/knowledge/glossary.md) |
| 6 | **AI 도구 활용** | [docs/AGENTS_AND_SKILLS.md](docs/AGENTS_AND_SKILLS.md) |

---

## 📁 디렉토리 구조

```
bodydoctor_project/
├── docs/                  ← 프로젝트 문서·지식베이스 (DIGEST·PROJECT_MASTER·findings)
├── data/                  ← raw/ (크롤링 원본) + processed/ (정제본)
├── experiments/           ← 산공통: 가상 페이지·쿼리셋·API 러너
├── crawler/               ← 사이트별 크롤러
├── stats/                 ← 산공통 (가설검정·로지스틱 — 보류 중)
├── ml/                    ← 데마 (XGBoost·SHAP·B1 결과)
├── consulting/            ← GN 컨설팅 산출물·페르소나·PDP 카피
├── scripts/               ← 인프라 스크립트 (Notion 적층·NAVER·JSON-LD·monitoring)
└── presentations/         ← 발표 자료
```

각 디렉토리 README: [`docs/knowledge/README.md`](docs/knowledge/README.md) · [`consulting/README.md`](consulting/README.md) · [`ml/README.md`](ml/README.md) · [`scripts/README.md`](scripts/README.md)

자세한 데이터·시크릿 관리 룰: [CLAUDE.md §2 + §8](CLAUDE.md)

---

## 🎯 현재 상태 (2026-04-30)

**우선순위**: 데마 + 컨설팅 (Phase A~D). 산공통 보류 중.

| 트랙 | 상태 |
|---|---|
| 데마 Phase B1 본실험 (재실행, 페르소나 stratified 32 쿼리) | ✅ 2,560 호출 완료, 페이지 incremental 의료 +10.9%p / 가글 +19.1%p |
| 컨설팅 12주 로드맵 + 페르소나 정의 + PDP 카피 초안 | ⚠️ GN P0 응답 대기 |
| 수동 페이지 태깅 (X 변수, 7명 분담) | ⏳ Wayne Sheet 셋업 후 시작 |
| Y 변수 Claude 일치도 검수 (7명 × 1 Y) | ⏳ 보조 스크립트 작성 후 시작 |
| 자동화 (Notion 적층·주간 모니터링) | ✅ Notion 적층 작동 / 모니터링 cron 미설치 |

---

## 🛠️ 자주 쓰는 액션

| 작업 | 명령 |
|---|---|
| 본실험 재실행 (의료 open) | `python3 ml/scripts/run_b1_async.py --mode open --vertical medical_device --budget 3` |
| NAVER 검색 데이터 수집 | `python3 scripts/naver_keyword_mapping.py` |
| 바디닥터 JSON-LD 풀스키마 생성 | `python3 scripts/generate_jsonld_bodydoctor.py` |
| 주간 AiEO 모니터링 (수동) | `python3 scripts/monitor_aieo.py` |
| Notion Work Log 자동 적층 | `git commit` (PostToolUse hook 자동) |

---

## 👥 팀

- **방우식 (Wayne)**: 양쪽 조율 + 실험 설계 + 컨설팅 연결 + 검수
- **박지윤·이소현·이경민·박재후·이재현·최지혜**: 분담 (자세히는 [수동태깅_팀_분배_및_절차](docs/knowledge/methods/수동태깅_팀_분배_및_절차.md) + [Y변수_프롬프트_검수_분배_및_절차](docs/knowledge/methods/Y변수_프롬프트_검수_분배_및_절차.md))

---

## 환경 설정

```bash
# Python 3.11+
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# .env 생성 (API 키)
cp .env.example .env
# OPENAI_API_KEY, ANTHROPIC_API_KEY, NAVER_*, NOTION_* 등
```

---

## 기여 룰

- PR 단위는 한 가지 일만. 영역 prefix (`[산공통]`, `[데마]`, `[컨설팅]`, `[인프라]`, `[docs]`)
- *최신* 파일 라벨링: `_최종`. 이전 버전은 `_보존` 또는 의미 접미사 ([팀_네이밍_규칙.md Rule 6](docs/knowledge/팀_네이밍_규칙.md))
- 코드는 영어 식별자, 문서는 한국어 첫 등장 풀이름
- 자세히는 [CLAUDE.md §11](CLAUDE.md)
