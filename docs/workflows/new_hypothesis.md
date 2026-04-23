# Workflow: 새 가설 추가/검정

**목적**: 마스터 §4.4의 H1~H9 외에 새 가설을 추가하거나, 기존 가설을 본실험 데이터로 검정.
**언제 쓰나**: EDA에서 패턴 발견 시 / 발표 직전 보강 분석 / 데이터 본 후 사후 가설(별도 표시).
**예상 시간**: 60~90분 (분석만, 데이터 수집 별도).
**전제조건**:
- 가설 ID (H10, H11... 또는 EXPLORATORY_X)
- 검정에 필요한 데이터 (가상 페이지 결과 또는 크롤링) 준비
- 메커니즘 근거 한 줄 (왜 이 가설이 그럴듯한가)

---

## 단계

### 1. 가설 사전 등록 vs 사후 탐색 구분
- **사전 등록**: 데이터 보기 *전* 추가. `stats/results/preregistered_hypotheses.md`에 추가, ID는 H10+
- **사후 탐색**: 데이터 본 *후* 추가. `stats/results/exploratory_hypotheses.md`에 추가, ID는 EXPLORATORY_*. 발표/리포트에 "사후 탐색" 명시 의무.

⚠️ p-hacking 방지. 둘 섞지 말 것.

### 2. 가설 명세
- 내용 (H10: ...)
- 메커니즘 (왜 그럴 것 같은가, 한 문단)
- 측정 변수 (어느 X, 어느 Y)
- 검정 방법 (카이제곱 / 로지스틱 / t-test / ANOVA)
- 의사결정 기준 (p-value? effect size? 둘 다?)

### 3. 분석 코드
- `stats/scripts/h<NN>_<topic>.py` 신설
- 결과 저장: `stats/results/h<NN>_<topic>.json` (p-value, OR, CI, effect size)
- 시각화: `stats/results/h<NN>_<topic>.png`

### 4. 다중 비교 보정
- H1~H9에 H10 추가하면 보정 baseline 변경됨. Bonferroni / Holm 재계산.
- 결과에 보정 전/후 모두 명시.

### 5. 가설 상태 갱신
- `DIGEST.md` 가설 상태 표에 추가/갱신 (🟡→🟢/🔴)
- finding 파일 작성: `docs/knowledge/findings/F<date>_h<NN>_<topic>.md`
  - frontmatter: `supports: [H<NN>]` 또는 `contradicts: [H<NN>]`

### 6. 마스터 문서 갱신 (사전 등록만)
- `docs/PROJECT_MASTER.md` §4.4 가설 표에 행 추가 (PR로)

---

## 호출할 스킬/에이전트

| 단계 | 도구 |
|------|------|
| 1, 2 | 메인 (사람이 결정) |
| 3 | Bash 분석 실행 / Plan agent로 분석 설계 위임 |
| 4 | scipy.stats |
| 5 | Edit |
| 6 | PR 생성 (`/ship`) |

`/codex` — 분석 설계가 통계적으로 타당한지 second opinion.
`/plan-eng-review` — 분석 파이프라인 리뷰.

---

## 검증 체크리스트

- [ ] 사전 등록 / 사후 탐색 명확히 구분
- [ ] 메커니즘 근거 명시 (없으면 fishing)
- [ ] 다중 비교 보정 적용
- [ ] effect size + CI 함께 보고 (p-value 단독 X)
- [ ] 시각화 한글 폰트 정상
- [ ] DIGEST + 마스터 문서(사전 등록만) 갱신
- [ ] finding 파일 frontmatter 채워짐

---

## 산출물

- 분석 코드: `stats/scripts/h<NN>_*.py`
- 결과: `stats/results/h<NN>_*.json` + `.png`
- 발견: `docs/knowledge/findings/F<date>_h<NN>_*.md`

---

## 자주 막히는 곳

- **사후 가설인데 사전인 척 보고**: 절대 금지. 발표에서 들킴.
- **샘플 크기 부족**: 셀당 n<15면 검정력 낮음. 본실험 추가 데이터 필요할 수도.
- **교호작용 검정 시 다중 비교**: 6개 요인 페어 = 15개 교호작용. 모두 보면 무조건 1개는 유의. 사전 등록한 것만 검정.
