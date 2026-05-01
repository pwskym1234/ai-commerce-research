# methods/ — 방법론 문서

차원 정의·실험 설계·팀 운영 절차를 담는 디렉토리. 분류:

## 🔬 학술 / 실험 설계

| 파일 | 내용 |
|---|---|
| [experiment_design.md](experiment_design.md) | 본실험 설계 (현재 사용) — L54 + 8 쿼리 유형 + Y1~Y7 + H1~H15 |
| [orthogonal_array_L54.md](orthogonal_array_L54.md) | L54 다구치 직교배열 (확정, 현재 사용) |
| [orthogonal_array_L36.md](orthogonal_array_L36.md) | L36 (이전 버전, L54로 대체) |
| [sample_size_justification.md](sample_size_justification.md) | 표본 크기 정당화 (N=6 등) |
| [synthetic_pages_design.md](synthetic_pages_design.md) | 가상 페이지 제작 가이드 (Jinja2 + F1~F6 변형) |
| [query_realism_plan.md](query_realism_plan.md) | 쿼리 자연성 보강 plan |
| [h_taxonomy_to_tagging_mapping.md](h_taxonomy_to_tagging_mapping.md) | H 가설 → 태깅 차원 매핑 |

## 🏷️ 태깅·검수

| 파일 | 내용 |
|---|---|
| [manual_tagging_guide.md](manual_tagging_guide.md) | 페이지 정성 차원 정의 (T·Q·M·G 39 차원) |
| [수동태깅_팀_분배_및_절차.md](수동태깅_팀_분배_및_절차.md) | 페이지 X 변수 — 7명 분담 + Google Sheets 워크플로우 |
| [Y변수_프롬프트_검수_분배_및_절차.md](Y변수_프롬프트_검수_분배_및_절차.md) | 응답 Y 변수 — 7명 × Claude 일치도 검수 |

## 분류

- **학술/실험 설계**: 산공통 본실험·가설 검정에 사용. 기존 영어 파일명.
- **태깅·검수**: 팀 운영 (분담·절차). 한국어 파일명 — 신규 팀원 진입 시 직관성 우선 ([팀_네이밍_규칙](../팀_네이밍_규칙.md) Rule 5).

## 어디부터 봐야?

| 역할 | 시작 |
|---|---|
| 산공통 팀 | experiment_design.md → orthogonal_array_L54.md → synthetic_pages_design.md |
| 데마 팀 | manual_tagging_guide.md (차원 정의) → 수동태깅_팀_분배_및_절차.md (자기 분담) |
| Y 변수 검수 | Y변수_프롬프트_검수_분배_및_절차.md |
| 신규 팀원 (전체 입문) | manual_tagging_guide.md + 본인 분담 한 가지 절차 |

## 관련 문서

- [docs/knowledge/glossary.md](../glossary.md) — 모든 코드 (F·H·Y·R·BRD·CAT 등) 한 줄 정의
- [docs/knowledge/팀_네이밍_규칙.md](../팀_네이밍_규칙.md) — 파일명·약어 사용 규칙
- [docs/knowledge/DIGEST.md](../DIGEST.md) — 현재 상태 + 최신본 인덱스
