# Experiment Runner — 공유 러너 스펙

> 모든 LLM API 실험은 이 러너를 통해야 한다. 6명이 각자 부르면 결과 합칠 때 깨진다.
> 실제 코드는 1차 API 콜 직전(2주차)에 작성. 이 문서는 인터페이스 스펙.

---

## 0. 책임

이 러너 하나가 다음을 *모두* 책임:
1. CLAUDE.md §4의 R1~R10 재현성 룰을 코드 레벨에서 강제
2. 모든 호출을 jsonl로 자동 로깅 (모델 버전·시드·타임스탬프·해시)
3. 응답 캐싱 — 같은 호출 두 번 안 하기
4. 파일럿/본실험 모드 스위치
5. 실패 재시도 + 부분 결과 저장
6. 비용 추정 (사전) + 실제 누적 비용 (사후)

---

## 1. 디렉토리 레이아웃 (예정)

```
experiments/
├── _RUNNER_SPEC.md          ← 이 문서
├── _runner.py               ← 본체 (생성 예정)
├── _cache.py                ← 응답 캐싱 (생성 예정)
├── _models.py               ← LLM 클라이언트 추상화
├── _summary.py              ← run 종료 후 SUMMARY.md 자동 생성
├── prompts/
│   ├── system_medical.j2    ← 의료기기용 시스템 프롬프트 (Jinja2)
│   ├── system_gargle.j2     ← 가글용
│   └── queries.yaml         ← 쿼리셋
├── synthetic_pages/
│   └── F<NN>_<config>.html  ← F1~F6 조합별 가상 페이지
└── api_runs/
    ├── _cache/              ← 응답 캐시 (gitignore)
    │   └── <hash>.json
    └── 2026-04-25_pilot/
        ├── config.yaml      ← 이 run의 설정 스냅샷
        ├── responses.jsonl  ← raw API 응답
        └── SUMMARY.md       ← Claude가 메인 컨텍스트에서 읽을 요약
```

---

## 2. ExperimentConfig (스펙)

```python
@dataclass(frozen=True)
class ExperimentConfig:
    # R3: 모델 버전 핀
    model_version: str
    provider: Literal["openai", "google", "perplexity", "anthropic"]
    
    # R1: 반복 횟수 (파일럿은 5, 본실험은 15~20)
    n_repeat: int = 20
    
    # R2: temperature (None = API 기본값, 보통 0.7)
    temperature: float | None = None
    
    # R5: 시드 베이스 (실제 시드 = base + run_idx)
    seed_base: int = 42
    
    # 쿼리/페이지 셔플 활성화 (R4)
    shuffle_products: bool = True
    
    # 모드
    mode: Literal["pilot", "main"] = "pilot"
    
    # 출력 디렉토리
    out_dir: Path = field(default_factory=lambda: Path("experiments/api_runs"))
    
    # 캐시 사용
    use_cache: bool = True
```

**런타임 assert**:
```python
assert config.model_version, "R3: 모델 버전 명시 필수"
assert config.n_repeat >= 15 or config.mode == "pilot", \
    f"R1: 본실험은 반복 ≥15 필수 (파일럿은 OK), got {config.n_repeat}"
assert config.temperature is None or 0.5 <= config.temperature <= 1.0, \
    "R2: temperature는 None(기본값) 또는 [0.5, 1.0]. 0 고정 금지"
```

---

## 3. 호출 인터페이스 (스펙)

```python
def run_experiment(
    config: ExperimentConfig,
    queries: list[Query],
    products: list[Product],
) -> ExperimentRun:
    """
    각 (query, n_repeat) 마다:
      1. seed = config.seed_base + run_idx 로 RNG 생성
      2. RNG로 products 셔플
      3. (model_version, system_prompt, user_prompt, seed) 해시 → 캐시 확인
      4. 캐시 hit: 저장된 응답 사용 / miss: API 호출 후 캐시 저장
      5. 응답을 jsonl에 한 줄 append (메타데이터 포함)
      6. Y1~Y4 추출
    
    종료 시 SUMMARY.md 자동 생성.
    """
```

---

## 4. jsonl 한 줄 스키마

```json
{
  "run_id": "2026-04-25_pilot",
  "query_id": "Q003",
  "repeat_idx": 7,
  "seed": 49,
  "model_version": "gpt-4o-2024-08-06",
  "provider": "openai",
  "temperature": null,
  "system_prompt_hash": "a1b2c3...",
  "user_prompt_hash": "d4e5f6...",
  "products_order": ["bodydoctor_k", "easyk", "drk"],
  "raw_response": "...",
  "y1_parsing_accuracy": 0.92,
  "y2_selected_brands": ["bodydoctor_k"],
  "y3_evidence_type": "spec_based",
  "y4_safety_avoidance": false,
  "tokens_in": 1234,
  "tokens_out": 567,
  "cost_usd": 0.0042,
  "timestamp": "2026-04-25T14:32:11Z",
  "from_cache": false
}
```

**불변 원칙**: 한 번 jsonl에 쓴 줄은 절대 수정·삭제 X. 재분석은 `_summary.py` 재실행으로.

---

## 5. 캐시 설계

- 키: `sha256(provider + model_version + system_prompt + user_prompt + seed + temperature)`
- 위치: `experiments/api_runs/_cache/<hash>.json`
- 본실험은 의도적 cold (실제 데이터 수집)
- 분석/디버깅은 hot (반복 분석 무료)
- `.gitignore`로 캐시 디렉토리 제외 (대용량)
- 단, 캐시 히트율은 SUMMARY.md에 기록 (재현성 확인용)

---

## 6. SUMMARY.md 자동 생성 (Claude 가독성)

`_summary.py`가 jsonl을 읽어 다음을 생성:

```markdown
# Run Summary: 2026-04-25_pilot

**Mode**: pilot
**Model**: gpt-4o-2024-08-06 (openai)
**Total calls**: 150 (cache hits: 0)
**Cost**: $4.32
**Duration**: 23 min

## Y2 Recommendation Rate by Combination

| query_id | combo | n | Y2 mean | Y2 σ | 95% CI |
|----------|-------|---|---------|------|--------|
| Q001 | F1=TABLE,F2=MD | 5 | 0.80 | 0.18 | [0.40, 0.97] |
| ...

## Variance Estimate
- Mean σ across combinations: 0.14
- Recommendation: n=20 for σ_p̂ < 0.10

## Notable Patterns
- (예: Y4 회피 반응이 F5=none일 때 60% → H6 지지 신호)

## Failures
- 3 calls returned malformed JSON (1.9%)

→ raw: responses.jsonl (15,432 lines)
```

이게 있으면 Claude는 raw jsonl 안 읽어도 됨. 토큰 절약 핵심.

---

## 7. 비용 안전장치

- 실행 전 `--dry-run` 옵션으로 호출 수·예상 비용 출력
- 본실험은 `MAX_COST_USD` 환경변수로 상한 (초과 시 abort + 부분 결과 저장)
- 매 100호출마다 누적 비용 stderr에 출력

---

## 8. 팀원이 지켜야 할 것

- 새 분석을 위해 *추가 API 호출 절대 금지*. 항상 기존 jsonl + 캐시 활용
- 새 데이터 필요하면 *새 run_id*로 별도 실행 (기존 jsonl 오염 방지)
- 캐시 디렉토리는 절대 삭제 금지 (재현성)
- 로컬에서 모델 버전 바꾸지 말 것 — `.env`로 핀

---

## 9. 구현 우선순위 (작성 시점에)

1. `_models.py` — OpenAI 클라이언트 추상화 (Gemini/Perplexity는 P2)
2. `_cache.py` — 단순 파일 기반 키-값 캐시
3. `_runner.py` — 위 인터페이스 구현
4. `_summary.py` — jsonl → markdown
5. 통합 테스트 — 5조합 × 2회 dry run

작성 시 LLM 토큰 절약: 코드는 `general-purpose` 또는 `Plan` agent에 설계 위임 후 메인이 구현. 또는 `claude-api` 스킬로 SDK 패턴 활용.
