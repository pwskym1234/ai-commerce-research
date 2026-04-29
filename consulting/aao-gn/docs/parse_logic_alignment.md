# GEO 감사 파이프라인 수정 가이드
## 프롬프트 생성 구조와 04_parse_responses.py를 함께 맞추는 기준

이 문서는 현재 사용 중인 **프롬프트 생성 구조(02_generate_prompts.py)** 와 **응답 파서(04_parse_responses.py)** 를 함께 보정하기 위한 실전 가이드임.  
목표는 단순히 코드가 돌아가게 하는 것이 아니라, **프롬프트 설계 의도와 파싱 로직이 서로 같은 정의를 쓰도록 맞추는 것**임.

---

## 1. 핵심 진단

현재 구조는 전반적으로 괜찮지만, 아래 3개 지점에서 프롬프트 생성 의도와 파싱 로직이 서로 충돌할 가능성이 큼.

### 1-1. 추천형 프롬프트를 만들고 있는데 파서는 추천 시그널을 너무 좁게 봄
프롬프트 생성은 최근 버전에서 다음 방향으로 정리되었음.

- 설명형보다 **선택형**
- FAQ형보다 **구매판단형**
- 리뷰진위형보다 **대안탐색형**
- 단순 속성 비교보다 **무엇을 살지 판단하는 질문**

그런데 파서의 `post_validate()`는 추천 시그널을 아래와 같이 매우 좁게 잡고 있음.

- 추천
- 권장
- 고려
- 좋은 선택
- 좋은 옵션
- 베스트
- 1위로

문제는 실제 AI 응답은 명시적 추천이어도 저 단어를 안 쓸 수 있다는 점임.

예:
- “프로폴린스 쪽이 더 무난합니다”
- “이 경우에는 바디닥터K가 더 적합합니다”
- “초보자라면 리스테린보다 프로폴린스가 낫습니다”
- “집에서 쓰기에는 바디닥터K 쪽이 더 편합니다”

즉, **프롬프트는 선택형으로 잘 생성했는데 파서가 그걸 추천으로 못 잡을 수 있음**.

### 1-2. 프롬프트는 경쟁사명을 자연어로 다양하게 만들고 있는데 파서는 문자열 포함 검사에 너무 의존함
현재 H2H / COMP_ONLY 프롬프트는 자연어적으로 잘 만들어지고 있음.  
하지만 파서는 경쟁사 탐지를 사실상 다음 방식으로 처리함.

- `normalize_text(keyword) in normalize_text(response_text)`

이 방식은 아래 문제를 만듦.

- `Easy-K` / `Easy K` / `easy-k`
- `이지케이` / `이지케이 요실금치료기`
- `어썸쿨 프로폴리스 가글 600ml` / `어썸쿨 가글` / `프로폴리스 가글`
- `테라브레스` / `TheraBreath`

즉, **프롬프트 생성에서는 자연스러운 표기 변형을 허용하는데 파서는 그 변형을 안정적으로 못 따라감**.

### 1-3. 프롬프트는 H2H와 COMP_ONLY를 다른 질문 의도로 생성하는데 파서는 둘을 비슷하게 win/loss/draw로 집계함
현재 생성 구조상:

- **H2H**: 직접 비교
- **COMP_ONLY**: 경쟁사 대안 탐색

이 둘은 질문 의도가 다름.

그런데 파서의 `determine_win_loss_draw()`는 둘 다 동일하게 처리함.

- 우리만 추천되면 win
- 타깃 경쟁사만 추천되면 loss
- 둘 다 추천되면 rank 또는 final_recommendation으로 비교

이 방식은 H2H에는 어느 정도 맞지만, COMP_ONLY에는 해석상 애매함.

예를 들어:
- “리스테린 말고 뭐 있어?” → 프로폴린스 추천
- 이 경우는 분명 대안 소환 성공이지만, H2H의 ‘승리’와 같은 의미로 보면 과장임

즉, **프롬프트 생성 구조가 이미 둘을 다르게 만들고 있으므로, 파싱과 집계도 그 차이를 반영해야 함**.

---

## 2. 파싱 로직에서 반드시 손봐야 할 것

### 2-1. 브랜드/경쟁사 문자열 정규화 강화

현재 `normalize_text()`는 공백 축약 정도만 하고 있어 브랜드/경쟁사 탐지용으로는 약함.

현재:
```python
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()
```

권장:
```python
def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[\(\)\[\]\-_/]", "", text)
    text = re.sub(r"\s+", "", text)
    return text
```

이렇게 해야 공백, 괄호, 하이픈 차이로 인한 miss를 줄일 수 있음.

---

### 2-2. `brand_keywords` / `competitor keywords` 자동 파생 강화

현재 파서는 config의 `brand_keywords`와 `competitors[].keywords` 품질에 지나치게 의존함.

최소한 아래 파생을 자동 추가하는 것이 좋음.

- 원본 name
- 괄호 제거 버전
- 괄호 안 영문 버전
- 공백 제거 버전
- 하이픈 제거 버전
- 영문 소문자 버전

예시:
```python
def expand_name_variants(name: str) -> List[str]:
    raw = (name or "").strip()
    if not raw:
        return []

    variants = {raw}

    no_paren = re.sub(r"\s*\([^\)]*\)", "", raw).strip()
    if no_paren:
        variants.add(no_paren)

    paren_parts = re.findall(r"\(([^\)]*)\)", raw)
    for p in paren_parts:
        p = p.strip()
        if p:
            variants.add(p)

    compact = re.sub(r"[\s\-_/]", "", raw)
    if compact:
        variants.add(compact)

    for v in list(variants):
        variants.add(v.lower())

    return sorted(v for v in variants if v)
```

그리고 `competitor_match_keywords()`에서 이 함수를 쓰는 식으로 확장해야 함.

---

### 2-3. 추천 시그널 확장 또는 다운그레이드 조건 완화

현재 `post_validate()`는 추천 시그널이 없으면 recommended를 N으로 강등함.  
이건 선택형 프롬프트 구조와 충돌함.

추천 시그널은 아래처럼 넓히는 것이 좋음.

```python
RECOMMENDATION_SIGNALS = [
    "추천", "권장", "권합니다", "권해", "권유",
    "고려해", "고려하시", "선택하는 것이", "선택하시면",
    "좋은 선택", "좋은 옵션", "추천드립니다", "추천 드립니다",
    "탁월", "최고의 선택", "베스트", "1순위", "1위로",
    "낫", "더 낫", "더 맞", "적합", "무난", "유리", "괜찮",
    "선호", "좋", "권할 만", "잘 맞"
]
```

또는 더 안전하게, 아래 조건을 만족할 때만 recommended를 강등하도록 보수적으로 바꾸는 것이 좋음.

- 추천 시그널 없음
- `final_recommendation` 없음
- `our_brand_rank` 없음
- `our_brand_top1/top3` 없음
- 응답이 비교 설명형 또는 일반 정보형

즉, **LLM 판정을 쉽게 뒤집지 않도록 해야 함**.

---

### 2-4. evasion 판정 완화

현재는 응답 앞 600자에 회피 시그널이 있으면 회피로 판정함.

하지만 실제 응답은 아래처럼 부분 회피 + 실질 추천일 수 있음.

- “브랜드별 임상 근거 비교는 어렵지만, 일반적으로는 바디닥터K가 더 무난합니다.”
- “정확한 성분 비교는 어렵지만 프로폴린스 쪽이 입문용으로는 더 적합합니다.”

따라서 회피는 아래처럼 더 엄격하게 판정하는 것이 좋음.

- 회피 시그널 있음
- 추천 시그널 없음
- `final_recommendation` 비어 있음
- 우리 브랜드/경쟁사 recommended도 없음

즉 **부분 회피와 완전 회피를 구분**해야 함.

---

### 2-5. H2H와 COMP_ONLY 집계 해석 분리

현재 `determine_win_loss_draw()`는 `H2H`, `COMP_ONLY`를 같은 룰로 처리함.

이건 최소한 집계 단계에서 분리해야 함.

권장:
- **H2H**: `win/loss/draw`
- **COMP_ONLY**: `our_brand_mentioned`, `our_brand_recommended`, `target_competitor_recommended`, `co_mentioned`

즉 COMP_ONLY는 “대안 소환 성공 여부” 중심으로 보는 것이 맞음.

최소 수정으로는:
- `determine_win_loss_draw()`는 유지
- 05에서 H2H와 COMP_ONLY를 분리된 섹션으로 보여주기

더 정확하게 하려면:
- H2H만 `win_loss_draw`
- COMP_ONLY는 `surfaced / not_surfaced / co-mentioned` 같은 별도 outcome 추가

---

## 3. 프롬프트 생성 구조(02)도 같이 조정해야 하는 것

### 3-1. config에 브랜드/경쟁사 별칭을 더 풍부하게 넣기

예:
```json
{
  "brand_name": "프로폴린스",
  "brand_name_en": "Propolinse",
  "brand_keywords": ["프로폴린스", "propolinse", "프로 폴린스"],
  "competitors": [
    {
      "name": "리스테린",
      "keywords": ["리스테린", "listerine"]
    },
    {
      "name": "테라브레스",
      "keywords": ["테라브레스", "therabreath", "테라 브레스"]
    }
  ]
}
```

이렇게 해야 생성 프롬프트가 자연어로 흔들려도 파서가 따라갈 수 있음.

---

### 3-2. H2H 생성에서 긴 경쟁사명과 짧은 자연 표기를 섞기

예:
- 어썸쿨 프로폴리스 가글 600ml
- 어썸쿨 프로폴리스 가글
- 어썸쿨 가글

정식명만 고집하면 파싱과 모델 응답 일관성 둘 다 나빠짐.  
질문 생성 단계에서 자연 표기를 섞는 것이 좋음.

---

### 3-3. 후기 진위형 질문 비중 제한

파서는 후기/추천/회피를 동시에 해석해야 하므로, 생성 프롬프트가 너무 후기 진위형으로 치우치면 추천률 파싱이 흔들림.

권장:
- H2H: 후기 진위형 20% 이하
- COMP_ONLY: 후기/리뷰 검증형 20% 이하
- BRAND_ONLY: 후기 진위형 20% 이하

나머지는 구매판단형 / 대안탐색형 / 선택형 중심 유지.

---

### 3-4. NEUTRAL에서 생활 디테일형 질문은 소수만 유지

예:
- 소분하기 편한가
- 보관하기 편한가
- 몇 개입이 좋은가

이런 질문은 브랜드 언급 감사보다 생활 편의 질의에 가까움.  
AI가 브랜드를 추천하기보다 일반 속성 설명으로 빠질 가능성이 높음.

권장:
- NEUTRAL 75개 중 이런 질문은 5개 이하

---

## 4. 실전 수정 우선순위

### 우선순위 1 — 꼭 수정
1. `normalize_text()` 강화
2. 브랜드/경쟁사 alias 자동 확장
3. recommendation signal 확대 또는 recommended 다운그레이드 조건 완화

### 우선순위 2 — 강력 권장
4. evasion 판정 완화
5. H2H / COMP_ONLY 집계 분리

### 우선순위 3 — 구조 정리
6. config에 `brand_keywords`, `competitors[].keywords` 확장
7. 02_generate_prompts.py에서 긴 경쟁사명과 짧은 자연 표기를 섞어 생성

---

## 5. 코드 레벨 최소 수정안

### 5-1. normalize_text 교체
```python
def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[\(\)\[\]\-_/]", "", text)
    text = re.sub(r"\s+", "", text)
    return text
```

### 5-2. 경쟁사 키워드 확장
```python
def expand_name_variants(name: str) -> List[str]:
    raw = (name or "").strip()
    if not raw:
        return []

    variants = {raw}

    no_paren = re.sub(r"\s*\([^\)]*\)", "", raw).strip()
    if no_paren:
        variants.add(no_paren)

    paren_parts = re.findall(r"\(([^\)]*)\)", raw)
    for p in paren_parts:
        p = p.strip()
        if p:
            variants.add(p)

    compact = re.sub(r"[\s\-_/]", "", raw)
    if compact:
        variants.add(compact)

    return sorted(set(v for v in variants if v))
```

```python
def competitor_match_keywords(comp: Dict) -> List[str]:
    name = (comp.get("name") or "").strip()
    extras = [str(k).strip() for k in comp.get("keywords", []) if str(k).strip()]
    all_names = []
    for candidate in [name] + extras:
        all_names.extend(expand_name_variants(candidate))
    return sorted(set(all_names))
```

### 5-3. 추천 시그널 확장
```python
RECOMMENDATION_SIGNALS = [
    "추천", "권장", "권합니다", "권해", "권유",
    "고려해", "고려하시", "선택하는 것이", "선택하시면",
    "좋은 선택", "좋은 옵션", "추천드립니다", "추천 드립니다",
    "탁월", "최고의 선택", "베스트", "1순위", "1위로",
    "낫", "더 낫", "더 맞", "적합", "무난", "유리", "괜찮",
    "선호", "좋", "권할 만", "잘 맞"
]
```

---

## 6. 최종 판단

현재 04_parse_responses.py는 **구조는 괜찮지만, 최근의 프롬프트 생성 구조가 더 자연스럽고 더 선택형으로 바뀐 만큼 파서도 그 정의를 따라가도록 보정이 필요함**.

핵심은 아래 한 문장으로 요약 가능함.

> 프롬프트 생성이 “무엇을 살지 결정하는 질문” 중심으로 바뀌었으면, 파서도 “추천”을 너무 좁게 해석하지 말고, 브랜드/경쟁사 매칭도 자연어 표기 흔들림을 견딜 수 있게 강화해야 함.

즉, 지금 필요한 건 전면 재작성보다:
- **문자열 정규화 강화**
- **키워드 확장**
- **추천/회피 보정 완화**
- **H2H/COMP_ONLY 집계 해석 분리**
이 4가지임.
