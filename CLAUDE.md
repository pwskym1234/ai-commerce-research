# CLAUDE.md — AiEO 프로젝트 작업 가이드

> 이 파일은 Claude(또는 다른 AI 어시스턴트)가 본 레포에서 작업할 때 따라야 할 운영 지침이다.
> 프로젝트 전반의 맥락은 [docs/PROJECT_MASTER.md](docs/PROJECT_MASTER.md)에 있고, **모든 작업 시작 전에 마스터 문서를 먼저 읽어야 한다**.
> 팀원 모두가 공유하는 문서이므로 임의로 원칙을 바꾸지 말 것. 변경이 필요하면 PR로 토론.

---

## 0. 한 줄 요약

상품 페이지의 어떤 요소가 AI 추천에 영향을 주는지 측정하는 연구 프로젝트.
- **산공통(stats/)**: 통제 실험 → 인과 추론 (가상 페이지 + 직교 배열 + 로지스틱 회귀)
- **데마(ml/)**: 실제 크롤링 → 예측 모델링 (XGBoost + SHAP + 버티컬 비교)
- **컨설팅(consulting/)**: 결과를 바디닥터K(GN그룹) 페이지 진단/개선 시뮬레이터로 전환

---

## 1. Claude의 핵심 역할

본 프로젝트에서 Claude가 담당하는 역할 8가지. 각 역할의 산출물은 [팀 검수 → 메인 머지] 워크플로우로 처리한다.

### 1.1 실험 설계 지원 (산공통)
- F1~F6 요인의 **직교 배열(Taguchi L18/L36) 설계** 코드 작성
- F1(HTML 포맷) × F2(JSON-LD) × F3(수치 구체성) × F4~F6(인증/근거) 조합 18~36개 산출
- 각 조합에 대응하는 **가상 상품 페이지 HTML 자동 생성** (TABLE/BULLET/PARAGRAPH 변형, Product/MedicalDevice JSON-LD 변형)
- 쿼리셋(Q1×Q2) 자동 생성

### 1.2 데이터 수집 파이프라인 (데마)
- 크롤러 작성: 바디닥터K(bodydoctor.co.kr), GN코스몰, 네이버 스마트스토어, 쿠팡, 경쟁사
- HTML 파싱 → 피처 추출(HTML 포맷 비율, JSON-LD 필드 수, 인증 정보 위치, 수치 구체성 점수, 텍스트 길이, 이미지 수, 리뷰 수/평점, 가격, 섹션 분리 명확성)
- Reddit/네이버 카페/블로그 서드파티 언급 빈도 수집
- 모든 크롤링 결과는 `data/raw/` 원본 보존, `data/processed/` 정제본 분리

### 1.3 LLM API 실험 실행
- ChatGPT(OpenAI)/Gemini/Perplexity API 호출 코드
- **재현성 룰 강제 적용** (§4 참조): 15~20회 반복, temperature default, 모델 버전 고정, position bias 셔플
- Y1~Y4 자동 측정: 파싱 정확도, 추천 선택률, 근거 수치 기반도, 안전성 회피 반응
- 모든 raw 응답은 `experiments/api_runs/<date>/<run_id>.jsonl`로 저장 (재분석 가능하도록)

### 1.4 통계 분석 (산공통)
- Phase 2: 단변량 검정(카이제곱, Fisher's exact, t-test, Mann-Whitney U)
- Phase 3: 로지스틱 회귀 — p-value, odds ratio, 95% CI, 교호작용항 (특히 F1×F2, F4×F6)
- 이항 비율 신뢰구간(Wilson score) 시각화
- ANOVA(연속형 Y2 사용 시), 다중비교 보정(Bonferroni / Holm)

### 1.5 머신러닝 모델링 (데마)
- Baseline: 로지스틱 회귀
- Main: XGBoost, Random Forest
- 해석: SHAP summary plot, dependence plot, 개별 SKU 워터폴
- Spearman rank correlation: 오픈엔드 vs 클로즈드셋 추천 일치도
- 버티컬별 모델 분리 학습 후 SHAP 기여도 비교

### 1.6 컨설팅 산출물 생성
- 바디닥터K 현재 페이지를 F1~F6 기준으로 진단 → `consulting/diagnosis/bodydoctor_k_<date>.md`
- 경쟁사 동일 기준 비교표
- "Before/After 시뮬레이터": 입력 = 페이지 변경, 출력 = 예상 추천 확률 변화
- "우선순위 액션 리스트": SHAP 음의 기여 순으로 정렬

### 1.7 발표 자료 준비
- 학술적 구조(연구 질문 → 가설 → 실험 설계 → 결과 → 결론) 우선
- 발표 초반 필수 슬라이드: 실제 AI 쇼핑 에이전트 작동 구조 + 실험 프로토콜 요약
- "So What" 슬라이드: 바디닥터K Before/After
- 예상 질문 대비 카드 (마스터 문서 §9.4)

### 1.8 팀 협업 관리
- 팀원 6명(산공통 3 + 데마 3) 작업 분배 시 명확한 인터페이스 정의(파일 경로/스키마)
- PR 리뷰 시 §4 재현성 룰, §5 통계 컨벤션, §6 ML 컨벤션 위반 여부 자동 체크
- 주차별 마일스톤 추적

---

## 2. 디렉토리 구조 컨벤션

```
bodydoctor_project/
├── CLAUDE.md                        ← 이 파일
├── README.md                        ← 팀원 온보딩용
├── docs/
│   ├── PROJECT_MASTER.md            ← 프로젝트 전체 컨텍스트 (필독)
│   ├── AGENTS_AND_SKILLS.md         ← 사용 권장 에이전트/스킬 가이드
│   ├── decisions/                   ← ADR (architectural decision records)
│   └── meeting_notes/
├── data/
│   ├── raw/                         ← 크롤링 원본 (수정 금지)
│   ├── processed/                   ← 피처 추출 후 정제본
│   └── external/                    ← 공개 데이터셋, 참고자료
├── experiments/
│   ├── synthetic_pages/             ← 산공통 가상 페이지 HTML (F1~F6 조합별)
│   ├── prompts/                     ← 쿼리셋, 시스템 프롬프트
│   └── api_runs/<date>/<run_id>/    ← API 호출 raw 결과 (jsonl)
├── crawler/
│   ├── scripts/                     ← 사이트별 크롤러
│   └── output/                      ← 크롤링 임시 출력 (검증 후 data/raw로 이동)
├── stats/                           ← 산공통 영역
│   ├── notebooks/                   ← EDA, 가설검정 ipynb
│   ├── scripts/                     ← 재현 가능한 분석 .py
│   └── results/                     ← 표/그림/p-value/odds ratio 산출물
├── ml/                              ← 데마 영역
│   ├── notebooks/
│   ├── scripts/
│   ├── models/                      ← 학습된 모델 아티팩트 (.pkl, .json)
│   └── results/                     ← SHAP 시각화, 메트릭
├── consulting/
│   ├── diagnosis/                   ← 바디닥터K/경쟁사 페이지 진단 리포트
│   └── reports/                     ← 최종 컨설팅 산출물
└── presentations/                   ← 수업별 발표자료
    ├── stats_*.pdf
    └── ml_*.pdf
```

**규칙**:
- `data/raw/`는 한 번 들어가면 **절대 수정·삭제 금지**. 정제는 항상 `processed/`에.
- `experiments/api_runs/`의 jsonl은 한 번 생성하면 불변. 재분석은 새 디렉토리.
- `notebooks/`는 탐색용, 재현 가능한 결과는 `scripts/`로 추출 후 `results/`에 저장.
- 산공통과 데마는 디렉토리로 완전 분리해서 한쪽 팀이 다른 쪽 코드를 안 봐도 됨.

---

## 3. 기술 스택

### 3.1 권장 스택 (변경 시 ADR 필요)

| 용도 | 도구 | 비고 |
|------|------|------|
| 언어 | Python 3.11+ | 산공통/데마 공통 |
| 패키지 관리 | `uv` 또는 `poetry` | `requirements.txt`도 함께 유지 |
| 통계 | `statsmodels`, `scipy.stats` | 로지스틱 회귀, 가설검정 |
| ML | `scikit-learn`, `xgboost`, `shap` | |
| 데이터 처리 | `pandas`, `polars` | |
| 시각화 | `matplotlib`, `seaborn`, `plotly` | 한글 폰트 설정 필수 |
| 크롤링 | `httpx` + `selectolax`, JS 페이지는 `playwright` | `requests`+`bs4`도 무방 |
| LLM API | `openai`, `google-generativeai`, `anthropic` | 모델 버전은 명시적으로 핀 |
| HTML 생성 | `jinja2` 템플릿 | 가상 페이지 F1~F6 변형 |
| JSON-LD | `pydantic` 모델 → JSON 직렬화 | Schema.org 준수 |
| 노트북 | `jupyterlab` | |
| 환경변수 | `.env` + `python-dotenv` | API 키는 절대 커밋 금지 |

### 3.2 R 사용 여부
산공통에서 R이 익숙한 팀원이 있다면 `stats/scripts/` 안에 `.R` 스크립트 허용. 단, 최종 결과는 동일 데이터에서 Python 결과와 일치 확인.

---

## 4. 실험 재현성 룰 (절대 위반 금지)

이 룰은 2차 발표 피드백을 반영한 것이며, 전체 연구의 신뢰성이 여기에 달려 있다.
PR 리뷰 시 자동 체크리스트로 사용한다.

| # | 룰 | 구현 방법 |
|---|-----|---------|
| R1 | **반복 횟수 15~20회** | API 호출 함수에 `n_repeat` 파라미터 강제, 기본값 20 |
| R2 | **temperature는 API 기본값 (보통 0.7) 유지** | `temperature=None`로 두거나 명시적 0.7. 절대 0 금지 |
| R3 | **모델 버전 고정** | `MODEL_VERSION` 상수로 정의 (예: `"gpt-4o-2024-08-06"`), 결과 jsonl에 함께 저장 |
| R4 | **Position bias 셔플** | 쿼리에 상품 리스트 넣을 때 `random.shuffle(products, seed=run_id)` |
| R5 | **랜덤 시드 기록** | 셔플/샘플링 모든 시드를 jsonl에 기록 |
| R6 | **Y변수 이중 정의** | 같은 데이터로 binary Y와 continuous Y(빈도) 둘 다 산출 |
| R7 | **이항 비율 95% CI** | 모든 비율 추정치는 Wilson score CI 함께 표기 |
| R8 | **Raw 응답 보존** | API 응답 원문 + 메타데이터(모델, 버전, 시드, 타임스탬프) jsonl 저장 |
| R9 | **파일럿 우선** | 본실험 전 20~30개 조합 × 5회 파일럿으로 변동성 측정 후 반복 횟수 결정 |
| R10 | **버티컬 분리 분석** | 의료기기와 가글을 같은 모델/같은 결론으로 묶지 말 것. 버티컬 간 차이 자체가 발견. |

**위반 사례 예방 코드 패턴**:
```python
# experiments/api_runs/_runner.py 예시
@dataclass
class ExperimentConfig:
    model_version: str           # 필수, 빈 문자열 금지
    n_repeat: int = 20           # R1
    temperature: float | None = None  # R2: None이면 API 기본값
    seed_base: int = 42          # R5

def run_query(config: ExperimentConfig, query: str, products: list[Product]) -> dict:
    assert config.model_version, "R3: 모델 버전 명시 필수"
    assert config.n_repeat >= 15, f"R1: 반복 횟수 15회 이상 필수, got {config.n_repeat}"
    # 매 반복마다 상품 순서 셔플 (R4)
    rng = random.Random(config.seed_base + run_idx)
    shuffled = rng.sample(products, k=len(products))
    ...
```

---

## 5. 통계 분석 컨벤션 (산공통)

| 항목 | 규칙 |
|------|------|
| 가설 사전 등록 | 분석 시작 전 `stats/results/preregistered_hypotheses.md`에 H1~H9 명시 (마스터 §4.4 참조) |
| 다중 비교 | Bonferroni 또는 Holm 보정 명시. 보정 전/후 모두 표기 |
| Effect size | p-value만으로 결론 짓지 말 것. odds ratio, Cohen's d, Cramér's V 함께 |
| Sample size | 셀당 최소 n=15 보장 (반복 횟수 룰 R1과 일치) |
| 카테고리 변수 | reference level 명시. 모델 출력에 baseline 표시 |
| 교호작용 | F1×F2, F4×F6 우선 검정. 다른 조합은 설명력 있을 때만 |
| Robustness | binary Y와 continuous Y 두 분석 결과 일치 여부 reporting |
| 시각화 | forest plot(odds ratio + 95% CI), interaction plot 권장 |

**금지 사항**:
- ❌ p-hacking (사후 가설 추가 후 동일 데이터로 검정)
- ❌ "p < 0.05이면 효과 있음" 단정 — effect size와 CI를 함께 해석
- ❌ Phase 2~3에서 실제 데이터(`data/raw/`) 사용 — 가상 데이터(`experiments/`)만

---

## 6. ML 분석 컨벤션 (데마)

| 항목 | 규칙 |
|------|------|
| Train/Val/Test 분리 | 시간 기반 또는 SKU 기반 그룹 분리 (같은 SKU가 train+test에 동시 등장 금지) |
| Baseline 필수 | 로지스틱 회귀 baseline 없이 XGBoost 결과만 보고 금지 |
| 메트릭 | AUC, PR-AUC, Brier score (확률 보정 확인). Accuracy 단독 금지 |
| Feature importance | XGBoost gain만 보지 말고 SHAP global summary와 비교 |
| SHAP | TreeExplainer 사용. dependence plot으로 비선형 확인. 개별 SKU 워터폴 |
| 클래스 불균형 | scale_pos_weight 또는 stratified sampling. SMOTE는 신중하게 |
| 버티컬 비교 | 의료기기/가글 분리 모델 → SHAP 기여도 차이가 핵심 발견 |
| 재현성 | `random_state` 고정, 데이터 버전 + 모델 버전 함께 모델 아티팩트에 저장 |

**금지 사항**:
- ❌ 테스트셋으로 하이퍼파라미터 튜닝
- ❌ "SHAP이 그렇게 말한다"만으로 인과 결론 — SHAP은 모델 설명일 뿐 인과 아님
- ❌ 한 모델로 두 버티컬 동시 학습 (R10 위반)

---

## 7. 코드 컨벤션

- 식별자: 영어, snake_case (Python 표준)
- 주석: 한국어 OK (특히 통계/실험 의도 설명에 권장)
- 타입 힌팅: 새 코드는 type hint 필수
- 함수 길이: 50줄 초과 시 분리 검토
- 매직 넘버: 상수로 추출 (`N_REPEAT_DEFAULT = 20`)
- 한글 폰트: 시각화 시 `plt.rcParams['font.family'] = 'AppleGothic'` (mac) 또는 `'Malgun Gothic'` (win)
- Linter: `ruff check`, formatter: `ruff format`
- Notebook: 커밋 전 `nbstripout`로 출력 제거 (대용량 셀 방지)

---

## 8. 데이터 / 시크릿 관리

| 종류 | 위치 | 커밋? |
|------|------|------|
| API 키 (.env) | 루트 `.env` | ❌ `.gitignore` |
| 크롤링 raw HTML | `data/raw/` | 작은 샘플(<10MB)만, 큰 건 외부 스토리지 |
| 가상 페이지 HTML | `experiments/synthetic_pages/` | ✅ (재현성 위해 필수) |
| API 응답 jsonl | `experiments/api_runs/` | 작은 건 ✅, 큰 건 압축 또는 외부 |
| 학습된 모델 | `ml/models/` | <50MB는 LFS, 큰 건 외부 스토리지 |
| 노트북 출력 | `**/*.ipynb` | ❌ nbstripout |

**API 키 노출 발견 시**: 즉시 키 폐기 → 새 키 발급 → git history 정리(BFG/git-filter-repo) → 팀에 공지.

---

## 9. 작업 시작 전 체크리스트

새 작업을 시작할 때 Claude는 다음을 확인한다:

1. [ ] [docs/PROJECT_MASTER.md](docs/PROJECT_MASTER.md) 읽었는가
2. [ ] 산공통 작업인지 데마 작업인지 명확한가 (`stats/` vs `ml/`)
3. [ ] 마스터 문서 §10 미확정 사항 중 의존하는 항목이 있는가 — 있으면 Wayne에게 확인
4. [ ] 재현성 룰(§4) 위반 가능성이 있는가
5. [ ] 산출물이 수업 발표용인지 컨설팅용인지 — 표현 톤 결정
6. [ ] 변경이 다른 팀원 작업에 영향 주는가 — 그러면 PR 분리

---

## 10. 산출물 검증 기준

| 산출물 종류 | 검증 |
|------------|------|
| 가상 페이지 HTML | F1~F6 의도된 수준이 실제 HTML에 반영됐는지 시각 검수, JSON-LD validator 통과 |
| API 실험 결과 | jsonl에 모델 버전·시드·타임스탬프 포함, 반복 횟수 ≥15 |
| 통계 분석 | preregistered hypotheses에 명시된 검정만, 사후 검정은 별도 표기 |
| ML 모델 | baseline 비교, train/test 누수 없음, SHAP 일관성 |
| 컨설팅 리포트 | 비전문가도 읽을 수 있는가, Before/After 정량 수치 포함 |
| 발표자료 | 1분 내 클로즈드셋 정당화, 예상 질문 대비 |

---

## 11. 팀 협업 규칙

- **언어**: 모든 한국어 산출물(README, 발표자료, 리포트)는 한국어. 코드는 영어 식별자.
- **PR 단위**: 한 PR은 한 가지 일만. 산공통/데마 변경 동시 금지.
- **PR 본문 템플릿**: 무엇을, 왜, 어떻게 검증했는지 + 마스터 문서 어느 섹션에 영향
- **커밋 메시지**: `[stats] H3 교호작용 분석 추가` 같이 영역 prefix
- **이슈 라벨**: `area/stats`, `area/ml`, `area/crawler`, `area/consulting`, `priority/p0~p2`
- **회의록**: `docs/meeting_notes/YYYY-MM-DD.md`
- **의사결정 기록**: 큰 결정(직교배열 선택 등)은 `docs/decisions/NNNN-title.md` ADR로

---

## 12. 자주 묻는 의사결정 가이드

| 상황 | 가이드 |
|------|------|
| 새 가설을 추가하고 싶다 | 데이터 보기 전이면 OK, 본 후라면 별도 탐색 분석으로 표시 |
| temperature를 0으로 하고 싶다 | ❌ 금지 (R2). 정 필요하면 ADR로 정당화 |
| 반복을 5회만 하고 싶다 (비용) | ❌ R1 위반. 파일럿(R9)으로 먼저 변동성 측정 후 협의 |
| 의료기기와 가글을 합쳐서 모델 하나로 | ❌ R10 위반. 분리 모델 후 SHAP 비교가 핵심 |
| 페이지 진단을 바디닥터K만 하고 싶다 | ❌ 경쟁사 동일 기준 비교 필수 (마스터 §7.3) |
| LLM이 한국어/영어 답변 섞여 나옴 | 시스템 프롬프트로 응답 언어 고정. 파싱 규칙도 언어별 |
| 데이터에 이상치 발견 | `data/processed/`에서 처리, raw는 그대로 두고 처리 로직 코드로 명시 |
| 시간 부족해서 컷할 항목 | 컨설팅 산출물 < ML 모델 정확도 < 재현성 룰. 재현성은 절대 컷 금지 |

---

## 13. 변경 이력

CLAUDE.md 변경은 PR로. 큰 변경(원칙 수정)은 ADR 동반.

- 2026-04-23: 초안 작성. 마스터 문서 v1 기반.
