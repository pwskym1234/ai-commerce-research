# Workflow: 파일럿 실험 실행

**목적**: 본실험 전 작은 규모로 LLM 응답 변동성을 측정해서 본실험 반복 횟수를 결정 (R9).
**언제 쓰나**: 본실험 전 무조건. 비용/시간 손해 막는 게이트.
**예상 시간**: 2~3시간 + API 비용 ~$5~20 (조합 수에 따라).
**전제조건**:
- 가상 페이지 일부(20~30개) 또는 크롤링 데이터 일부 존재
- API 키 설정 (.env)
- `experiments/_runner.py` (또는 등가 러너) 사용 가능
- 모델 버전 결정 + .env에 핀

---

## 단계

### 1. 파일럿 설계
- 조합 수: 20~30개 (가상 페이지에서 샘플링)
- 반복 횟수: **5회** (본실험은 15~20회, 파일럿은 변동성만 보면 됨)
- 쿼리: 본실험에 쓸 쿼리셋의 부분집합 3~5개

### 2. 실행 전 게이트 체크
- [ ] R1~R10 (CLAUDE.md §4) 위반 없음
- [ ] `MODEL_VERSION` 명시
- [ ] `temperature` 미설정 (= API 기본) 또는 명시적 0.7
- [ ] 매 반복마다 상품 순서 셔플 코드 확인
- [ ] 결과 jsonl 저장 경로 준비: `experiments/api_runs/<date>_pilot/`

### 3. 실행
- 백그라운드로 (`run_in_background: true`)
- 진행률 모니터: 5분마다 raw jsonl 줄 수 확인
- 비용: 호출 횟수 × 토큰당 단가 추정치를 사전 출력

### 4. 결과 검증
- 모든 jsonl 라인이 `model_version`, `seed`, `timestamp` 필드 보유?
- 응답 파싱 실패율 < 5%?
- 캐시 적중 0% (cold cache 시작 확인)?

### 5. 변동성 분석
- 같은 (조합, 쿼리)에 대해 5회 반복의 Y2 (binary 추천 여부) 분산 측정
- σ_p̂ = √(p̂(1-p̂)/n) — 이항 비율 표준오차
- 결과: "본실험 N회 반복으로 표준오차 < X 달성 가능" 추정

### 6. 본실험 반복 횟수 결정
- σ < 0.1 원하면 n=15~20 OK
- σ < 0.05 원하면 n=50+ 필요 → 비용 재산정
- Wayne과 협의

### 7. 산출물 정리
- `docs/knowledge/findings/F<date>_pilot_variance.md` 작성
  - frontmatter: `phase: pilot`, `supports: [R9]`
  - 본문: 변동성 추정치 + 본실험 반복 횟수 결정
- `DIGEST.md` "다음 액션"에 본실험 일정 추가

---

## 호출할 스킬/에이전트

| 단계 | 도구 |
|------|------|
| 1, 2 | 메인 직접 |
| 3 | Bash run_in_background |
| 4 | Bash + Read 일부 (offset/limit으로 raw 안 넣기) |
| 5 | Python 스크립트 (matplotlib 분포 시각화) |

대용량 jsonl 분석은 `Explore` agent에 위임 — 메인 컨텍스트 보호.

---

## 검증 체크리스트

- [ ] 모든 jsonl 라인 메타데이터 완비 (R3, R5)
- [ ] 캐시 디렉토리 사용됨 (재실행 시 0 호출)
- [ ] σ 추정치 + 본실험 N 권고 명시
- [ ] finding 파일에 frontmatter `supports: [R9]` 표시
- [ ] DIGEST 갱신
- [ ] 비용 실제값 기록 (다음 본실험 예산 산정용)

---

## 산출물

- raw 응답: `experiments/api_runs/<date>_pilot/*.jsonl`
- 요약: `experiments/api_runs/<date>_pilot/SUMMARY.md`
- 발견: `docs/knowledge/findings/F<date>_pilot_variance.md`

---

## 자주 막히는 곳

- **API 레이트 리밋**: OpenAI tier에 따라 다름. 백오프+재시도 러너 필수
- **응답 파싱 실패율 高**: 시스템 프롬프트가 응답 포맷을 강하게 고정 안 함. JSON mode 또는 명시적 스키마
- **캐시 적중률 의도와 다름**: 캐시 키에 모델 버전·시드 포함됐나 확인. 디버깅 시 캐시 끄지 말고 "별도 prefix"로 우회
