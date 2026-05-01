# scripts/ — 인프라 스크립트

프로젝트 *전체에 걸친* 인프라·자동화 스크립트. 데마(`ml/scripts/`)·산공통(`experiments/`)·크롤러(`crawler/scripts/`)와 별개.

## 구성

| 파일 | 역할 | 실행 |
|---|---|---|
| [generate_jsonld_bodydoctor.py](generate_jsonld_bodydoctor.py) | 바디닥터 요실금치료기 JSON-LD MedicalDevice 풀스키마 생성 | `python3 scripts/generate_jsonld_bodydoctor.py` |
| [naver_keyword_mapping.py](naver_keyword_mapping.py) | NAVER 검색 API + DataLab Trends로 한국 의료기기·가글 키워드 빈도 매핑 | `python3 scripts/naver_keyword_mapping.py` |
| [monitor_aieo.py](monitor_aieo.py) | 주간 AiEO 가시성 모니터링 (바디닥터·프로폴린스 시계열) | `python3 scripts/monitor_aieo.py` |
| [com.aieo.monitor.plist](com.aieo.monitor.plist) | macOS launchd 매주 월 03:00 자동 실행 정의 | `launchctl load ~/Library/LaunchAgents/com.aieo.monitor.plist` |
| [notion_log_commit.py](notion_log_commit.py) | git commit 후 Notion Work Log 카드 자동 생성 | PostToolUse hook 자동 (수동: `python3 scripts/notion_log_commit.py`) |

## 산출물 위치

| 스크립트 | 산출 |
|---|---|
| `generate_jsonld_bodydoctor.py` | `consulting/diagnosis/bodydoctor_jsonld.json` + snippet.html |
| `naver_keyword_mapping.py` | `data/processed/naver_search_volume.json` + `.md` |
| `monitor_aieo.py` | `experiments/monitoring/<run_id>/responses.jsonl` + `history.csv` |
| `notion_log_commit.py` | Notion Work Log DB 카드 (적층 SHA는 `.claude/.notion_logged_commits.txt`) |

## 환경 의존성

`.env`에 다음 키 필요:
- `OPENAI_API_KEY` (모니터링)
- `NOTION_API_KEY`, `NOTION_WORK_DB_ID` (Notion 적층)
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` (검색 매핑)

## 자동화 hook

- **`git commit` 후 자동 발화**: `.claude/settings.json`의 PostToolUse hook이 [notion_log_commit.py](notion_log_commit.py) 호출 → Notion 카드 생성
- **카테고리 추론**: 변경 파일 경로로 (`stats/`→산공통 / `ml/`→데마 / `consulting/`→컨설팅 / 그 외→공통/인프라)
- **옵트아웃**: commit message 본문에 `[skip-notion]` 단독 라인

## 관련 문서

- [CLAUDE.md §13 Notion 적층 자동화](../CLAUDE.md)
- [docs/knowledge/findings/F2026-04-30_naver_search_insights.md](../docs/knowledge/findings/F2026-04-30_naver_search_insights.md) — naver_keyword_mapping 산출 인사이트
- [consulting/diagnosis/bodydoctor_jsonld.json](../consulting/diagnosis/bodydoctor_jsonld.json) — generate_jsonld 산출
