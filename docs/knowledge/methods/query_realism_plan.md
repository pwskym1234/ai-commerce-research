# 쿼리 현실성 강화 플랜

> "AI에게 사람들이 실제로 던지는 질문"으로 쿼리셋을 교체.
> 기존 v2.1 (24개)은 우리가 작성 — 어투가 부자연스럽거나 다양성 부족.
> 산공통 본실험(Phase E)과 데마 관측형(Phase B1) 둘 다 사용할 핵심 자산.

## 0. 목표

- 의료기기 24개 + 가글 24개 = **48개 현실 쿼리** 확보
- 각 8유형(BRD/CAT/SYM/CMP/COM/PRC/USE/DEC)에 3개씩
- 3개의 변형 패턴 유지: (1) 존댓말 완성문 (2) 반말 짧은 문장 (3) 구어체 불완전·문제 상황

## 1. 소스 우선순위 (4개)

| # | 소스 | 무엇을 얻나 | 접근 방법 | 예상 수율 |
|---|------|-----------|---------|----------|
| 1 | **네이버 지식iN** | 가장 풍부한 한국 사용자 질문, 의료/건강 카테고리 활성 | 검색 결과 수집 (검색 API의 `kin` 검색 활용 — Wayne 발급한 키 사용) | 카테고리당 200~500 |
| 2 | **쿠팡 / 네이버 스마트스토어 Q&A** | **구매 직전** 실제 질문 | 우리가 이미 크롤한 페이지 HTML 안에 보통 있음 → 재추출 (추가 호출 없음) | 페이지당 5~20 |
| 3 | **네이버 카페 게시글 제목** | 산후/갱년기 맘카페 — 핵심 페르소나 어투 | 카페글 검색 API (Wayne 키 사용) | 키워드당 100+ |
| 4 | **유튜브 댓글** | "써봤는데" 사용 후기 어투 | 수동 (10분 분량 영상 5~10개의 상위 댓글) | 50~100 |

**추천 콤보**: 1(지식iN) + 2(Q&A) 자동 수집 → 합쳐서 ~700 풀 → 거기서 24개씩 선별. 3, 4는 옵션.

## 2. 수집 방법론

### 2.1 네이버 지식iN

- API 엔드포인트: `https://openapi.naver.com/v1/search/kin.json`
- 일일 한도: 25,000 (충분)
- 키워드 (의료기기): 요실금치료기 / 케겔운동기 / 골반저근 운동 / 전립선 운동기 / 산후 회복 / 요실금 증상
- 키워드 (가글): 가글 추천 / 구취 가글 / 잇몸 가글 / 구강청결제 / 입냄새 / 산후 가글
- 검색당 100건 (display=100), 각 키워드 1~5페이지 → 카테고리당 500~2,500개

### 2.2 쿠팡·스마트스토어 Q&A 재추출

- 이미 `data/raw/medical_device/*` 와 `data/raw/gargle/*` 에 47개 페이지 HTML 있음
- BeautifulSoup 으로 `.question`, `.qna`, `text-question` 등 쿠팡 Q&A 섹션 추출
- 페이지당 5~20개 → ~200~500개

### 2.3 네이버 카페

- API: `cafearticle.json`
- 동일 키워드. 제목만 추출 (본문은 노이즈)
- ~100개 키워드당

### 2.4 유튜브 댓글 (옵션, P2)

- 키워드별 영상 5개 × 상위 10개 댓글 = 50~100
- YouTube Data API or 수동

## 3. 필터링 기준 (자동 정제)

```python
def is_realistic_query(text: str) -> bool:
    if len(text) < 8 or len(text) > 100:        # 너무 짧거나 길면 제외
        return False
    if any(spam in text for spam in SPAM_KEYWORDS):  # 광고/스팸
        return False
    if not any(kw in text for kw in DOMAIN_KEYWORDS):  # 도메인 키워드 없으면 제외
        return False
    if text.count('?') > 2:                      # 다중 질문은 제외
        return False
    return True
```

- 도메인 키워드(의료기기): 요실금/케겔/골반/전립선/방광/소변/EMS
- 도메인 키워드(가글): 가글/구취/입냄새/구강/잇몸/구강청결
- 스팸: 무료증정/이벤트/공구/공동구매

## 4. 8유형 매핑 (자동 분류)

각 쿼리를 다음 정규식·키워드 기반 룰로 분류:

```python
def classify_query_type(text: str) -> str:
    if any(b in text for b in OUR_BRANDS):     # 우리 브랜드 단일 지명
        return "BRD"
    if any(c in text for c in COMP_BRANDS) and "말고" in text:
        return "COM"                            # 경쟁사 후 대안
    if any(c in text for c in COMP_BRANDS):
        return "CMP"                            # 비교
    if any(num+"만원" in text or num+"원" in text for num in PRICES):
        return "PRC"
    if any(s in text for s in SYMPTOMS):       # 출산/요실금/구취 등
        return "SYM"
    if any(u in text for u in USE_CASES):      # 산후/갱년기/식후 등
        return "USE"
    if "하나만" in text or "딱 하나" in text or "1개만" in text:
        return "DEC"
    return "CAT"  # 기본
```

각 유형별로 풀에서 무작위 추출 → 가독성 검수 → 24개 선별.

## 5. 표본 선택 — 변형 패턴 유지

기존 v2.1 구조 (3변형 × 8유형 = 24) 유지하되 **각 슬롯을 실제 사용자 질문으로 교체**:

| 슬롯 | 변형 | 원형 (v2.1) | 교체 후보 (실제 발췌) |
|------|------|-----------|--------------------|
| BRD-1 | 존댓말 완성문 | "바디닥터 요실금치료기는 어떤 제품인가요?" | "바디닥터 요실금치료기 사용해보신 분 후기 부탁드립니다" |
| BRD-2 | 반말 짧음 | "바디닥터 써본 사람 있어?" | "바디닥터 써본 사람 솔직 후기 좀" |
| BRD-3 | 구어체 불완전 | "바디닥터 요실금치료기 사려는데 좀 알려줘봐" | "바디닥터 사려고 하는데 어떨까요 출산 6개월 차" |
| ... | ... | ... | ... |

지식iN/카페에서 그대로 가져와도 되고, **약간 다듬어서 PII(개인정보) 제거** 정도만.

## 6. 품질 검증

- 팀원 2명에게 24개 보여주고 각각 0~5점 평가:
  - "AI에게 정말 물어볼만한가" (현실성)
  - "어투가 자연스러운가" (구어체 적합성)
- 평균 < 3.5점 슬롯은 풀에서 다른 후보로 교체
- inter-rater 평균 차이 ≥ 1.5점이면 재검토

## 7. 산출물

- `experiments/prompts/queries.yaml` — 의료기기 24개 (교체)
- `experiments/prompts/queries_gargle.yaml` — 가글 24개 (신규)
- `data/processed/query_pool_raw.jsonl` — 수집 풀 원본 (지식iN/Q&A 등) — 향후 추가 추출 가능
- `docs/knowledge/methods/query_realism_plan.md` — 이 문서

## 실행 단계

1. **(자동)** 지식iN + 쿠팡 Q&A 수집 스크립트 작성·실행 → query_pool_raw.jsonl
2. **(자동)** 필터링 + 8유형 자동 분류 → 8유형별 후보 풀
3. **(반자동)** Wayne 또는 Claude가 각 8유형 × 3변형에 풀에서 1개씩 선별
4. **(수동)** 팀원 2명 품질 검수
5. **(자동)** queries.yaml / queries_gargle.yaml 갱신
6. **(검증)** Phase B1 dry-run으로 새 쿼리로 5 호출 → AI 응답 자연스러운지 눈 검수

총 소요: 자동 30분 + 검수 1시간 = ~1.5시간.
