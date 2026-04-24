# 제품 단위 AI 노출 최적화 회사/스타트업 맵 (2026-04-24 기준)

## 0. 전제

이 문서는 **"제품 단위(SKU/Product-level) AI 노출 최적화"**를 표방하거나, 실제로 그렇게 확장 중인 회사들을 공개 웹 자료 기준으로 최대한 넓게 수집한 결과임.

중요한 한계가 있음.

- 이 시장은 2025~2026년에 급격히 생기고 있는 초기 시장이라 **"전부"를 완전하게 보장할 수는 없음**.
- 많은 회사가 실제로는 **브랜드 단위 AI visibility 모니터링**에 가깝지만, 마케팅 문구에서는 product/shopping/commerce까지 넓게 말함.
- 따라서 이 문서에서는 회사를 아래 4개 층위로 분리했음.
  1. **실질적으로 SKU/Product-first에 가까운 회사**
  2. **리테일/eCommerce 특화이지만 SKU 클로즈드 루프는 약한 회사**
  3. **일반 AEO/GEO/AI visibility 툴이지만 제품 카테고리 적용이 가능한 회사**
  4. **툴이 아니라 서비스/에이전시 위주 플레이어**
- 각 회사별로 **공개 자료 기반 사실**과 **내 추론**을 명확히 분리했음.

---

## 1. 한 줄 결론

이 시장에서 진짜로 **제품 단위 입력→AI 노출 측정→콘텐츠/카탈로그 보정→재배포→성과 측정**의 폐루프(closed loop)를 상대적으로 명확하게 보여주는 회사는 많지 않음.

현재 공개 자료상 상대적으로 강한 축은 아래와 같음.

- **Alhena**: SKU 렌더링/추천/수익 연결까지 가장 명시적임
- **Profound (Shopping / Product Analysis)**: ChatGPT 쇼핑 및 SKU/merchant 레이어 분석이 가장 직접적임
- **Azoma**: 제품 카탈로그를 AI shopping agent가 읽는 방식 자체를 표준화/배포하려는 방향이 강함
- **ReFiBuy**: 상품 데이터 ingest → evaluate → enrich → distribute의 폐루프를 가장 정직하게 설명함
- **Sixthshop**: 개별 product URL을 AI가 어떻게 읽는지 스캔하는 진단형에 가까움

그 외 다수는 **측정/모니터링 툴**이거나, **콘텐츠/스키마 최적화 권고**까지는 하지만 실제로 SKU 레벨 배포 파이프라인까지는 공개적으로 보여주지 않음.

---

## 2. 분류 기준

### A. 진짜 SKU/Product-first로 분류한 기준
아래 중 2개 이상이 공개 자료에서 비교적 명확해야 넣었음.

- 개별 SKU / product / catalog item 단위 추적
- AI shopping / product recommendation / commerce query 명시
- 상품 속성, 가격, 재고, 리뷰, 이미지, schema, feed를 개선 대상으로 명시
- Shopify / PIM / catalog / merchant center / syndication / protocol 배포 연결
- 제품별 visibility와 revenue/checkout/traffic 연결

### B. 부분적으로만 product-level로 분류한 기준
- 리테일 특화 문구는 있으나 실제는 브랜드 visibility 중심
- 제품 카테고리/질문/비교 추적은 가능하지만 SKU 운영 루프가 불명확
- schema/FAQ/콘텐츠 권고 수준이 강함

### C. "최적화" 문구를 볼 때 주의할 점
이 시장에서 "optimize"는 실제로는 아래 세 경우가 섞여 있음.

1. **진짜 변경 실행**: 스키마/카탈로그/콘텐츠를 생성·수정·배포
2. **작업 지시**: 무엇을 고치라고 추천만 함
3. **마케팅 표현**: 측정 대시보드만 있는데 optimize라고 부름

이 문서에서는 이 차이를 계속 지적함.

---

## 3. 시장 지도 요약

## 3.1 가장 주목할 제품 단위 플레이어

| 회사 | 분류 | 공개상 핵심 포지션 | 실제로 보이는 핵심 로직 | 판단 |
|---|---|---|---|---|
| Alhena | SKU/Product-first | Commerce용 AEO/GEO, 어떤 SKU가 AI 쇼핑 답변에 어떻게 등장하는지 추적 | SKU appearance/rendering/competitor/revenue 연결, 외부 소스 추적, 콘텐츠 액션 | 가장 강함 |
| Profound | SKU/Product-first | AI shopping / Product Analysis / Merchant optimization | 쇼핑 모드 유발 쿼리, SKU별 노출·속성·checkout ownership, merchant feed/FAQ/PDP 보정 | 가장 강함 |
| Azoma | SKU/Product-first | Catalog를 AI agent가 이해·추천·구매하게 만드는 layer | catalog audit/enrich/syndicate, ACP/UCP/AMP 계층, AI-ready listings 생성 | 구조적으로 강함 |
| ReFiBuy | SKU/Product-first | ACO(Agentic Commerce Optimization) | Ingest → Evaluate → Enrich → Distribute 폐루프 | 명확함 |
| Sixthshop | Product-page diagnostic | 개별 product URL을 AI가 어떻게 읽는지 점수화 | schema/data trust, intent match, media, eligibility 기반 스코어링 | 진단형 강점 |
| Recomaze | Product-comparison driven | ChatGPT/Perplexity/Gemini에 제품 질의·비교를 던져 모니터링 | 질문 세트 기반 compare, AI-ready titles/Q&A 생성 | 중간 |
| Authoritas (Retail) | Retail AI visibility | 온라인 리테일용 AI visibility | catalog/keyword import, category-feature prompt tracking, mention/citation parsing | 넓지만 실행은 약간 간접적 |
| Ayzeo | Retail AI visibility | product category 모니터링 + schema audit | commercial prompt set, position/competitor/schema audit, GA revenue attribution | 중간 |
| AEO Vision | Product recommendation tracker | AI 제품 추천 추적 | smart prompts, competitor discovery, recommendation/sentiment/review monitoring | 중간 |
| Goodie | Commerce AEO suite | AI shopping 경험에서 제품 추적·최적화 | crawler gaps, action playbook, analytics, attribution, content assist | 방향성은 강하나 공개 로직 세부는 다소 추상적 |

---

## 4. 회사별 상세 정리

## 4.1 Alhena

**분류:** SKU/Product-first

### 공개적으로 어떻게 소개하는가
- 스스로를 **"commerce를 위한 AEO & GEO solution"**로 설명함.
- 공개 자료에서 **"어떤 SKU가 AI shopping answer에 등장하는지, 어떻게 등장하는지, 왜 안 보이는지"**를 추적한다고 말함.
- 단순 mention이 아니라 **rendering**을 구분해서 설명함. 즉, 텍스트에서 한 번 언급되는 것과, 가격/리뷰/이미지/버튼이 붙은 rich commerce card 형태를 다르게 봄.

### 공개 자료에서 추출되는 동작 로직
1. AI shopping / answer surface에서 SKU 단위 노출을 수집함
2. 단순 등장 여부가 아니라 아래를 함께 파싱하는 것으로 보임
   - price
   - ratings
   - reviews
   - image/card rendering
   - positioning / ranking context
3. 경쟁 SKU와 비교함
4. 외부 웹 소스(브랜드 사이트 외부의 후기/기사/리뷰/UGC 등)가 AI 답변에 영향을 주는지 추적함
5. 어떤 콘텐츠/상품정보를 고쳐야 visibility와 revenue가 개선되는지 액션을 제시함
6. 일부 자료에서는 **first-party shopper behavior data**와 연결한다고 설명함

### 내가 보는 실제 구조 추정
Alhena는 단순 AEO 모니터링 툴이 아니라, 아래 3개를 결합하려는 쪽에 가까움.

- **AI shopping SERP/answer parser**
- **catalog/SKU entity mapping layer**
- **revenue attribution layer**

즉, "어떤 프롬프트에서 어떤 SKU가 어떤 형태로 노출되었는가"를 제품 카탈로그와 매핑하고, 이후 onsite behavior 또는 commerce analytics와 연결해 **노출 → 클릭/탐색 → 매출 기여**를 계산하는 구조로 보임.

### 비판적 판단
현재 공개 자료상 **가장 제품 단위에 가까운 회사 중 하나**임.
다만 실제로 얼마나 많은 엔진/쇼핑 인터페이스를 안정적으로 커버하는지, 그리고 revenue attribution이 얼마나 causal한지까지는 외부에서 검증 불가함.

### 참고 자료
- Alhena 홈페이지 / product pages / comparison pages
- 기사/디렉터리 요약 자료 다수 검토

---

## 4.2 Profound

**분류:** SKU/Product-first

### 공개적으로 어떻게 소개하는가
- Shopping Analysis, Product Analysis, Merchant optimization 등으로 설명함.
- **ChatGPT shopping performance**, **AI shopping visibility**, **individual SKUs**, **checkout option ownership** 같은 표현이 직접 등장함.

### 공개 자료에서 추출되는 동작 로직
1. 어떤 프롬프트가 **shopping mode**를 유발하는지 파악함
2. 그 상황에서 어떤 제품이 발견·설명·추천되는지 추적함
3. 제품에 어떤 속성(attribute)이 부여되는지도 본다고 설명함
4. 개별 SKU 기준으로 아래를 추적하는 것으로 보임
   - appearance frequency
   - triggering prompts
   - product attributes assigned by AI
   - merchant/checkout ownership
5. 이후 **merchant layer optimization**을 권함
   - 상품 feed / structured data 정비
   - PDP/FAQ/merchant 정보 개선
   - 경쟁 SKU가 먹는 query 영역 역공략

### 내가 보는 실제 구조 추정
Profound는 현재 공개 자료상 **"브랜드 visibility tool"에서 가장 직접적으로 shopping layer로 확장한 회사**로 보임.
기술적으로는 아래 구조가 유력함.

- prompt library 생성
- shopping-mode detection
- answer card / merchant module parser
- product entity normalization
- merchant ownership mapping
- feed/PDP/schema remediation recommendation

### 비판적 판단
Profound의 강점은 **제품 단위 추적 문구가 매우 선명**하다는 점임.
반면 실제 수정 실행이 자동 배포 수준인지, 아니면 권고 중심인지는 공개 자료만으로는 100% 확정하기 어려움.
하지만 현재 시장에서 **제품 레벨 analytics의 대표격**으로 볼 만함.

### 참고 자료
- Profound 공식 product pages
- Profound 보도자료 / 인터뷰 / 기사

---

## 4.3 Azoma

**분류:** SKU/Product-first

### 공개적으로 어떻게 소개하는가
- GEO + ACO(Agentic Commerce Optimization)를 결합한 플랫폼으로 설명함.
- ChatGPT, Gemini, Perplexity, Amazon Rufus, Walmart Sparky 등을 언급하며 **브랜드/상품이 AI agents에 의해 어떻게 이해되고 추천되는지 관리**한다고 설명함.
- 핵심 메시지는 **"브랜드 카탈로그를 AI가 읽을 수 있는 방식으로 정리하고 배포한다"**는 쪽임.

### 공개 자료에서 추출되는 동작 로직
1. 제품 카탈로그를 읽어 readiness / gaps를 진단함
2. title, attribute, taxonomy, listing content를 enrichment함
3. AI-optimized product listings / FAQs / testimonials / structured comparisons 등을 생성함
4. Shopify / Amazon / Walmart / Salsify 등과 연결해 배포함
5. AI shopping agent가 소비하는 **protocol layer**(ACP/UCP/AMP) 위에서 통제하려는 방향을 제시함
6. 일부 자료에서는 **digital twin**으로 프롬프트/에이전트 상황을 시뮬레이션한다고 설명함

### 내가 보는 실제 구조 추정
Azoma는 일반 visibility SaaS보다는 **"AI commerce middleware"**에 가까움.
핵심은 모니터링이 아니라 **catalog translation layer**임.

가능한 구조는 아래와 같음.

- catalog ingest
- product normalization / enrichment
- protocol-ready export
- commerce-agent channel syndication
- ongoing monitoring

즉, 웹페이지 자체를 고치는 것보다 **"AI가 읽기 좋은 제품 객체를 만들어 여러 AI commerce endpoint로 보낸다"**는 구조가 핵심으로 보임.

### 비판적 판단
방향성은 매우 강함. 특히 앞으로 shopping agent들이 API/protocol 기반으로 상품을 읽기 시작하면 유리함.
다만 지금 시점에서는 **실제 채널 커버리지와 adoption이 얼마나 되는지**가 핵심 불확실성임.

### 참고 자료
- Azoma 홈페이지 / AMP 설명 페이지
- Business Insider 등 기사
- 파트너/도입 사례 자료

---

## 4.4 ReFiBuy

**분류:** SKU/Product-first

### 공개적으로 어떻게 소개하는가
- 스스로를 **ACO(Agentic Commerce Optimization)**라고 부름.
- 가장 특징적인 점은 제품 동작을 **Ingest → Evaluate → Enrich → Distribute**라는 명시적 루프로 설명한다는 점임.

### 공개 자료에서 추출되는 동작 로직
1. **Ingest**
   - SKU-level product data를 다양한 시스템에서 가져옴
2. **Evaluate**
   - schema / crawlability / content gaps / completeness 등을 감시함
   - AI agents가 답변에 쓸 수 있는 상태인지 점검함
3. **Enrich**
   - titles / descriptions / bullets / features를 보강함
   - 속성 누락, 명확성 부족, 비교 정보 부족 등을 보완함
4. **Distribute**
   - 최적화된 데이터를 다시 배포함
   - 폐루프 형태로 재측정함

### 내가 보는 실제 구조 추정
ReFiBuy는 마케팅 문구가 과장되기보다 오히려 **기본 파이프라인을 솔직하게 설명하는 편**임.
핵심은 **PIM/feed optimizer + AI-readiness evaluator** 조합으로 보임.

### 비판적 판단
가장 세련된 인터페이스를 보여주는 회사는 아닐 수 있지만, 공개 자료 기준으로는 오히려 **무엇을 하는지 명확**함.
제품 단위 AI 최적화의 실무 본질에 가장 근접한 구조 중 하나임.

### 참고 자료
- ReFiBuy 공식 product page / launch material

---

## 4.5 Sixthshop

**분류:** Product-page diagnostic

### 공개적으로 어떻게 소개하는가
- 개별 **product URL을 스캔**해서 AI가 그 페이지를 어떻게 읽는지 보여준다고 설명함.
- AI Shopping Visibility 점수를 0~100으로 계산한다고 밝힘.

### 공개 자료에서 추출되는 동작 로직
점수 체계가 비교적 구체적임.

- **Schema & Data Trust**: 35%
- **Content & Intent Match**: 25%
- **Media & Visual Signals**: 20%
- **Commerce & Eligibility**: 20%

즉, 단순 SEO audit가 아니라 AI shopping 맥락에서 product page를 진단함.

### 내가 보는 실제 구조 추정
개별 PDP를 가져와서 아래를 체크하는 진단 엔진으로 보임.

- JSON-LD / schema completeness
- 가격/재고/리뷰/브랜드/속성 등 핵심 commerce fields 존재 여부
- AI가 사용하기 쉬운 텍스트 구조 여부
- 이미지/비주얼 신호 품질
- 구매 가능성/자격 정보(availability, offer, eligibility) 존재 여부

### 비판적 판단
Sixthshop은 **"실행 플랫폼"이라기보다는 진단 스캐너**에 가까움.
하지만 제품 단위 AI 최적화 시장에서 이런 스캐너는 초기 진입점으로 매우 실용적임.
특히 중소 셀러/Shopify 상점에는 이해하기 쉬운 포맷임.

### 참고 자료
- Sixthshop 공식 페이지 / visibility score 설명 페이지

---

## 4.6 Recomaze

**분류:** Product-comparison driven monitoring

### 공개적으로 어떻게 소개하는가
- ChatGPT, Perplexity, Gemini에 고객이 실제로 할 질문을 던져 **제품이 어디서 경쟁사를 이기는지/지는지** 본다고 설명함.
- Shopify app 설명에서는 **AI-ready titles, descriptions, summaries, Q&A** 생성을 언급함.

### 공개 자료에서 추출되는 동작 로직
1. 제품/카테고리/비교 질문 세트를 생성함
2. 여러 AI 엔진에 질의함
3. 내 상품 vs 경쟁사 상품 비교 결과를 파싱함
4. product copy와 Q&A를 생성·개선함
5. 월별 product optimization을 제공한다고 설명함

### 내가 보는 실제 구조 추정
핵심은 **"비교 질문 기반 테스트 벤치"**임.
즉, 구조적으로는 product benchmarking engine + content rewrite tool에 가까움.

### 비판적 판단
실무적으로는 유용할 수 있음. 특히 소비재/브랜드 비교 질문이 많은 카테고리에서.
다만 진짜 SKU 데이터 레이어라기보다 **prompt scenario layer**에서 강함.

### 참고 자료
- Recomaze 공식 홈페이지
- Shopify app listing

---

## 4.7 Authoritas (Retail AI module)

**분류:** Retail AI visibility, partial product-level

### 공개적으로 어떻게 소개하는가
- **온라인 리테일러용 AI optimization tool**이라고 설명함.
- 제품 listings, buying journeys, branded/unbranded retail prompts를 다룬다고 말함.

### 공개 자료에서 추출되는 동작 로직
- product keywords / catalog import
- category / sub-category / feature 단위 프롬프트 추적
- branded vs unbranded buyer journey 구분
- AI answers에서 **mentions / descriptions / recommendations / citations** 파싱
- multilingual / long-tail retail prompt builder 제공

### 내가 보는 실제 구조 추정
Authoritas는 **대규모 retail prompt research + monitoring**에 강한 구조임.
카탈로그를 넣고 해당 제품군을 다양한 상업적 질의 집합으로 분해해 AI 결과를 추적하는 쪽으로 보임.

### 비판적 판단
데이터 수집과 segmentation은 꽤 강해 보이나, 실제 수정/배포 루프는 상대적으로 덜 직접적임.
즉, **"어디가 비는지 보여주는 리테일 분석기"** 성격이 강함.

### 참고 자료
- Authoritas 공식 retail/AI visibility 페이지

---

## 4.8 Ayzeo

**분류:** Retail AI visibility, partial product-level

### 공개적으로 어떻게 소개하는가
- eCommerce 및 product category 모니터링을 직접 언급함.
- 예시 프롬프트가 **"best running shoes under $150"** 같이 명백히 상업적임.

### 공개 자료에서 추출되는 동작 로직
- category/commercial prompt tracking
- appearance / position / competitors 추적
- Product, Review, Offer, AggregateRating, Breadcrumb 등 schema audit
- GA 기반 revenue attribution

### 내가 보는 실제 구조 추정
Ayzeo는 실무적으로는 **category-commerce prompt monitoring + schema QA + analytics attribution** 조합으로 보임.
제품 하나하나보다 **"구매형 질의에서 내 카테고리 포지션"**을 보는 쪽이 강함.

### 비판적 판단
유용하지만, 공개 자료만 보면 순수 SKU platform이라기보다 **eCommerce GEO dashboard**에 가까움.

### 참고 자료
- Ayzeo 공식 pages

---

## 4.9 AEO Vision

**분류:** Product recommendation tracking

### 공개적으로 어떻게 소개하는가
- **"Dominate AI Product Recommendations"**를 전면에 둠.
- product recommendation tracking, competitor product analysis, review sentiment monitoring을 말함.

### 공개 자료에서 추출되는 동작 로직
- smart prompts 자동 생성
- 경쟁 제품 자동 발굴
- recommendation / mention / citation / sentiment 파싱
- review source 및 제품 인식 모니터링

### 내가 보는 실제 구조 추정
제품 추천 맥락에 한정한 **narrow monitoring tool** 성격이 강함.
즉, AI가 어떤 상황에서 어떤 제품을 추천하는지를 추적하고, 그 결과를 바탕으로 copy/reviews/schema 개선 작업을 유도하는 방식으로 보임.

### 비판적 판단
포지셔닝은 선명하지만, 공개 자료상 execution layer 깊이는 제한적임.
그래도 **제품 추천 추적**을 명시적으로 파는 점은 분명함.

### 참고 자료
- AEO Vision 공식 pages

---

## 4.10 Goodie

**분류:** Commerce AEO suite

### 공개적으로 어떻게 소개하는가
- Agentic Commerce Suite를 통해 ChatGPT, Amazon Rufus, Perplexity 등에서 제품을 추적·최적화한다고 설명함.
- crawler gap analysis, analytics, attribution, action playbook, writer 등을 함께 이야기함.

### 공개 자료에서 추출되는 동작 로직
- AI crawler visibility gap 분석
- shopping/commerce surfaces 추적
- prioritized action playbook 생성
- content assist / writer 제공
- analytics / attribution 연동

### 내가 보는 실제 구조 추정
Goodie는 **monitoring + recommended execution + content generation**을 묶은 패키지로 보임.
특정 엔진에서 상품이 안 잡히는 이유를 crawler, content, authority 관점에서 분해하는 구조가 유력함.

### 비판적 판단
방향은 좋지만 공개 자료상 가장 구체적인 제품 데이터 레이어는 보이지 않음.
즉, commerce 중심 AEO이긴 하지만 **정확한 SKU 운영 파이프라인은 다소 추상적**임.

### 참고 자료
- Goodie 공식 site / company descriptions

---

## 5. 리테일/eCommerce에 맞춰져 있지만 SKU 폐루프는 약한 회사들

## 5.1 AthenaHQ

**핵심 포지션**
- eCommerce 산업을 명시적으로 타깃팅함
- Shopify/GA4/GSC와 연결해서 AI search impact를 추적한다고 말함
- ChatGPT Shopping 대응법으로 structured data, crawler access, trusted reviews를 강조함

**추출되는 로직**
- visibility tracking
- content gap/citation gap analysis
- Shopify 등과 연결한 attribution
- CMS publishing loop

**판단**
AthenaHQ는 제품 카테고리에는 적용 가능하나, 공개 자료상 핵심은 여전히 **브랜드/콘텐츠 visibility**임.
다만 eCommerce 실행 환경을 꽤 잘 이해하고 있음.

---

## 5.2 OmniSEO

**핵심 포지션**
- eCommerce/B2B/B2C visibility 측정·개선이라고 설명함
- Perplexity, Google AI Overviews, ChatGPT, Google AI Mode 등 별도 tracker를 운영함
- 일부 2차 자료에서는 Shopify catalog 연결을 언급함

**추출되는 로직**
- prompt tracking
- competitor analysis
- citation/sentiment analysis
- AI bot analytics
- commercial query별 visibility monitoring

**판단**
공식 자료만 보면 **범용 AI visibility platform**에 더 가까움.
다만 상거래 쿼리 추적과 catalog 연결 가능성이 보여서 리테일용으로 쓸 수는 있음.

---

## 5.3 Mirakl

**핵심 포지션**
- 자사 자료에서 product page analysis tool을 제시함
- structured data, pricing visibility, inventory accuracy, reviews/social proof를 AI recommendation의 핵심으로 설명함

**추출되는 로직**
- PDP 분석
- missing attributes / schema gaps 진단
- 재고·가격·리뷰 신뢰도 개선 권고

**판단**
Mirakl은 이 시장의 전용 스타트업이라기보다 **기존 eCommerce 인프라 회사가 AI shopping readiness scanner를 붙인 경우**임.
하지만 상품 단위 AI 최적화 논리 자체는 꽤 정석적임.

---

## 5.4 Salsify

**핵심 포지션**
- AEO for eCommerce를 적극적으로 설명함
- 제품 정보가 불완전·불일치·비구조적이면 AI가 잘못 설명한다고 말함

**추출되는 로직**
- complete product attributes
- naming standardization
- contextual purpose/use-case enrichment
- topic clusters / semantic formatting
- mention/citation tracking

**판단**
Salsify는 원래 PXM/PIM 계열 강자라서, AI 최적화를 **product content governance 문제**로 해석하는 편임.
전용 AEO 스타트업은 아니지만, 실제 실무에서는 오히려 현실적인 축일 수 있음.

---

## 5.5 WordLift

**핵심 포지션**
- structured knowledge graph 기반으로 브랜드/카탈로그를 AI가 읽기 쉽게 만든다고 설명함
- eCommerce catalog/category/product visibility use case를 제시함

**추출되는 로직**
- entity extraction
- knowledge graph 생성
- semantic markup
- navigation/content structure optimization

**판단**
WordLift는 직접적인 shopping visibility tracker라기보다 **semantic infrastructure provider**에 가까움.
제품 단위 AI 최적화의 하부 인프라로 볼 수 있음.

---

## 5.6 Scrunch

**핵심 포지션**
- AXP(Agent Experience Pages)라는 별도 machine-readable page layer를 만든다고 설명함
- content diagnostics에서 entities, claims, pricing, product specs gaps를 찾는다고 말함

**추출되는 로직**
- AI agent가 읽기 쉬운 경량 병렬 페이지 생성
- crawlability / explicit meaning / structured data 개선
- pricing / specs / use case / comparison answers 강화

**판단**
Scrunch의 차별점은 모니터링보다 **AI agent 전용 렌더링 레이어**에 있음.
제품에도 적용 가능하지만, 아직은 범용 브랜드/웹사이트 optimization 성격이 더 강함.

---

## 6. 일반 AI visibility 플랫폼이지만 제품 단위로 확장 가능한 회사들

아래는 엄밀히 말하면 "제품 단위 AI 노출 최적화 회사"라기보다 **브랜드 visibility 플랫폼**임. 다만 제품 카테고리형 질문, 비교형 질문, 가격형 질문 등으로 확장 가능해서 같이 넣음.

### 6.1 Promptwatch
- AI visibility monitoring, visitor analytics, crawler logs, content optimization, technical optimization을 제공함
- 공식 자료 기준 핵심은 브랜드 visibility이나, 제품/카테고리 질의 세트로 운영 가능성이 높음
- 추정 로직: prompt set 관리 + source/citation 분석 + 개선 작업 추천

### 6.2 OtterlyAI
- brand mention / ranking / citation 추적
- AI Prompt Research로 질문 의도와 토픽 패턴을 찾는다고 설명함
- 제품 직접 최적화보다 **어떤 질문 세트를 만들어야 하는가**에 강점이 있음

### 6.3 Peec AI
- AI visibility, source usage, citation coverage 분석
- 어떤 URL/domain이 AI 답변 생성에 **used** 되었는지와 최종 **cited** 되었는지를 나눠봄
- 제품 레벨이라기보다 citation intelligence가 강점

### 6.4 Searchable
- AI visibility를 traffic / leads / revenue와 연결한다고 설명함
- 공식 문구에서 "customers discovering new products and brands through ChatGPT"를 언급함
- 다만 실질 구현은 브랜드/도메인 중심으로 보임

### 6.5 FinSEO
- GEO audit, citability, crawlability, schema, prompt discovery 등을 설명함
- 전형적인 AI visibility stack이며, product-specific 포지셔닝은 약함

### 6.6 Unusual
- "Marketing to AI"라는 메시지로, AI agent가 브랜드를 어떻게 말하는지 교정하는 데 초점이 있음
- 제품 카탈로그 최적화라기보다 **AI narrative control**에 가까움

### 6.7 HubSpot AEO
- visibility score, prompt tracking, citation analysis, recommendations 제공
- product/service relevance filter를 언급하지만, 본질은 범용 브랜드/콘텐츠 visibility 도구임

---

## 7. 서비스/에이전시 플레이어

이들은 소프트웨어 제품이 아니라 **대행·서비스형**이 강함. 그래도 시장 파악을 위해 넣음.

### 7.1 BetterAnswer
- 생성형 AI에서 브랜드 visibility를 높여준다고 홍보함
- 무료 AEO mini audit 등 서비스성 오퍼가 강함
- 로직 추정: prompt testing + source gap 분석 + content/schema 권고

### 7.2 NoGood
- end-to-end AEO services, technical support, on-page recommendations, referral traffic/conversions 증대를 이야기함
- 실행 대행 성격이 강함

### 7.3 AEO Engine
- AI-powered done-for-you AEO system이라 설명함
- tracking, blog generation, internal linking, bulk indexing, off-page seeding까지 폭넓게 말함
- 다만 폭이 너무 넓어서 각 요소의 깊이는 검증 필요

### 7.4 AEO eCommerce Websites
- eCommerce 전용 AEO + PPC 서비스를 제시함
- 제품 단위라기보다 쇼핑몰 전반 최적화 대행에 가까움

### 7.5 Siege Media
- GEO services를 통해 AI 검색에서의 visibility를 높여준다고 설명함
- 전형적인 콘텐츠/PR/authority 기반 서비스형 접근임

---

## 8. 이 회사들이 실제로 만드는 공통 로직

공개 자료를 종합하면, 제품 단위 AI 노출 최적화 회사들이 만드는 핵심 로직은 대부분 아래 8단계 중 일부 조합임.

### 8.1 Prompt universe 생성
- 브랜드명 질의
- 일반 카테고리 질의
- 증상/문제 해결 질의
- 비교 질의
- 가격/예산 질의
- use case / gifting / audience 질의
- 장바구니/구매 의도 질의

즉, "사람이 실제로 묻는 제품 질문 분포"를 만들어야 함.

### 8.2 멀티 엔진 실행
- ChatGPT
- Gemini
- Perplexity
- Google AI Overviews / AI Mode
- Amazon Rufus
- Walmart Sparky
- 기타 shopping agent

여기서 중요한 건 단순 API 호출이 아니라, **실제 사용자 인터페이스에서 shopping card/merchant module/rich result가 어떻게 렌더링되는지**까지 잡아내는 것임.

### 8.3 결과 파싱
파싱 대상은 대체로 아래와 같음.

- mention 여부
- ranking / placement
- citation source
- sentiment / framing
- product attributes assigned by AI
- review / rating / price / availability 노출
- rich card rendering 여부
- merchant ownership / checkout ownership

### 8.4 Catalog/SKU 매핑
파싱한 텍스트/카드를 실제 상품 카탈로그와 맞춰야 함.

- 상품명 변형 처리
- 컬러/용량/옵션 정규화
- parent-child SKU 정리
- 경쟁사 SKU 매칭

이 단계가 없으면 진짜 제품 단위 분석이 안 됨.

### 8.5 원인 분해
노출 저하 원인을 보통 아래 관점에서 찾음.

- schema / structured data 부족
- 상품 속성 누락
- 가격/재고 최신성 부족
- 리뷰/평판 부족
- 이미지/비주얼 신호 약함
- PDP 텍스트가 AI가 이해하기 어렵게 되어 있음
- 외부 웹에서 경쟁사가 더 많이 인용됨
- FAQ / comparison / use-case 설명 부족
- crawlability 문제
- robots / bot access 문제

### 8.6 수정안 생성
수정안은 대체로 아래를 건드림.

- product title / description / bullets
- FAQs
- comparison copy
- category copy
- structured data / JSON-LD
- reviews/reputation capture strategy
- external citation source 확보
- merchant/feed/catalog normalization

### 8.7 배포
실제로 강한 회사는 여기까지 들어감.

- Shopify
- PIM/PXM
- Salsify
- merchant feeds
- Amazon/Walmart listings
- protocol layer(ACP/UCP/AMP 등)

약한 회사는 여기 없이 **"이렇게 고치세요"**까지만 말함.

### 8.8 성과 측정
- AI visibility score
- recommendation rate
- citation share
- competitor win/loss
- traffic
- assisted revenue
- onsite conversion contribution

실제 난도는 여기서 올라감. 왜냐하면 AI 노출과 매출 사이의 인과관계 측정이 어렵기 때문임.

---

## 9. 회사별로 보는 "최적화"의 본질

### 9.1 진짜 execution-heavy 회사
- Alhena
- Azoma
- ReFiBuy
- 일부 Profound product modules

이들은 단순 측정이 아니라 **상품 데이터 구조 자체를 고치는 방향**이 강함.

### 9.2 진단/권고-heavy 회사
- Sixthshop
- Authoritas
- Ayzeo
- AEO Vision
- AthenaHQ
- OmniSEO

이들은 어디가 비는지 잘 보여주지만, 실제 배포/수정 루프는 상대적으로 약하거나 외부 시스템에 의존함.

### 9.3 인프라/레이어 회사
- Salsify
- WordLift
- Scrunch
- Mirakl

이들은 전용 AEO 스타트업이라기보다 **기존 product data / semantic / page infrastructure를 AI에 맞게 재해석**하는 축임.

### 9.4 범용 visibility 회사
- Promptwatch
- OtterlyAI
- Peec AI
- Searchable
- FinSEO
- Unusual
- HubSpot AEO

이들은 제품 단위라기보다 브랜드 단위에서 시작함.
제품 단위 사업을 하려면 이들만으로는 부족할 가능성이 높음.

---

## 10. 내가 보는 시장의 핵심 공백

### 10.1 대부분은 아직 "진짜 제품 운영 툴"이 아님
많은 회사가 product/shopping/commerce를 말하지만, 실제 공개 자료를 보면 상당수는 아래 수준에 머묾.

- 브랜드 mention 추적
- prompt 대시보드
- citation 분석
- 콘텐츠 추천

즉, **SKU catalog system과 결합된 운영 툴**은 아직 드묾.

### 10.2 앞으로 진짜 승부는 "web SEO"보다 "catalog protocol"일 가능성이 큼
지금은 다들 PDP, schema, FAQ를 고침.
그런데 AI shopping agent가 커질수록 핵심은 아래로 이동할 가능성이 큼.

- structured product object
- verified merchant data
- live price / availability
- reviews / trust graph
- direct machine-readable feed
- agent commerce protocol

즉, **웹페이지 최적화 → 상품 객체 최적화**로 무게중심이 이동할 수 있음.

### 10.3 measurement와 execution이 분리되어 있음
많은 툴이 측정은 하는데, 실행은 사람/에이전시/기존 CMS/PIM에 넘김.
이 분리가 크면 고객은 결국 "대시보드는 예쁜데 변화가 안 난다"고 느끼기 쉬움.

### 10.4 제품 단위 사업이라면 결국 external evidence war가 중요함
브랜드 사이트만 고쳐서는 부족함.
AI가 제품을 추천할 때는 아래가 강하게 작용함.

- 리뷰/평판
- 제3자 기사/랭킹/비교글
- Reddit/커뮤니티/UGC
- 유통 채널 데이터
- 일관된 속성 정보

그래서 진짜 강한 플레이어는 결국 **"외부 증거 생태계"**를 같이 관리해야 함.

---

## 11. 너의 관점에서 특히 중요한 시사점

네가 하려는 게 **"제품 단위 AI 노출 최적화"**라면, 이 시장을 볼 때 중요한 질문은 "누가 visibility를 잰다"가 아니라 아래임.

1. **개별 SKU/옵션까지 구분하는가?**
2. **단순 mention이 아니라 shopping rendering을 보나?**
3. **PDP만 보나, 외부 citation/review ecosystem까지 보나?**
4. **수정안을 실제 catalog/feed/schema에 반영할 수 있나?**
5. **성과를 revenue/merchant ownership까지 연결하나?**

이 기준으로 보면, 시장에는 툴이 많아 보여도 실제로 네가 만들려는 문제를 정면으로 푸는 회사는 아직 제한적임.

즉, 아직 자리가 있음.

다만 반대로 말하면, **진짜 어려운 문제를 풀어야 한다는 뜻**이기도 함. 특히 아래 3개가 어렵다.

- SKU entity matching
- shopping UI parsing
- AI visibility ↔ revenue attribution

---

## 12. 우선순위별 경쟁 구도 정리

### Tier 1: 가장 직접적인 경쟁 구도
- Alhena
- Profound
- Azoma
- ReFiBuy

이들은 제품 단위 최적화라는 문제 정의에 가장 가깝게 붙어 있음.

### Tier 2: 실무 대체재 / 부분 경쟁
- Sixthshop
- Authoritas
- Recomaze
- Ayzeo
- AEO Vision
- Goodie

이들은 문제 일부를 잘 해결함. 특히 진단, 비교, 리테일 모니터링, recommendation tracking 쪽.

### Tier 3: 인프라/보완재
- Salsify
- Mirakl
- WordLift
- Scrunch
- AthenaHQ
- OmniSEO

이들은 직접 경쟁자라기보다, 네 제품이 나중에 통합해야 할 파트너/보완재가 될 수도 있음.

### Tier 4: 일반 visibility 툴 / 서비스
- Promptwatch
- OtterlyAI
- Peec AI
- Searchable
- FinSEO
- Unusual
- BetterAnswer
- NoGood
- AEO Engine
- Siege Media

이들은 시장 인식을 넓히는 데는 도움되지만, 제품 단위 execution 측면에선 한계가 큼.

---

## 13. 최종 판단

이 시장은 겉으로 보면 회사가 많지만, 실제로는 세 가지 층으로 갈림.

1. **브랜드 visibility 대시보드 회사**
2. **리테일 특화 모니터링 회사**
3. **상품 객체 자체를 AI commerce용으로 재구성하는 회사**

네가 하려는 것은 1번이 아니라 2번과 3번 사이, 정확히는 **"상품 객체 + 외부 증거 + AI shopping 결과 + revenue"**를 하나의 운영 루프로 묶는 문제임.

공개 자료 기준으로는 **Alhena, Profound, Azoma, ReFiBuy**가 가장 가까운 축이고, 나머지 대부분은 그 주변에서 일부 레이어를 담당하는 상태로 보임.

즉, 이 시장은 이미 시작됐지만 아직 끝나지 않았고, **문제 정의를 더 정확하게 잡는 쪽이 유리한 초기 시장**이라고 보는 것이 맞음.

---

## 14. 참고한 회사/자료 목록

아래는 이번 조사에서 실제로 검토한 주요 공개 자료의 범주임. URL 전체를 일일이 적기보다, 회사별로 어떤 종류의 자료를 봤는지 정리함.

### 공식 홈페이지 / 공식 문서 / 제품 페이지
- Alhena
- Profound
- Azoma
- ReFiBuy
- Sixthshop
- Recomaze
- Authoritas
- Ayzeo
- AEO Vision
- Goodie
- AthenaHQ
- OmniSEO
- Mirakl
- Salsify
- WordLift
- Scrunch
- Promptwatch
- OtterlyAI
- Peec AI
- Searchable
- FinSEO
- Unusual
- HubSpot

### 기사 / 보도자료 / 디렉터리 / 비교글
- Business Insider
- Adweek
- Shopify App Store listings
- Product Hunt / launch materials
- eCommerce/MarTech 업계 비교 페이지
- 각사 블로그 내 comparison / explainer pages

### 주의
비교글과 디렉터리는 편향 가능성이 커서, 최종 판단은 **공식 제품 페이지 문구가 있는 회사를 우선**으로 했음.

---

## 15. 추가로 바로 써먹을 수 있는 압축 버전

### "진짜 제품 단위 AI 최적화"에 가장 가까운 곳
- Alhena
- Profound
- Azoma
- ReFiBuy

### "제품 페이지 진단"에 강한 곳
- Sixthshop
- Mirakl

### "리테일형 visibility/monitoring"에 강한 곳
- Authoritas
- Ayzeo
- AEO Vision
- Goodie

### "인프라/배포 레이어"로 볼 수 있는 곳
- Salsify
- WordLift
- Scrunch

### "범용 AI visibility"에 가까운 곳
- Promptwatch
- OtterlyAI
- Peec AI
- Searchable
- FinSEO
- Unusual
- HubSpot AEO

---

## 16. 내 최종 코멘트

이 시장에서 가장 흔한 착시는 **브랜드 visibility 툴을 제품 단위 최적화 툴로 오인하는 것**임.

제품 단위 사업을 하려면 결국 아래가 필요함.

- 프롬프트별 제품 노출 추적
- SKU normalization
- shopping rendering parser
- schema/feed/catalog enrichment
- 외부 증거 생태계 관리
- revenue attribution

이 중 2~3개만 해도 어렵고, 전부 묶으면 훨씬 더 어려움.
그래서 아직 공개 시장에 플레이어가 많아 보여도, 실제로 깊게 푸는 곳은 제한적임.

