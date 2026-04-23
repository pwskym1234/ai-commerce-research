# 에이전트 & 스킬 활용 가이드

> AiEO 프로젝트에서 Claude Code의 서브 에이전트와 스킬을 어떻게 쓸지 정리한 문서.
> 모든 도구를 다 쓸 필요는 없다. **이 프로젝트에서 실제로 도움 되는 것만** 큐레이션.

---

## 1. 서브 에이전트 (Subagents)

서브 에이전트는 메인 컨텍스트를 보호하면서 병렬/특수 작업을 수행한다.

| 에이전트 | 언제 쓰나 | 예시 |
|---------|----------|------|
| **Explore** | 빠른 코드/문서 탐색 (3쿼리 이상) | "크롤러 스크립트 중에 네이버 스마트스토어 처리하는 게 있나?", "F1~F6 변형이 적용된 가상 페이지가 어디에?" |
| **Plan** | 비자명한 구현 전 설계 | "L18 직교배열로 가상 페이지 18개 자동 생성하는 시스템 설계", "오픈엔드 vs 클로즈드셋 비교 실험 파이프라인 설계" |
| **general-purpose** | 광역 리서치, 다단계 조사 | "케겔운동기 경쟁사 5곳 리스트업 + 각 사이트 페이지 구조 조사", "한국 의료기기 인증 표기 규제 조사" |
| **claude-code-guide** | Claude Code 자체 사용법 | "hooks로 PR 푸시 전 재현성 룰 자동 체크하려면?" |
| **statusline-setup** | 상태 표시줄 커스텀 (선택) | 거의 안 씀 |

**병렬 실행 전략**:
- 의료기기 경쟁사 5곳을 동시에 리서치할 때: 한 메시지에 5개 `general-purpose` 호출
- 산공통/데마/크롤러 3축을 동시에 조사할 때: 한 메시지에 3개 `Explore` 호출

**위임하지 말아야 할 것**:
- 통계/ML 분석의 결과 해석 — Wayne이 직접 봐야 의사결정 가능
- 컨설팅 리포트 최종 톤 조정 — 사람이 다듬어야 함
- 실험 재현성 룰 위반 여부 판단 — 명시적 체크리스트로 메인이 직접

---

## 2. 스킬 (Skills) — 권장

`/<skill-name>` 형식으로 호출. 본 프로젝트에서 유용할 것들.

### 2.1 항상 켜두면 좋은 것

| 스킬 | 용도 | 트리거 예시 |
|------|------|------|
| `/investigate` | 버그/이상 결과 root cause 분석 | "왜 H3 교호작용이 음의 계수가 나오지?", "크롤링이 특정 페이지에서만 빈 결과" |
| `/review` | PR 머지 전 코드 리뷰 | "이 통계 분석 코드 머지 전에 봐줘" |
| `/codex` | OpenAI Codex로 second opinion | "이 로지스틱 회귀 모델링에 빠진 게 있나 codex에 물어봐" |
| `/checkpoint` | 작업 중단점 저장/재개 | 발표 직전 작업 컨텍스트 보존 |
| `/learn` | 프로젝트 학습 누적 관리 | "지금까지 어떤 분석 패턴을 학습했나" |

### 2.2 특정 단계에서 유용

| 단계 | 스킬 | 용도 |
|------|------|------|
| 실험 설계 / 가설 검토 | `/plan-eng-review` | "직교배열 설계 + API 실험 파이프라인 아키텍처 리뷰" |
| 가설 톤 검토 | `/plan-ceo-review` | "이 가설셋이 산공통 교수 + 컨설팅 양쪽 모두에 임팩트가 있나" |
| 발표 자료 시각 검토 | `/design-review`, `/plan-design-review` | 발표 슬라이드 디자인 폴리시 |
| 발표 시뮬레이션 | `/office-hours` | "이 발표를 처음 듣는 교수가 이해할 수 있나" |
| 크롤러/페이지 QA | `/qa`, `/browse`, `/gstack` | 크롤링 결과 검증, 가상 페이지가 의도대로 렌더링되는지 |
| 보안 점검 | `/cso`, `/security-review` | API 키 노출, 크롤링 robots.txt 준수 |
| GitHub 워크플로우 | `/ship`, `/land-and-deploy` | PR 생성/머지/배포 자동화 |
| 사후 분석 | `/retro` | 매주 작업 회고 |

### 2.3 LLM API 작업 전용

| 스킬 | 용도 |
|------|------|
| `/claude-api` | Anthropic API 호출 코드 작성/캐싱 최적화 — Anthropic 모델 실험 추가 시 |
| `/loop` | 폴링형 백그라운드 작업 — 장시간 API 실험 모니터링 시 (단, 본 실험은 보통 batch로 충분) |
| `/schedule` | cron 기반 스케줄 — 일별 크롤링 자동화 |

### 2.4 본 프로젝트와 무관 (사용 X)

- `/edu-*` (교육 사이트 전용)
- `/design-html`, `/design-shotgun`, `/design-consultation` (디자인 사이트 제작 전용)
- `/setup-deploy`, `/canary` (배포 모니터링 — 연구 레포에 불필요)
- `/freeze`, `/unfreeze`, `/guard`, `/careful` (편집 잠금 — 1인 개발자 모드. 팀 작업엔 PR/리뷰가 우선)
- `/gstack-upgrade`, `/setup-browser-cookies` 등 환경 셋업 도구

---

## 3. MCP 서버

| 서버 | 활용 |
|------|------|
| Notion (`mcp__claude_ai_Notion__*`) | 팀 회의록/리서치 노트가 Notion에 있으면 fetch/search로 동기화 |
| Gmail (`mcp__claude_ai_Gmail__*`) | GN그룹 컨택, 발표 일정 메일 검색 (조심해서) |
| Google Drive | 발표자료 공유 시 (수업 제출용) |
| Google Calendar | 발표 일정 확인 |
| Figma | 발표 슬라이드 디자인 — 굳이 안 써도 됨 |

**원칙**: 외부 SaaS 동기화는 Wayne이 명시적으로 요청할 때만. 자동 조회 금지.

---

## 4. 자주 쓰게 될 워크플로우 매핑

### 워크플로우 A: 새 가설 추가
1. `Explore` (medium) — 기존 가설 코드/문서 탐색
2. `/plan-eng-review` — 새 가설 검정 설계 검토
3. PROJECT_MASTER.md §4.4와 `stats/results/preregistered_hypotheses.md` 업데이트
4. PR 생성 (`/ship`)

### 워크플로우 B: 새 경쟁사 추가
1. `general-purpose` — 경쟁사 사이트 구조 조사
2. `crawler/scripts/` 에 새 크롤러 작성
3. `/qa` 또는 `/browse` — 크롤러 결과 검증
4. `data/raw/` 에 저장 → `/review` 후 PR

### 워크플로우 C: API 실험 본실행
1. 파일럿(R9) 결과 확인
2. `experiments/api_runs/<date>/` 디렉토리 생성
3. 백그라운드 실행 (`run_in_background: true`)
4. 실행 후 jsonl 검증: 모델 버전·시드·반복 횟수 누락 체크
5. `/investigate` — 이상 패턴 발견 시

### 워크플로우 D: 발표 직전 점검
1. `/checkpoint` — 현재 상태 저장
2. `/plan-design-review` — 슬라이드 디자인
3. `/office-hours` — 1차 청중 시뮬레이션
4. `/codex` — 예상 질문 brainstorm
5. PROJECT_MASTER.md §9.4 예상 질문 카드 업데이트

### 워크플로우 E: 컨설팅 리포트 생성
1. ML SHAP 결과 + 산공통 odds ratio를 input으로
2. `consulting/diagnosis/bodydoctor_k_<date>.md` 작성
3. 경쟁사 동일 기준 비교표 추가 (마스터 §7.3)
4. `/review` 후 GN그룹 전달용 정리

---

## 5. 유의사항

- 스킬 호출은 **유용할 때만**. 작업과 매칭 안 되면 일반 도구가 더 빠름.
- 서브 에이전트에게 "결정"을 위임하지 말 것. 사실 수집/탐색만 위임.
- LLM API 키 등 시크릿 — 어떤 에이전트에도 절대 전달 금지.
- 외부 시스템(Notion, Gmail) 쓸 때는 사용자 확인 후.
