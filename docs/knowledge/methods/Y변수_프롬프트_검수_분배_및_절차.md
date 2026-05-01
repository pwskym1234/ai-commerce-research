# Y 변수 프롬프트 디자인 + Claude 일치도 검수 — 7명 분배 + 진행 절차

**작성**: 2026-04-30
**대상**: 산공통 + 데마 팀 모두
**용도**: 본실험 재실행 응답 2,560개의 Y 변수를 *Claude haiku 자동 파싱* + *팀원 무작위 샘플 직접 분류* 비교로 *학술 방어 가능한 일치도(Cohen's κ)* 확보
**관련**: [수동태깅_팀_분배_및_절차.md](수동태깅_팀_분배_및_절차.md) (페이지 X 변수 — 본 문서는 응답 Y 변수, 별도 트랙), [핵심 페르소나](../../consulting/personas/핵심_페르소나.md), [팀 네이밍 규칙](../팀_네이밍_규칙.md)

---

## 0. 작업 한 줄 요약

본실험 재실행 응답 **2,560개**의 Y 변수 7개를 7명이 *각자 1 Y 변수*씩 담당:
1. 본인 Y 변수에 대한 *Claude 파싱 프롬프트* 디자인
2. 무작위 *유의 샘플 ~150개*를 본인이 직접 라벨링
3. Claude 자동 파싱 결과와 *Cohen's κ 일치도* 측정
4. κ < 0.7이면 프롬프트 iterate

산출: 7 Y 변수 × Cohen's κ 일치도 보고 → 학술·발표·논문 방어용. *전수 검수 불필요* (κ 검증으로 자동 파싱 정당화).

---

## 1. 분담 표 — 7명 × 7 Y 변수

| # | 이름 | 담당 Y 변수 | 적용 범위 | 라벨 |
|:-:|---|---|---|---|
| **1** | **이경민** | `mentioned_brands` (NER) | 모든 응답 | 자유 텍스트 (한·영 brand 추출) |
| **2** | **방우식** (Wayne) | `our_mention` (binary) | 모든 응답 | true / false |
| **3** | **이재현** | `our_sentiment` | 우리 brand 언급된 응답 | positive / neutral / negative / not_mentioned |
| **4** | **이소현** | `our_rank` | 우리 brand 언급 + 순위 있는 응답 | 1, 2, 3, ... / null |
| **5** | **박재후** | `comparison_result` | CMP 쿼리만 (4 쿼리 × 80 = 320 응답/vertical) | win / tie / loss / solo / null |
| **6** | **최지혜** | `single_select` | DEC 쿼리만 (4 쿼리 × 80 = 320 응답/vertical) | brand_id / null |
| **7** | **박지윤** | `safety_avoidance` | 의료기기 응답 (1,280) | true / false |

**매핑 결정 근거**: 각자 *수동 페이지 태깅*에서 담당하는 차원 결과 비슷한 Y 변수 매칭 (ex. 페이지 NER을 본 이경민 → 응답 NER, 의료 도메인 specialist 박지윤 → 의료 안전성 회피).

> 도메인 swap 가능 (Wayne 결정 시).

---

## 2. 각 Y 변수 라벨 정의 + 프롬프트 디자인 가이드

본인 Y 변수에 대한 Claude 파싱 프롬프트 작성 시 참조. 라벨 정의는 *변경 금지* (분석 일관성 위함).

### 2.1 `mentioned_brands` (이경민) — NER

**무엇**: 응답에 명시적으로 등장한 모든 brand 명. 한국어/영어/오타·변형 포함, 카테고리(케겔 트레이너)·기능명 제외.

**라벨**: 자유 텍스트 list. brand_id 정규화 (예: "EASY-K" → "easyk", "Body Doctor" → "bodydoctor", "Elvie Trainer" → "elvie")

**프롬프트 핵심 지시**:
- 한국어 + 영어 표기 둘 다 매칭
- 오타·변형 (바디닥터스, BodyDoctor) 동일 brand로 묶기
- 우리 SKU 풀 13개 (의료 9 + 가글 4) 외 brand도 자유 추출 → 풀 외 brand 발굴 가치
- "케겔 트레이너", "구강청결제" 같은 *카테고리·기능명* 제외

**모호 케이스**:
- "프로폴리스 가글" — 프로폴린스인지? *일반어*인지? → 일반어로 처리
- "여성용 케겔 운동기" — 일반어, 무시

### 2.2 `our_mention` (방우식 Wayne) — binary

**무엇**: 우리 brand가 명시적으로 언급되는가? (true/false)

**라벨**: true / false

**프롬프트 핵심**:
- vertical=의료기기 → anchor "바디닥터" / vertical=가글 → anchor "프로폴린스"
- 변형 ("바디닥터스", "Body Doctor") 모두 true
- "바디닥터K" (케겔 힙머신) ≠ "바디닥터" (요실금치료기) — *둘 다 우리 GN 그룹 제품*. 의료기기 vertical에선 요실금치료기만 true. K는 별도 anchor.
- *추천 안 한다*도 우리 brand *언급*되면 true (mention ≠ recommend)

### 2.3 `our_sentiment` (이재현) — 4 라벨

**무엇**: 우리 brand에 대한 응답의 감성

**라벨**:
- `positive`: 추천·긍정적 묘사 ("바디닥터가 효과 좋다")
- `neutral`: 단순 언급, 평가 없음 ("바디닥터, 이지케이, 세라젬이 있다")
- `negative`: 회피·단점 강조·"추천하지 않음"
- `not_mentioned`: 우리 brand 미언급

**프롬프트 핵심**:
- our_mention=false면 자동 not_mentioned
- 추천 *순위 1위* = positive 강함
- 비교에서 *경쟁사가 더 좋다* = negative
- "선택지 중 하나" 단순 나열 = neutral

### 2.4 `our_rank` (이소현)

**무엇**: 응답에서 우리 brand 추천 순위

**라벨**: 1, 2, 3, ... / null (언급 없음 또는 순위 없음)

**프롬프트 핵심**:
- 추천 순위가 명시 ("첫째로 바디닥터…") → 1
- 단순 나열 ("바디닥터, 이지케이, 세라젬") → 1 (첫 등장)
- 우리 brand가 *대안* 또는 *마지막* → 그 순위
- 추천 안 함 또는 미언급 → null

### 2.5 `comparison_result` (박재후) — CMP 쿼리만

**무엇**: CMP 쿼리에서 비교 결과

**라벨** (CMP만, 그 외 null):
- `win`: 우리가 더 우수
- `tie`: 비슷·결정 어려움
- `loss`: 경쟁사가 더 우수
- `solo`: 우리만 언급됨 (비교 의미 없음)

**프롬프트 핵심**:
- query_type ≠ CMP → null 자동
- 단순 "둘 다 좋다" → tie
- "A는 X 강점, B는 Y 강점" 차이 명시 + 우리 우위 → win

### 2.6 `single_select` (최지혜) — DEC 쿼리만

**무엇**: DEC 쿼리에서 *단 하나* 추천한 brand

**라벨** (DEC만, 그 외 null):
- 우리 brand → "bodydoctor" (또는 "propolinse")
- 다른 brand → 그 brand_id
- 결정 안 함 → null

**프롬프트 핵심**:
- query_type ≠ DEC → null 자동
- "하나만 추천한다면 X" → X
- "A 또는 B" 두 개 → null (단일 선택 아님)

### 2.7 `safety_avoidance` (박지윤) — 의료기기만

**무엇**: 의료 회피 발언 — "의사·약사·전문가와 상담"

**라벨** (의료기기만):
- `true`: "의료진 상담 권장", "전문의 진단 필요" 표현 있음
- `false`: 그런 표현 없음

**프롬프트 핵심**:
- vertical=가글 → null 자동
- 단순 *추가 안내*만 (사용법 설명 끝에 "의문 있으면 의사 상담") = true
- 회피 강도 분류는 *별도 차원* (현 파이프라인 단순 binary)

---

## 3. 진행 절차 — 8 단계

### Step 1 — 본인 Y 변수 + 프롬프트 디자인

- [ ] §1 분배표에서 본인 Y 변수 확인
- [ ] §2 본인 Y 라벨 정의 정독
- [ ] [기존 parse_responses_claude.py](../../../ml/scripts/parse_responses_claude.py) 의 PARSE_INSTRUCTION 참고
- [ ] 본인 Y 변수 *전용 프롬프트* 작성 → `ml/scripts/prompts/y_<variable>_prompt.txt`
  - 예: `y_mentioned_brands_prompt.txt`, `y_our_sentiment_prompt.txt`
- [ ] 프롬프트 핵심 요건:
  - 입력: query_text + raw_response + (필요 시 query_type)
  - 출력: JSON `{"value": ..., "confidence": 0~1}`
  - confidence 모호 케이스 표시 (검수 우선순위용)

### Step 2 — 무작위 샘플 추출

- [ ] 본인 Y 변수의 *적용 범위* 확인 (전체 / CMP / DEC / 의료)
- [ ] `ml/scripts/sample_for_y_irr.py --y-var <name> --n 150` 실행 (스크립트는 Wayne 또는 1명이 작성)
- [ ] 출력: `data/processed/y_irr/<your_name>_<y_var>_sample.csv`
  - 컬럼: run_id, query_id, repeat_idx, query_text, raw_response, your_label (빈), claude_label (자동 채움)

### Step 3 — Claude 자동 파싱 (Wayne 1회 실행)

- [ ] Wayne이 7개 프롬프트 모아서 통합 실행:
  ```bash
  python3 ml/scripts/y_irr_claude_parse.py --runs ml/data/b1_runs/b1_*_20260501_094*
  ```
- [ ] 산출: 모든 응답에 대해 7 Y 변수 자동 파싱 결과 (~$3 / 5분)
- [ ] 각 팀원 sample.csv의 `claude_label` 자동 채움

### Step 4 — 본인 직접 라벨링

- [ ] sample.csv 열기 (Excel / Google Sheets)
- [ ] 각 행의 `query_text` + `raw_response` 읽고 본인 *직접* 라벨 입력 (`your_label` 컬럼)
- [ ] **주의**: `claude_label` 보지 말고 *blind* 라벨링 (편향 회피)
- [ ] 모호 케이스 → 노란색 + 코멘트

### Step 5 — Cohen's κ 일치도 측정

- [ ] sample.csv 채워서 카톡 단톡방 공유
- [ ] Wayne 또는 데마 팀이 κ 계산:
  ```bash
  python3 ml/scripts/y_irr_kappa.py --csv data/processed/y_irr/<your_name>_<y_var>_sample.csv
  ```
- [ ] 결과: 본인 vs Claude 일치도 + 불일치 cell 분석

### Step 6 — 프롬프트 iterate (κ < 0.7 시)

- [ ] 불일치 cell 검토 → 본인 프롬프트의 *모호한 부분* 식별
- [ ] 라벨 정의 명확화 또는 예시 추가
- [ ] 프롬프트 v2 → Claude 재실행 → κ 재측정
- [ ] κ ≥ 0.7 도달까지 iterate (최대 2~3회)

### Step 7 — 통합 보고 (Wayne)

- [ ] 7 Y 변수 × κ 일치도 표 작성
- [ ] κ ≥ 0.8 변수 → "강한 일치, 자동 파싱 신뢰 OK"
- [ ] κ ≥ 0.7 변수 → "수용 가능"
- [ ] κ < 0.7 변수 → 프롬프트 추가 iterate or 사람 검수 비율 늘림

### Step 8 — 최종 결과 적층

- [ ] `ml/results/y_irr_summary.md` 작성
- [ ] 7 Y 변수 × κ + 모호 케이스 통계
- [ ] 학술·발표·컨설팅 자료에 *"자동 파싱 일치도 κ ≥ X로 검증"* 메시지

---

## 4. 통계 검정 — Cohen's κ 해석

| κ 값 | 일치도 | 권장 액션 |
|:-:|---|---|
| ≥ 0.8 | 강한 일치 | 자동 파싱 신뢰 OK, 보고서에 명시 |
| 0.6 ≤ κ < 0.8 | 적절한 일치 | 수용 가능, 모호 cell만 사람 검수 보강 |
| 0.4 ≤ κ < 0.6 | 약한 일치 | 프롬프트 iterate 또는 라벨 정의 재검토 |
| < 0.4 | 일치 부족 | 라벨 자체 재정의 또는 사람 분류 비율 ↑ |

**N=150 샘플 기준 κ 추정 95% CI 폭 ~±0.08** — 점 추정이 0.7이면 95% CI [0.62, 0.78]. 충분히 정밀.

---

## 5. 산출물 위치

| 파일 | 위치 | 누가 |
|---|---|---|
| 본 절차 | docs/knowledge/methods/Y변수_프롬프트_검수_분배_및_절차.md | 모두 참조 |
| Y 변수별 프롬프트 | ml/scripts/prompts/y_<variable>_prompt.txt | 각 팀원 작성 |
| 무작위 샘플 + Claude 결과 + 사람 라벨 | data/processed/y_irr/<name>_<y_var>_sample.csv | 각 팀원 |
| Cohen's κ 분석 결과 | ml/results/y_irr_<y_var>.md | Wayne / 데마 팀 |
| 통합 일치도 보고 | ml/results/y_irr_summary.md | Wayne |

---

## 6. 시작 전 체크리스트 — 모든 팀원

- [ ] §1 분담표에서 본인 Y 변수 확인 (이경민/방우식/이재현/이소현/박재후/최지혜/박지윤)
- [ ] §2 본인 Y 변수 라벨 정의 정독
- [ ] 카톡 단톡방에서 작업 안내 받기
- [ ] 본인 Y 변수 프롬프트 디자인 (Step 1)
- [ ] Wayne 통합 Claude 파싱 (Step 3) 완료 후 sample.csv 받기

---

## 7. FAQ

**Q: 다른 팀원의 Y 변수도 일부 라벨링해야 하나?**
A: 본인 Y 변수만. 다른 Y의 일치도는 그 담당자 책임.

**Q: blind 라벨링이 정확히 무슨 의미?**
A: sample.csv 열 때 `claude_label` 컬럼을 *숨기고* 본인 라벨링. 끝나면 비교. Claude 답을 보고 본인 라벨이 휘둘리면 일치도 측정 무의미.

**Q: 프롬프트 iterate κ 도달 안 하면?**
A: κ 0.6~0.7도 *수용 가능* (모호 라벨 영역). 학술 보고에 "κ X, 모호 cell 비율 Y%로 사람 검수 보강" 명시.

**Q: 본 작업이 수동 페이지 태깅과 어떻게 다른가?**
A: 별개 트랙.
- *수동 페이지 태깅* = 페이지 X 변수 (T·Q·M·G 차원, 13 SKU × 39 차원)
- *Y 변수 검수* = 응답 Y 변수 (mentioned_brands·sentiment 등, 2,560 응답 × 7 Y)
- 두 작업 *병렬 가능*, 다른 매체 (페이지 = 자사몰 직접 / Y 검수 = sample.csv)

**Q: 프롬프트 디자인 가이드 없이 시작 가능?**
A: §2의 라벨 정의 정독 + [기존 parse_responses_claude.py](../../../ml/scripts/parse_responses_claude.py) PARSE_INSTRUCTION 참고하면 충분. 막히면 카톡 질문.

**Q: 사람 라벨링이 너무 많지 않나?**
A: 인당 ~150 cells 무작위 샘플. cell당 30초~1분. 150 × 30초 = 75분 정도. 학술 정당화 + 본인 Y 변수 깊이 학습 양쪽에 가치 큼.

---

## 8. Wayne 다음 액션

- [ ] **본 문서 + §2 라벨 정의** 카톡 단톡방에 공유
- [ ] 7 Y 변수 분담 ↔ 이름 매핑 OK 또는 swap 결정
- [ ] **`ml/scripts/sample_for_y_irr.py` 작성** 또는 Claude에게 의뢰 (~30분)
- [ ] **`ml/scripts/y_irr_claude_parse.py` + `y_irr_kappa.py` 작성** 또는 Claude에게 의뢰
- [ ] 팀원 7명 프롬프트 디자인 시작 OK 발화
- [ ] 통합 Claude 파싱 (Step 3) 실행
- [ ] 통합 일치도 보고 (Step 7) 완성 후 학술·발표 자료에 적용
