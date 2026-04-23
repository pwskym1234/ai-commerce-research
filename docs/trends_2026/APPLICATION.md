# 트렌드 적용: AiEO 프로젝트에 어떻게 녹이는가

> [AI_TRENDS_2026.md](AI_TRENDS_2026.md) 글의 5가지 핵심 명제를 본 프로젝트에 적용하는 설계.
> 토큰 효율 + 복리로 쌓이는 컨텍스트 자산 = 같은 얘기. 미리 구조를 깔아둔다.

---

## 0. 한 문장 요약

이 글의 핵심: **"프롬프트 엔지니어링 → 컨텍스트 엔지니어링"**.
모델 옆에 놓이는 자산(메모리, 지식베이스, 워크플로우, 도구 하네스)이 매주 복리로 쌓이게 만들어야 한다.

---

## 1. 5가지 명제 → 프로젝트 매핑

| # | 글의 명제 | AiEO 프로젝트에서의 의미 | 적용 |
|---|----------|------------------------|------|
| 1 | 프롬프트 ≪ 컨텍스트 | "이 프로젝트가 뭔지" 매번 설명할 필요 없게, 한 번 잘 쓴 문서가 7주 내내 일한다 | `CLAUDE.md` + `docs/PROJECT_MASTER.md` (이미 함) |
| 2 | 에이전트식 코딩 | 코드 하나 짜는 게 아니라 "직교배열 → 가상 페이지 → API 실험 → 분석" 파이프라인을 위임 | `experiments/_runner.py` 같은 공유 하네스 + 서브에이전트 위임 |
| 3 | 오픈소스 에이전트 인프라 | 화려한 분석 전에 지루한 배관(재현성, 시드, 로깅, 캐싱) 먼저 | CLAUDE.md §4 재현성 룰 + 공유 헬퍼 |
| 4 | 카파시 위키 (복리 지식) | 매 실험 결과·경쟁사 조사·통계 발견을 한 곳에 적층 | `docs/knowledge/` 디렉토리 (지금 신설) |
| 5 | RAG 세 진영 | 우리는 어느 진영인가? → **Ragless** (지식 양 적당, 수동 유지 가능) | `docs/knowledge/DIGEST.md`를 항상 최신으로 유지 |

---

## 2. 토큰 효율을 위한 5가지 구조적 설계

### 2.1 캐시 친화적 문서 레이아웃

**원칙**: Anthropic 프롬프트 캐시는 5분 TTL. 매 세션 시작 시 같은 시스템 프롬프트 + `CLAUDE.md`를 읽는다. **자주 바뀌는 내용은 파일 끝에**, 안정된 원칙은 파일 앞에 두면 캐시 적중률 ↑.

**적용**:
- `CLAUDE.md` 앞부분(§0~§7)은 7주 내내 거의 안 바뀜 → 캐시됨
- 진행 상황·미확정 사항·새 발견은 `CLAUDE.md` 끝 또는 `docs/knowledge/DIGEST.md`에 누적 → 캐시 미스되어도 작은 영역만
- ❌ `CLAUDE.md` 앞부분을 자주 수정하면 매번 풀 재처리

### 2.2 메모리 vs 지식베이스 분리

| 레이어 | 위치 | 무엇이 들어가나 | 누가 읽나 |
|--------|------|--------------|----------|
| **메모리** (사용자별, 세션 간) | `~/.claude/.../memory/` | Wayne 프로필, 협업 선호, 프로젝트 핵심 사실 | Claude 자동 (MEMORY.md 항상 로드) |
| **프로젝트 지식베이스** (레포, 팀 공유) | `docs/knowledge/` | 경쟁사 분석, 실험 발견, 방법론 노트 | 사람 + Claude (필요 시 Read) |
| **메모리 인덱스** | `MEMORY.md` | 메모리 파일들의 원라이너 목록 | Claude 자동 (앞부분 200줄만 로드) |
| **지식 다이제스트** | `docs/knowledge/DIGEST.md` | 현재 상태 한눈에 (Ragless 핵심) | Claude가 매 작업 시작 시 Read |

**왜 분리?**: 메모리는 *Wayne만의* 영구 저장. 지식베이스는 *팀 공유*. 둘을 섞으면 팀원이 못 보거나, Wayne 개인 정보가 GitHub로 새거나.

### 2.3 서브에이전트 위임 = 컨텍스트 보호

큰 탐색·다중 파일 검색은 메인 컨텍스트에서 하지 말고 서브에이전트에게:

| 작업 | 메인이 하면 | 서브에이전트에게 | 토큰 절약 |
|------|------------|----------------|---------|
| 경쟁사 5곳 페이지 구조 조사 | 5×수만 토큰 누적 | `general-purpose` 5개 병렬, 보고서만 받음 | 80~90% |
| 100개 jsonl raw 응답 검토 | 메인 컨텍스트 폭발 | `Explore` agent에 "패턴 요약" 요청 | 95% |
| 코드베이스에서 특정 함수 찾기 | grep으로 충분 | (불필요) | — |

**판단 기준**: 결과만 알면 되는 일 = 서브에이전트. 코드를 직접 수정해야 하는 일 = 메인.

### 2.4 Raw 데이터는 절대 메인에 안 들어옴

| 데이터 | 위치 | 메인 컨텍스트 로드? |
|--------|------|----------------|
| 크롤링 raw HTML (수MB~) | `data/raw/` | ❌ 절대 |
| API 응답 jsonl (수만 줄) | `experiments/api_runs/` | ❌ 절대 |
| 학습된 모델 아티팩트 | `ml/models/` | ❌ |
| **요약 다이제스트** | `experiments/api_runs/<run_id>/SUMMARY.md` | ✅ |
| **EDA 리포트** | `data/processed/<dataset>/EDA.md` | ✅ |

**룰**: 모든 raw 산출물에 대해 자동/반자동으로 `SUMMARY.md`를 쓴다. Claude는 SUMMARY만 읽고 raw는 필요할 때만 부분 Read(`offset`/`limit`).

### 2.5 워크플로우 = 재사용 가능한 프롬프트

같은 작업을 두 번 이상 할 거라면 `docs/workflows/`에 템플릿화. 매번 "직교배열 만들고, JSON-LD 변형하고, ..." 다시 설명하지 말 것.

```
docs/workflows/
├── README.md              ← 워크플로우 인덱스
├── new_competitor.md      ← 새 경쟁사 추가
├── new_hypothesis.md      ← 새 가설 추가
├── pilot_run.md           ← 파일럿 실험
├── full_experiment.md     ← 본실험
├── consulting_report.md   ← 컨설팅 리포트 생성
└── presentation_prep.md   ← 발표 준비
```

각 템플릿: **목적 / 전제조건 / 단계 / 검증 체크리스트 / 호출할 스킬**.
Claude는 "워크플로우 X를 실행해줘"만 받으면 됨.

---

## 3. 카파시-스타일 지식베이스 설계 (`docs/knowledge/`)

### 3.1 구조

```
docs/knowledge/
├── README.md              ← 운영 규칙 (어떻게 채우고 갱신하나)
├── DIGEST.md              ★ Ragless의 핵심: 현재 상태 한눈에 (항상 최신)
├── glossary.md            ← 도메인 용어 (AiEO, GEO, Y4 회피반응 등)
├── findings/              ← 실험·분석에서 나온 발견 (시간순 누적)
│   ├── F2026-04-23_pilot_variance.md
│   └── ...
├── competitors/           ← 경쟁사 프로필 (한 곳당 한 파일)
│   ├── easyk.md
│   ├── drk.md
│   ├── listerine.md
│   └── ...
└── methods/               ← 통계/ML 방법 노트 (재사용 가능 템플릿)
    ├── orthogonal_array_L18.md
    ├── logistic_regression_template.md
    └── shap_interpretation.md
```

### 3.2 갱신 의식 (주간)

**매주 금요일 30분**:
1. 그 주 실험·발견을 `findings/`에 한 파일씩
2. 새로 알게 된 경쟁사 정보를 `competitors/`에 추가
3. `DIGEST.md` 갱신 — 새 발견을 한 줄로 요약 + 기존 결론과 모순되면 표시
4. 메모리에 영향 가는 것은 메모리도 함께 갱신

**왜 의식화?**: 글의 핵심 — "복리로 쌓는다"는 매주 작은 누적. 한 번에 다 하려면 안 됨.

### 3.3 GraphRAG-lite: 발견 간 관계 표시

각 `findings/F<date>_<title>.md` 헤더에 frontmatter로 관계를 명시:

```yaml
---
date: 2026-04-23
related_findings: [F2026-04-15_query_design]
contradicts: []
supports: [H3, H5]   # 마스터 §4.4 가설 ID
vertical: medical_device
---
```

이렇게만 해두면 나중에 grep/스크립트로 가설별·버티컬별·관계별 추출 가능. 풀 그래프 DB까지 필요 없음.

---

## 4. 도구 하네스 설계 (배관 공사)

글이 강조한 "지루한 인프라". 이걸 미리 깔아둬야 본실험에서 안 깨진다.

### 4.1 공유 실험 러너 (구조만 명시, 코드는 나중)

`experiments/_runner.py` (가칭) 책임:
- R1~R10 재현성 룰을 코드 레벨에서 강제 (assert)
- 모든 API 호출을 jsonl로 자동 로깅 (모델 버전, 시드, 타임스탬프 포함)
- **응답 캐싱**: `(model, prompt, seed)` 해시 기반. 같은 호출 절대 두 번 안 함 → API 비용 절감 + 재현성
- 파일럿/본실험 모드 스위치
- 실패 재시도 + 부분 결과 저장

**왜 미리 설계?**: 팀원 6명이 각자 다른 방식으로 API 부르면 결과 합칠 때 깨진다.

### 4.2 응답 캐시는 토큰 효율의 1순위

OpenAI/Gemini는 우리가 부른 만큼 돈 받음. **같은 요청 두 번 부르는 게 가장 큰 낭비**.
- 캐시 키: `sha256(model_version + system_prompt + user_prompt + seed)`
- 캐시 위치: `experiments/api_runs/_cache/<hash>.json`
- 본실험은 의도적으로 cold cache로 시작, 분석 단계에선 같은 데이터 여러 번 읽음 → 핫 캐시

### 4.3 settings.json 훅으로 자동 가드 (선택)

CLAUDE.md §4 룰을 사람이 잊을 수 있음. Claude Code 훅으로 자동 차단:
- PreToolUse Edit `data/raw/**`: 수정 차단 (raw 보존 원칙)
- PreToolUse Bash `git push --force`: 차단
- Stop hook: "이번 세션에 새 발견 있었으면 docs/knowledge/findings/에 기록했나?" 알림

`update-config` 스킬로 설정 가능. 우선순위 낮음, 팀원이 충돌 일으키면 그때 추가.

---

## 5. 검색(RAG) 전략: 우리는 Ragless

### 5.1 왜 Ragless인가

| 진영 | 적합 조건 | 우리 매칭? |
|------|----------|----------|
| 개선된 RAG | 코퍼스 크고 자동 처리 필요 | ❌ 코퍼스 작음 (7주, 수십~수백 문서) |
| GraphRAG | 관계 추론이 핵심 | △ 가설 간 관계는 있지만 풀 그래프 과함 |
| Ragless | 수동 유지 가능 + 복리 효과 큰 영역 | ✅ 정확히 우리 |

### 5.2 Ragless 운영

- 모든 발견·분석·결정을 `docs/knowledge/`에 평문 마크다운으로 적층
- Claude는 grep + Read로 직접 접근. 벡터 DB 없음.
- `DIGEST.md` 한 파일이 항상 최신 = "한 권의 책"
- 양이 너무 늘면 그때 해시 인덱스 또는 임베딩 도입 검토 (현재 불필요)

### 5.3 발표 자료/컨설팅 리포트 생성 시 활용

발표 임박했을 때:
1. Claude에게 "`docs/knowledge/DIGEST.md` 읽고 발표 슬라이드 초안"
2. 필요한 발견이 있으면 `findings/` 그 파일만 추가 Read
3. raw 데이터 없이도 일관된 스토리 가능

---

## 6. 워크플로우 네이티브: 우리 환경에서

글이 말한 "AI가 작업 안에 산다". 우리 환경:
- 터미널 = Claude Code (이미 함)
- 코드 에디터 = VSCode 확장 (현재 환경)
- 노트북 = Jupyter (Claude Code Bash로 실행 가능)
- GitHub = `gh` CLI (이미 인증됨)
- 브라우저 = `/browse`, `/gstack` 스킬 (페이지 진단·QA에 활용)

별도 채팅 창으로 가지 말고, 작업하는 곳에서 Claude를 부른다.

---

## 7. 즉시 실행할 것 (이번 주)

우선순위 높은 순서:

1. ✅ **`docs/knowledge/` 스캐폴딩** — 이 PR로 신설 (README, DIGEST 템플릿, glossary 시드)
2. ✅ **`docs/workflows/` 스캐폴딩** — 이 PR로 신설 (README + 1~2개 예시)
3. ✅ **CLAUDE.md §14 추가** — 토큰 효율 & 컨텍스트 자산 운영 규칙
4. ⏳ **`experiments/_runner_spec.md` 작성** — 공유 러너 스펙 (코드는 데이터 수집 단계 직전에)
5. ⏳ **응답 캐시 결정** — 1차 API 콜 직전에 코드 짜기
6. ⏳ **주간 갱신 의식 정착** — 첫 금요일에 시도

---

## 8. 안 할 것 (의도적으로)

토큰 트렌드라고 다 도입할 필요 없음. 우리 규모에 안 맞는 것:
- ❌ 벡터 DB / 임베딩 검색 — 코퍼스 작음, 마크다운 grep으로 충분
- ❌ 풀 GraphRAG — 가설 ID frontmatter로 80% 해결
- ❌ 자동 위키 컴파일러 — 카파시는 1인 + 매일. 우리는 7명 + 주간 의식.
- ❌ 멀티에이전트 자동화 (오케스트레이션 프레임워크) — Claude Code 서브에이전트로 충분
- ❌ MCP 서버 자체 구축 — 기존 MCP(Notion 등) 활용으로 충분

---

## 9. 참고 매핑: 글의 도구 → 우리 환경 등가물

| 글에서 언급 | 우리 환경에서 |
|------------|------------|
| Claude Code (CLI) | Claude Code VSCode 확장 (사용 중) |
| 카파시 위키 | `docs/knowledge/` (마크다운 위키) |
| OpenClaw (메시저 에이전트) | 해당 없음 |
| Hermes 3 (오픈 모델) | 해당 없음 (OpenAI/Gemini/Perplexity API) |
| MCP 통합 | 이미 가능 (Notion, Gmail, Figma 등) |
| 권한 시스템 | Claude Code permission mode |
| 메모리 레이어 | `~/.claude/.../memory/` (운영 중) |
| 응답 캐싱 | 우리가 직접 구현 예정 (`experiments/_cache/`) |

---

## 10. 1줄 결론

**"매주 30분 갱신 의식 + 캐시 친화 문서 + 서브에이전트 위임 + Ragless 지식베이스"**
이 4가지면 7주 후 Wayne 본인이 "이걸 어떻게 안 하고 살았지" 싶을 것.
