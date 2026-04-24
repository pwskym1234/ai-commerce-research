# AI 노출 최적화 (AEO/GEO/AiEO) 회사 전수 리서치

**작성일**: 2026년 4월 24일
**목적**: 제품 단위 AI 노출 최적화를 제공하는 회사/스타트업의 시장 지도 및 구체적 동작 로직 추출

---

## 0. 먼저 읽어야 할 것 — 비판적 요약

이 시장 전체를 봤을 때 가장 냉정한 사실 몇 가지부터 적는다. 이건 Wayne의 AiEO 포지셔닝에 직접 영향을 준다.

1. **52개 이상의 플랫폼이 이미 존재**하고, 누적 펀딩만 $300M+가 투입된 상태. 시장은 "새로 열린 블루오션"이 아니라 "급속히 레드오션화 중인 서프"다. 2024년 하반기 ~ 2026년 1분기 사이 대부분의 주요 플레이어가 시리즈 A/B를 클로징했다.
2. **대부분의 플랫폼은 "모니터링"에 머물러 있다.** Profound, Scrunch, Peec, AthenaHQ 전부 "AI에서 어떻게 보이는지 측정 + 콘텐츠 제안"이 본질이다. 제품 카탈로그 수준에서 실제로 데이터를 구조화해 AI 에이전트가 읽게 만드는 회사는 훨씬 적다. 이 지점이 Wayne의 차별화 포인트.
3. **"제품 단위 (SKU-level)" 최적화 전문 회사는 훨씬 적다.** 대다수는 브랜드 단위 가시성 추적. 제품 단위에 집중하는 회사는 전 세계적으로 봐도 **Ecomtent / Azoma (같은 팀), Alhena AI, Recomaze, 일부 Adobe Commerce/Feedonomics** 정도. Profound조차 "Asset Hierarchies"로 제품 단위를 지원한 건 2026년 3월이다.
4. **한국 시장은 비어있다.** 체인시프트(Chainsift)가 유일한 본격 플레이어. 그 외 리드젠랩, 픽셀아트공작소 등은 에이전시 형태. **한국 제품 DB(네이버 쇼핑, 쿠팡 등)에 접근 가능한 AiEO 스타트업은 사실상 없다.**
5. **측정의 신뢰도 문제**가 이 시장 전체의 아킬레스건이다. SparkToro + Carnegie Mellon 연구(2026년 1월)는 "동일 프롬프트 100회 실행 시 동일 브랜드 추천 리스트가 나올 확률이 1% 미만"임을 보여줬다. 대부분의 AI 가시성 점수는 확률 분포에서 뽑은 하나의 샘플에 불과하다.
6. **Query Fanout 추적은 누구도 제대로 못 하고 있다.** 모델이 내부적으로 분해한 sub-query에 브랜드가 나타나는지는 외부 도구로 관찰 불가. 유일하게 "fanout 추적"을 내세우는 곳이 LLMrefs인데, 주장 검증이 안 됐고, Profound의 Query Fanouts 페이지도 여전히 추정치 기반이다. Wayne이 이 지점을 실험적으로 해결할 수 있다면 큰 차별화.

---

## 1. 용어 정리

이 시장에는 비슷한 뜻의 약어가 난무한다. 혼란을 피하기 위해 정리한다.

- **SEO** (Search Engine Optimization): 전통 검색엔진 순위 최적화
- **AEO** (Answer Engine Optimization): AI 답변 엔진이 답변을 생성할 때 인용되도록 하는 최적화. Profound, Scrunch 등이 선호하는 용어.
- **GEO** (Generative Engine Optimization): AEO와 거의 동의어. Evertune, Writesonic 등이 선호. Profound는 명시적으로 "AEO = GEO"라고 정리함 (2025년 6월 블로그).
- **AIO** (AI Overview Optimization): Google AI Overview 전용 좁은 범주.
- **LLMO / LLMEO** (LLM Engine Optimization): LLM별 최적화. 리드젠랩 등 한국 일부에서 사용.
- **AiEO** (AI Engine Optimization): Wayne의 용어. 일부 한국 책에서 "AI Information Engine Optimization"으로도 사용됨(방현수, 『된다! AI 상위 노출』, 2026).
- **ACO** (Agentic Commerce Optimization): Azoma가 내세우는 최신 개념. AI 에이전트가 직접 구매까지 하는 흐름에서의 최적화.
- **AMP** (Agentic Merchandising Protocol): Azoma가 2026년 3월 발표한 프로토콜. ACP(Agentic Commerce Protocol, OpenAI가 Stripe와 함께 만든 것)와 구분됨.

Wayne이 주목할 포인트: **시장은 용어 전쟁 중이다.** 용어 선점 자체가 마케팅 자산이 되는 국면. "AiEO"라는 용어를 한국에서 표준화하려면 2026년 상반기가 마지막 기회에 가깝다.

---

## 2. 시장 지도 — 티어별 정리

펀딩/가격/코멘트는 각 회사 공식 자료 및 Plate Lunch Collective의 2026년 4월 52개 플랫폼 비교 리서치 기준.

### 2.1 엔터프라이즈 티어 ($500+/월, 대개 Contact Sales)

| 회사 | 국가 | 누적 펀딩 | 연간 발행 프롬프트 규모 | 제품 단위 지원 | 주 타겟 |
|---|---|---|---|---|---|
| **Profound** | 미국(NYC) | $154.5M (Series C, $1B 밸류에이션, 2026.2) | 수백만 프롬프트/월 | O (Asset Hierarchies, 2026.3) | Fortune 500 전반 |
| **Scrunch AI** | 미국 | $19M (Series A, 2025) | BYO 프롬프트 중심 | △ (AXP Agent Experience Platform) | 엔터프라이즈 마케팅 |
| **Evertune** | 미국 | 미공개 (창업자 이력 강함) | 1M+ 프롬프트/브랜드/월 | X (브랜드 중심) | Fortune 500, PR/브랜드 팀 |
| **Goodie AI** | 미국 | 미공개 | 100~500 프롬프트 | △ | 중견~엔터 |
| **BrandLight** | 미국 | $30M (Series A, Cardumen Capital) | 미공개 | X | Fortune 500 |
| **Bluefish AI** | 미국 | 미공개 | 미공개 | X (브랜드 평판 중심) | 엔터 커뮤니케이션 |
| **Adobe LLM Optimizer** | 미국 | Adobe 본체 | 미공개 | O (Adobe Commerce 연동) | Adobe 기존 고객 |
| **Azoma** | 영국/미국 | $4M Pre-Series A (eBay Ventures, 2025.12) | 수백만 프롬프트 | **O (이커머스 SKU 전문)** | CPG/FMCG 대형 브랜드 (L'Oréal, Unilever, Mars) |

### 2.2 미드마켓 티어 ($100~500/월)

| 회사 | 국가 | 가격 | 특징 |
|---|---|---|---|
| **AthenaHQ** | 미국 | $295/월 | Ex-Google Search PM 창업, Shopify 연동, G2 4.9 |
| **Peec AI** | 독일(베를린) | $95/월~ | $29M 누적, Mixpanel 같은 UI, 저예산 유럽 대표 |
| **Gauge** | 미국 | $99/월 | Y Combinator, Actions Center 차별점 |
| **Relixir** | 미국 | Contact | Y Combinator X25, "자율 GEO 직원 Rex" |
| **Writesonic GEO** | 인도 | $79/월 | 기존 콘텐츠 SaaS 확장형 |
| **AirOps** | 미국 | Free tier 있음 | $55.5M 누적, "insights-to-action" 콘텐츠 생산 자동화 |
| **Otterly.AI** | 오스트리아 | $29/월~ | Gartner Cool Vendor 2025 |
| **Ahrefs Brand Radar** | 싱가포르 | $129/월 | 기존 SEO 도구의 AEO 확장 |
| **Semrush AI Toolkit** | 미국 | $117/월 | Adobe 인수($1.9B, 2025.11) |

### 2.3 예산 티어 (<$100/월)

| 회사 | 가격 | 비고 |
|---|---|---|
| **ProductRank.ai** (by Gauge) | 무료 | 카테고리 기반 랭킹 무료 조회 |
| **Siteline** (구 GPTrends) | $0~ | Agent analytics 기반 |
| **Hall** | $0~ | Blackbird Ventures 투자 |
| **Passionfruit Labs** | $19/월 | 최저가 다중 모델 |
| **Rankscale AI** | $20/월 | 17개 엔진 커버 |
| **LLMrefs** | $79/월 | "Fan-out tracking" 주장 (검증 미진행) |
| **AI SEO Tracker** | 무료 | 감사 툴 |

### 2.4 제품/이커머스 특화 (Wayne과 가장 가까운 경쟁군)

| 회사 | 차별점 | 타겟 시장 |
|---|---|---|
| **Ecomtent** | Amazon Rufus/COSMO, Walmart, eBay 제품 리스팅 전용. A+ Content, AI 이미지, 상세설명 자동생성. 2500+ 기업. | Amazon/Walmart 셀러 |
| **Azoma** (Ecomtent 팀의 엔터 라인) | CPG/FMCG 대형 브랜드 대상. Agentic Merchandising Protocol(AMP) 발표. Rufus + Sparky + ChatGPT Shopping 통합. | L'Oréal, Unilever 급 대형 브랜드 |
| **Alhena AI** | SKU-level 추적 + 매출 귀속 분석 | DTC 이커머스 |
| **Recomaze** | 온사이트 AI 에이전트 + Discoverability Audit | 자사몰 운영사 |
| **Feedonomics** (by BigCommerce) | 제품 피드 최적화 | BigCommerce 생태계 |
| **Tadpull** | ChatGPT Instant Checkout 연동 컨설팅 | 중소 DTC |
| **seoClarity ArcAI Shopping** | 엔터 SEO에 AI 쇼핑 레이어 추가 | 기존 seoClarity 고객 |

### 2.5 한국 시장

| 회사 | 형태 | 특징 |
|---|---|---|
| **체인시프트 (Chainsift)** | SaaS + 컨설팅 | Antler Korea 6기, 2025.7 설립 → 4개월 만에 누적매출 3.5억 원, TIPS 선정. 대표 한용희. 아모레퍼시픽, 달바, LG전자, GC녹십자, CJ웰케어, 멀츠(울쎄라), 라운드랩, 로얄캐닌 등 레퍼런스. |
| **리드젠랩 (Lead Gen Lab)** | 에이전시 | "GEO 실험실" 포지션, 콘텐츠/CRO/광고 에이전시 |
| **픽셀아트공작소** | 에이전시 | 아임웹 기반 GEO 홈페이지 제작 |
| **Inblog** | 블로그 SaaS | AEO 친화 블로그 빌더 |

**핵심 관찰**: 한국에서 체인시프트 외에 본격 플랫폼을 내세운 경쟁자가 없다. 그리고 체인시프트조차 **브랜드 단위 추적 + 에이전시형 컨설팅** 모델이다. **제품 단위 최적화를 정면으로 내세우는 한국 플레이어는 아직 없다.** 이게 Wayne의 포지션 공간.

---

## 3. 각 회사별 구체적 동작 로직 분석

아래 섹션에서는 각 회사가 "어떻게 최적화를 한다"고 주장하는지, 그리고 그것이 구체적으로 어떤 로직으로 돌아갈 것인지를 공개 자료 기반으로 정리한다. 공개되지 않은 부분은 합리적 추론임을 명시한다.

---

### 3.1 Profound (미국, 시장 리더)

**공식 주장 (홈페이지/블로그)**:
- "AI가 브랜드를 어떻게 보는지 모니터링 → 인사이트 도출 → Agent가 콘텐츠 생성·발행까지 자동화"
- G2 2026 Winter AEO 카테고리 리더 선정
- SOC 2 Type II, HIPAA 인증

**제품 구조 (2026년 4월 기준)**:
- **Answer Engine Insights**: 브랜드가 ChatGPT/Perplexity/Gemini/Claude/Google AIO/Meta AI/Grok/DeepSeek 등 답변에 얼마나 등장하는지 추적
- **Agent Analytics**: 웹사이트에 AI 크롤러가 얼마나 방문하는지 서버 로그 기반 추적 (Vercel/Cloudflare/Akamai/GCP/WordPress/Shopify(Nostra 파트너십) 연동)
- **Prompt Volumes**: 400M+ 실제 대화 기반 키워드별 프롬프트 빈도 추정 (2025년 9월 글로벌 확장)
- **Query Fanouts**: 답변 엔진이 사용자 프롬프트를 내부적으로 분해하는 sub-query 추정 (2025년 10월 런칭)
- **Asset Hierarchies**: **제품/기능/서브에셋 단위로 가시성 추적** (2026년 3월 런칭) — 이 기능이 Wayne의 직접 경쟁 요소
- **Agents**: 워크플로 자동화 (Slack, WordPress, Webflow, Contentful, Framer, Google Workspace, Semrush 연동)
- **Profound Sheets**: 스프레드시트형 대량 처리 인터페이스 (2026년 3월)

**구체 동작 로직 (추론 포함)**:
1. **데이터 수집**: LLM API 직접 호출 (API-based methodology). 사전 정의된 프롬프트 세트(고객이 직접 정의 + Profound 추천)를 매일 수십~수백 회 각 모델에 반복 실행.
2. **파싱**: 각 응답에서 (a) 브랜드 언급 여부 (b) 위치(rank) (c) 공동 언급된 경쟁사 (d) 인용된 URL을 NER/파싱 파이프라인으로 추출.
3. **통계 집계**: 동일 프롬프트를 반복 실행한 결과를 평균내어 "mention frequency over time"으로 보고. 이것이 확률성 문제를 완화하는 Profound의 핵심 방법론.
4. **Citation 분석**: 답변에 포함된 인용 URL의 도메인을 카테고리화 → 어떤 타입의 사이트(Reddit/Wikipedia/공식 도메인/블로그)가 answer engine별로 선호되는지 분석 (2026년 1월 "Enhanced Citation Categories" 기능).
5. **콘텐츠 실행**: Agent가 Sanity/WordPress/Webflow/Contentful/Framer CMS에 직접 콘텐츠를 생성·발행. 이때 내부적으로 AEO Content Score라는 ML 모델이 "이 콘텐츠가 인용될 확률"을 예측해 방향을 잡음.
6. **ROI 귀속**: Agent Analytics로 AI 크롤러가 특정 URL을 방문한 후 트래픽이 증가하는지 추적 → Partnerize 파트너십으로 실제 매출 귀속까지.

**약점**:
- Starter 플랜이 50 프롬프트/월 제한 → 제품 라인이 많은 브랜드는 엔터 플랜 강제. 실질적으로 제품 단위 추적을 하려면 비용이 폭증.
- API-only 방식이라 ChatGPT UI에서만 나타나는 Shopping 카드, 테이블 포맷 등은 놓칠 수 있음.
- 확률성 문제는 근본적으로 해결 안 됨.

---

### 3.2 Scrunch AI (미국)

**공식 주장**:
- "AI 검색 가시성 감사 + AI 크롤러 행동 가시화 + AXP(Agent Experience Platform)로 AI 전용 콘텐츠 전달 레이어 제공"
- 500+ 브랜드, Series A $15M (Decibel, Mayfield, 2025.9)
- 레퍼런스: Lenovo, Crunchbase, Penn State, Skims, Clerk(9x sign-ups from AI search)

**제품 구조**:
- **Scrunch Platform**: 브랜드 가시성 추적 (ChatGPT, Claude, Perplexity, Gemini 커버, AI Mode/Copilot 미커버)
- **AXP (Agent Experience Platform)**: 가장 차별화된 주장. "AI 에이전트를 위한 Shadow Site" — 사람 대상 웹사이트는 그대로 두고, LLM/크롤러가 읽기 좋은 구조화된 버전을 병렬로 제공. *여전히 대기자 명단(2026.3 기준)*
- **Information Gap Analysis**: 출처가 오래되었거나 틀린 정보가 AI 답변을 오염시키는지 탐지

**구체 동작 로직**:
1. **Keyword → Prompt 변환**: 이것이 Scrunch의 **약점**으로 지적됨. 실제 사용자 프롬프트를 직접 추적하는 게 아니라, SEO 키워드를 LLM에 자연어 프롬프트로 변환한 뒤 실행. 즉 "사람들이 실제로 어떻게 묻는가"가 아니라 "키워드 x를 자연어로 옮기면 이렇게 묻겠지"를 가정.
2. **3일 업데이트 주기**: 배치 업데이트. 실시간 아님.
3. **Shadow Site (AXP)**: 가장 기술적으로 흥미로운 부분. 추정 동작:
   - 고객 도메인에 `/ai` 또는 서브도메인 형태로 병렬 엔드포인트를 호스팅
   - 구조화된 데이터(JSON-LD + Q&A 포맷)로 원본 페이지 내용을 재구성
   - AI 크롤러의 User-Agent를 감지하여 이 버전을 서빙 (일반 사용자에게는 기존 HTML)
   - 이 방식은 Google이 cloaking으로 간주할 위험이 있어 논란. 현재 대기자 명단인 이유 중 하나일 가능성.
4. **Misinformation Detection**: 크롤러가 참조하는 출처 URL을 역추적 → 해당 출처가 공식 정보와 불일치하면 플래그 → 고객에게 "이 아웃데이트된 페이지를 삭제/갱신하라"고 권고.

---

### 3.3 Evertune (미국)

**공식 주장**:
- "통계적 신뢰도 있는 GEO" — 브랜드당 월 1M+ 프롬프트 처리 (2025년 10배 증설)
- Hybrid methodology: API + 소비자 패널(2500만 명)
- 프로프라이어터리 **AI Brand Index** 점수 (빈도/순위/감정 결합)
- Trade Desk, Index Exchange와 연동해 AI 소스에 프로그래매틱 광고 집행 가능

**구체 동작 로직 (추론)**:
1. **Dual-source 데이터**: 
   - (a) LLM API 직접 호출로 답변 수집
   - (b) EverPanel이라는 소비자 패널 — 실제 사람들이 AI 도구를 쓸 때 브라우저 확장/앱으로 응답을 수집 (이게 Profound가 못 가진 차별화 — 실제 유저 컨텍스트에서의 응답을 관찰)
2. **Attribute Mapping**: 브랜드와 "안전", "가격", "품질" 등 속성의 공동출현 빈도 분석 → "LLM이 당신 브랜드를 어떤 속성과 연결 짓는가" 파악
3. **AI 소스 Programmatic 광고**: LLM이 자주 인용하는 미디어 사이트(예: Reddit, Forbes, Tom's Guide 등)에 타겟 광고를 집행 → 이 사이트의 콘텐츠가 LLM 인용될 때 브랜드 언급 유도. 이게 "AI에 간접 학습시키기" 전략의 상업적 구현.

**약점**: 가격 $3,000/월~ 시작. 포춘 500 외에는 접근 불가.

---

### 3.4 AthenaHQ (미국)

**공식 주장**:
- Ex-Google Search / DeepMind 창업. "Insight + Action" 양쪽을 커버한다고 주장.
- Shopify 연동으로 **AI 가시성 → 실제 매출 귀속** 제공.
- 레퍼런스: Gruns (6x SoV in 60d), Popl.co (+38% leads), Lago (1561% ROI)

**구체 동작 로직**:
1. **Citation Engine**: 각 답변에서 인용된 URL들을 수집 → 경쟁사가 인용되지만 자사가 인용되지 않는 "citation gap"을 식별.
2. **Recommendation Engine**: ML 모델이 (a) 콘텐츠 구조 (b) 키워드 밀도 (c) 인용 가능성 (d) 경쟁사 콘텐츠의 패턴을 학습해 on-page/off-page 액션을 생성.
3. **Pitch Workspace**: 에이전시용 기능 — 프로스펙트 도메인을 입력하면 5분 내 AI 검색 성과 리포트 자동 생성. 이걸로 신규 계약 수주. (체인시프트의 "브랜드 진단"과 유사한 접근.)
4. **Query Volume Estimation Model**: 특정 프롬프트가 한 달에 몇 번 실제로 발생하는지 자체 추정 모델 — 이게 정확도는 불투명하지만 "어느 프롬프트에 집중할지"의 우선순위화에 쓰임.

---

### 3.5 Ecomtent (캐나다, Amazon/Walmart 전문)

**이게 Wayne의 가장 직접적인 레퍼런스**다. Ecomtent이 잘하는 것과 못하는 것을 보면 Wayne의 포지셔닝이 명확해진다.

**공식 주장**:
- Amazon RUFUS, COSMO, Walmart Sparky, ChatGPT Search 최적화
- "제품 리스팅 전용 AI 콘텐츠 생성" — 상세설명, A+ Content, 인포그래픽, AI 제품 이미지
- 2500+ 회사 사용

**구체 동작 로직 (Amazon 논문 "A Shopping Agent for Addressing Subjective Product Needs" 기반)**:

Rufus의 작동 원리를 **Amazon 자체 논문**에서 역공학하고, 이에 맞춰 최적화하는 게 Ecomtent의 핵심이다. Rufus는 제품을 이해할 때 5가지 **Subjective Product Needs (SPN)**을 본다:

1. **Subjective Properties**: "sturdy", "colorful", "spacious" 같은 주관적 속성
2. **Event Relevance**: "perfect for Christmas", "ideal for weddings"
3. **Activity Suitability**: "great for gaming", "designed for travel"
4. **Goal/Purpose**: "helps organize office space", "promotes better sleep"
5. **Target Audience**: "for teens", "perfect for new parents"

**Ecomtent 파이프라인 (추론 포함)**:
1. **입력**: 기존 Amazon 리스팅 (ASIN, 제목, bullet points, 설명, 리뷰, 이미지) 크롤링
2. **SPN 추출**: 리뷰 텍스트 → NER/분류기로 위 5가지 facet 언급 추출 (예: 리뷰에서 "gaming에 좋다"가 자주 나오면 Activity Suitability: gaming 태그)
3. **Gap 분석**: 리스팅 본문에는 없지만 리뷰에는 있는 SPN 식별
4. **콘텐츠 생성**: LLM으로 해당 SPN을 포함한 새 bullet points, description, A+ Content 블록 생성
5. **이미지 생성**: "스노보드+해변에서 젊은 남성이 사용하는 장면" 같은 lifestyle 이미지를 AI로 생성하여 리스팅에 추가 (Rufus는 제품 이미지도 읽음)
6. **Infographic**: 제품 치수, 사용법 단계를 인포그래픽으로 자동 생성

**약점**:
- Amazon/Walmart 셀러 중심 → ChatGPT Shopping처럼 마켓플레이스 외부에서 벌어지는 상황은 Azoma 라인으로 분리함
- 작은 사이즈의 셀러가 많아 엔터 영업 역량이 약함

---

### 3.6 Azoma (영국, Ecomtent 팀의 엔터프라이즈 스핀오프)

**이게 Wayne이 가장 주목해야 할 회사**다. Ecomtent 팀이 대기업 CPG 브랜드 수요에 맞춰 엔터 라인을 분리한 것. 창업자 Max Sinclair는 Amazon에서 6년, 싱가포르 런칭과 EU Grocery를 담당.

**공식 주장**:
- **AMP (Agentic Merchandising Protocol)** 발표 (2026.3, 런던) — 가장 공격적인 개념
- "전통 이커머스는 PDP, 광고, 검색결과 같은 유한한 엔드포인트를 최적화해왔다. Agentic 세상에서는 이런 고정된 페이지가 사라진다." — Max Sinclair
- "SEO → ACO (Agentic Commerce Optimization)" 패러다임 전환
- 레퍼런스: L'Oréal, Unilever, Mars, Beiersdorf

**구체 동작 로직**:
1. **통합 모델 커버**: ChatGPT, Gemini, Amazon Rufus, Walmart Sparky, Perplexity — 즉 **마켓플레이스 내/외부 AI 에이전트 모두 커버** (이 조합은 Profound도 못 함)
2. **Product Attribute Gap Filling**: PIM(Product Information Management) 시스템과 API 연동 → LLM이 읽기 좋은 속성 필드를 자동 확장 (예: 셀러가 채우지 않은 "material_composition", "sustainability_certification" 필드를 LLM으로 추론해 채움)
3. **Bulk Listing Optimization**: 수백만 SKU를 한 번에 최적화할 수 있는 배치 파이프라인
4. **Content Syndication**: 제3자 소스(리뷰 사이트, 인플루언서 블로그)를 AI 에이전트가 자주 인용한다는 관찰에서, 해당 소스에 직접 콘텐츠 배포
5. **Agentic Commerce Protocol 구현**: OpenAI의 ACP에 맞춰 브랜드가 AI 에이전트와 직접 거래할 수 있도록 엔드포인트 세팅 (Stripe 연동 포함)
6. **RegGuard™**: FDA/DSHEA 규제 준수 자동 모니터링 — CPG 브랜드의 리스크 관리

**Wayne에게의 시사점**:
- **마켓플레이스 내부(Rufus/Sparky) + 외부(ChatGPT/Gemini)를 동시에 커버하는 것이 곧 표준이 될 것**. 둘 중 하나만 하면 시장 리더가 못 됨.
- **"제품 속성 채우기 (attribute gap filling)"가 구체적인 엔진 기능이다.** 이건 한국 네이버 쇼핑/쿠팡 카탈로그에도 그대로 적용 가능.

---

### 3.7 Alhena AI (SKU-level 매출 귀속)

**공식 주장**:
- "대부분의 AI 가시성 도구는 브랜드 멘션만 추적한다. Alhena는 SKU 단위로 추적한다."
- Shopify 등 이커머스 플랫폼과 직접 연동해 AI 검색 트래픽 → 실제 매출 전환까지 귀속

**구체 동작 로직 (추론)**:
1. 각 SKU마다 그 제품이 나올 법한 프롬프트 세트를 자동 생성 ("best waterproof hiking boots under $150")
2. 프롬프트 실행 후 제품명/URL 매칭으로 SKU 단위 가시성 점수 계산
3. Shopify 웹훅으로 주문 이벤트를 수신 → UTM/referrer 분석으로 AI 출처 트래픽 식별
4. (AI 가시성 변화) × (매출 변화) 상관분석 리포트 제공

---

### 3.8 Recomaze (온사이트 AI 에이전트)

**공식 주장**:
- 자사몰에 설치하는 온사이트 AI 쇼핑 어시스턴트 + Discoverability Audit
- "외부 가시성 추적은 안 하지만, 당신의 카탈로그 데이터를 AI-friendly하게 만든다"

**동작**: 자사몰 방문자가 AI 챗봇에게 질문 → 그 질문 로그를 분석해 "우리 제품 데이터의 어느 필드가 부족한지" 역산. Azoma가 외부에서 하는 것을 **자사몰 내부 트래픽 기반으로** 한다는 점이 차별점.

---

### 3.9 체인시프트 (Chainsift, 한국)

**공식 주장 (홈페이지 + 다음/매일경제/네이트 기사)**:
- AEO + GEO 앤드투앤드(E2E) 서비스
- Antler Korea 6기, 2025년 7월경 설립 → 4개월 만에 누적매출 3.5억, TIPS 선정
- 레퍼런스: 아모레퍼시픽, 달바, LG전자, GC녹십자, CJ웰케어, 멀츠(울쎄라), 라운드랩, 로얄캐닌, 패스트캠퍼스, 대홍기획, HSAD, 카테노이드, 에잇퍼센트, 위시켓

**공식 주장 — 측정 방법론 (홈페이지 FAQ에서)**:
1. **Fanout 기반 질문 확장 분석**: "AI가 실제 활용하는 질문군을 확장 수집"
2. **플랫폼별 인용 출처 분석**: ChatGPT, Gemini, Perplexity 비교
3. **감정 및 리스크 점수화**: 브랜드 언급 맥락을 정량화
4. **독자 엔진**: "단순 API 호출이 아닌, 실제 사용자가 LLM 챗봇을 사용하는 환경에서 구조적으로 측정"

**핵심 지표**:
- AI 노출 증가 vs 실제 브랜드 검색량 변화
- AI 인용 증가 vs 전환 페이지 유입 증가
- 경쟁사 대비 SOV (Share of Voice) 변화

**구체 동작 로직 (추론)**:
- "Fanout 기반 질문 확장"은 Profound의 Query Fanouts와 유사한 접근. 사용자의 주 프롬프트에서 LLM이 내부적으로 생성하는 sub-query를 역추정.
- "실제 사용자 환경에서 측정"은 Evertune의 EverPanel과 유사할 가능성 — 브라우저 확장이나 사용자 패널 기반. 또는 ChatGPT 웹 UI 자동화(Playwright/Puppeteer)를 통한 스크레이핑.
- "Action Item 제공": 리포트만이 아니라 콘텐츠 배포 제안, 보완 콘텐츠 설계, 대응 캠페인 권고까지.

**Wayne에게의 시사점**:
- 체인시프트는 **이미 한국 대기업 레퍼런스 확보에 성공**했다. 아모레퍼시픽, LG, GC녹십자 확보는 뷰티/전자/제약 카테고리 진입장벽을 사실상 차지한 상태.
- 하지만 여전히 **브랜드 단위 추적 + 에이전시형 컨설팅** 모델이다. **제품 단위(SKU-level) 최적화**와 **네이버 쇼핑/쿠팡 카탈로그 구조화**는 아직 비어있음.
- TIPS 선정 4개월, 누적매출 3.5억 → Wayne의 예비창업패키지와 겹치지 않는 트랙. 체인시프트가 시리즈 A를 받는 시점(2026년 하반기 예상)이 Wayne의 MVP 출시 데드라인.

---

### 3.10 기타 중요 회사 — 핵심만

- **Bluefish AI**: 엔터 브랜드 안전/평판 중심. Claude/AI Mode 커버 안 함. Fortune 500이지만 커뮤니케이션 팀 타겟.
- **Goodie AI**: 11개 모델 커버 (업계 최다) 포함 Rufus. 엔터 전용 데모 판매.
- **Peec AI**: $95부터, Mixpanel 스타일 UI. 유럽 저예산 대표.
- **Writesonic**: 기존 콘텐츠 SaaS가 GEO로 확장. Microsoft 파트너십으로 B2B 구매자 대상 포지셔닝.
- **Gauge**: Y Combinator, Actions Center가 차별점. 경쟁사 정확히 어떻게 이기는지 gap analysis.
- **Searchable** (런던): 2025.12 시드 $4M, 12,000+ 브랜드. 끝까지 살아남을지 불투명.
- **BrandLight**: CB Insights GEO Leader. $30M Series A.
- **Relixir**: YC X25, "자율 GEO 직원 Rex"를 내세움. 아직 실체 불투명.

---

## 4. 모든 회사가 공통으로 의존하는 기술적 기반

회사들의 차별화 주장을 걷어내고 보면, **이 시장의 모든 플레이어는 아래 7가지 기본 블록 조합으로 돌아간다.** 이 시장에서 새로 진입하려면 최소한 이 7개는 다 구현할 수 있어야 한다.

### 4.1 데이터 수집 (Data Collection)
- **API-based**: OpenAI/Anthropic/Google API로 직접 프롬프트 호출. 장점: 재현성. 단점: UI-only 기능(Shopping 카드, 테이블 등) 누락.
- **Scraping-based**: Playwright/Puppeteer로 웹/앱 UI 자동화. 장점: UI-only 요소 포착. 단점: UI 변경에 깨짐.
- **Hybrid**: 둘 다 (Evertune, Azoma, Siteline).
- **Panel-based**: 실제 사용자의 브라우저 확장/앱에서 응답 수집 (Evertune EverPanel, 체인시프트 추정).

### 4.2 프롬프트 생성 (Prompt Synthesis)
- 고객이 직접 정의 (BYO)
- 키워드 → 자연어 변환 (Scrunch, Ahrefs Brand Radar)
- 실제 유저 대화 로그 기반 추정 (Profound Prompt Volumes, 400M+ 대화 기반)
- 시장 조사/경쟁사 분석 기반 자동 생성 (AthenaHQ)

### 4.3 답변 파싱 (Response Parsing)
- Named Entity Recognition으로 브랜드 추출
- 순위 파싱 (목록/표/문단에서의 위치)
- 감정 분석 (긍정/부정/중립)
- 인용 URL 파싱
- 이미지/카드 요소 파싱 (ChatGPT Shopping 카드, Rufus 제품 카드 등)

### 4.4 통계 집계 (Statistical Aggregation)
- 동일 프롬프트 N회 반복 → 평균
- 시계열 (time series)
- 경쟁사 대비 Share of Voice (SoV)
- 신뢰구간/표준편차 (Profound, Evertune만 명시)

### 4.5 Content / Structured Data 생성
- JSON-LD Schema.org 마크업 자동 생성
- llms.txt 파일 자동 생성 (Indexly 등)
- Product/Offer/AggregateRating 스키마 채우기
- A+ Content, 인포그래픽, lifestyle 이미지 (Ecomtent)
- Q&A 포맷 재구성 (모든 회사)
- Knowledge Graph (WordLift)

### 4.6 배포 (Distribution)
- CMS 직접 통합: WordPress, Webflow, Sanity, Contentful, Framer (Profound, AirOps)
- 이커머스 플랫폼 연동: Shopify(Profound via Nostra, AthenaHQ, Alhena), BigCommerce(Feedonomics)
- 마켓플레이스 피드: Amazon Merchant, Walmart, ChatGPT Product Feed (15분 주기 갱신 가능)
- 제3자 소스 콘텐츠 배포 (Azoma의 Syndication, Evertune의 Programmatic)
- Reddit 등 커뮤니티 공략 (Soar, Writesonic)

### 4.7 귀속 (Attribution)
- 서버 로그에서 AI 크롤러 User-Agent 식별 (Profound Agent Analytics)
- GA4 + Search Console 연동 (AthenaHQ, Azoma, Adobe)
- 전환 이벤트 연동 (Shopify 웹훅, CRM)
- 브랜드 검색량 lift 분석 (체인시프트)

---

## 5. 이커머스/제품 단위 최적화의 실제 동작 — Amazon Rufus와 ChatGPT Shopping 사례

제품 단위 AiEO가 실제로 어떻게 돌아가는지, 두 대표 서피스의 메커니즘으로 설명한다.

### 5.1 Amazon Rufus (Amazon 자체 논문 기반)

Rufus는 다음 단계로 제품을 추천한다:
1. **유저 쿼리**: "Can I use this fishing reel in salt water?"
2. **제품 카탈로그 조회**: Amazon PIM에서 해당 ASIN의 제목/bullet/설명 + review embedding 검색
3. **SPN(Subjective Product Needs) 매칭**: 유저 쿼리의 의도를 5가지 facet(Subjective Properties / Event Relevance / Activity Suitability / Goal-Purpose / Target Audience)으로 분해 → 제품의 해당 facet 언급 강도 계산
4. **Web 보강**: Amazon 외부(제조사 사이트, 리뷰 사이트) 정보도 인용
5. **답변 생성**: 2~3개 제품 추천 + 근거 설명

**최적화 로직**: 각 facet에 대한 명시적 언급을 제목/bullet/설명에 심음. 리뷰에도 해당 언어가 나오도록 리뷰 프롬프팅. A+ Content에 lifestyle context 포함.

### 5.2 ChatGPT Shopping (2026년 초 기준)

- **Product Feed 제출**: CSV/TSV/XML/JSON으로 OpenAI에 직접 푸시. 15분 주기까지 갱신 가능.
- **필수 필드**: product ID, title, description, price, availability, images, GTIN, brand, condition
- **AI-중요 필드 (대부분 브랜드가 놓침)**: `product_review_count`, `average_rating`, `return_policy`, `shipping_details`, `popularity_score`, `video_link`, `model_3d_link`
- **검색/체크아웃 플래그**: `enable_search=true`, `enable_checkout=true` (ACP 준수 필요 시 Stripe 연동)
- **트리거 로직 (Profound 리서치)**: ChatGPT Shopping 카드는 전체 프롬프트의 10% 미만에서만 트리거됨. **제품 카테고리가 "Amazon에서 살 만한 것"인지가 강력한 트리거.** 서비스/소프트웨어/여행은 거의 트리거 안 됨.
- **안정성**: 한 번 트리거된 카테고리는 다음날도 83% 확률로 다시 트리거. 하지만 모델 업데이트 시 초기화됨.

**최적화 로직**:
1. 피드 완성도 최대화 (모든 선택적 필드 포함)
2. JSON-LD 스키마와 피드 가격/재고 일치시키기
3. 제목을 "카테고리 + 주요 속성 + 브랜드" 구조로 (예: "waterproof hiking boots, ankle support, size 10, BrandX")
4. 리뷰 수/평점을 피드에 직접 포함
5. 정기적(15분~1시간) 피드 갱신 자동화

---

## 6. Wayne을 위한 결론

리서치 전체를 요약했을 때 보이는 **공간과 위험**을 직설적으로 적는다.

### 6.1 열려 있는 공간
1. **한국 제품 DB 연동**: 네이버 쇼핑, 쿠팡 카탈로그에 직접 연동해 제품 속성을 LLM 친화적으로 구조화하는 솔루션은 아직 없다. 체인시프트도 이걸 하지 않는다.
2. **중소 셀러 타겟의 Ecomtent 한국 버전**: Ecomtent이 Amazon/Walmart에서 하는 걸 네이버 스마트스토어/쿠팡/11번가에서 하는 회사가 없다. 카테고리 단위 SPN 추출은 한국 리뷰 데이터에 그대로 적용 가능.
3. **AMP (Agentic Merchandising Protocol) 대응**: Azoma가 프로토콜을 제안했고, OpenAI가 ACP를 내놨다. 한국 플랫폼(네이버, 쿠팡)이 이 프로토콜을 언제 수용할지는 불확실하지만, **프로토콜 어댑터 레이어**는 명확한 B2B 기회.
4. **Query Fanout 실측**: 아무도 제대로 못 하고 있다는 게 이 시장의 공공연한 비밀. 여기에 정면으로 기술 실험을 걸면 데이터 리서치 콘텐츠 자체가 마케팅 자산.

### 6.2 위험
1. **Profound가 Asset Hierarchies(제품 단위 추적)를 2026년 3월 출시**했다. 6개월 내로 Ecomtent/Azoma 수준까지 기능이 올라올 가능성이 있다.
2. **체인시프트의 한국 대기업 레퍼런스 선점**. 브랜드 단위 영업에서는 이미 늦었다. 제품 단위/중소 셀러 타겟으로 차별화해야 한다.
3. **시장 포화 속도**: 2024년 하반기부터 2026년 4월까지 52개 플랫폼. 2026년 말까지 최소 10~20개는 쉬다운 또는 M&A될 것. Wayne의 구체적 "존재 이유"가 18개월 내 시장에 뚜렷해지지 않으면 휩쓸린다.
4. **측정 신뢰도 문제가 이 시장 전체의 엔드게임**. SparkToro+CMU 연구가 보여준 확률성 이슈는 고객이 깊게 물어볼수록 치명적. 이걸 정면으로 다루는 솔루션(high prompt volume + 신뢰구간 리포팅)이 장기 승자가 될 가능성 높음.
5. **한국 언어 모델 커버리지**: HyperCLOVA, 네이버 Cue 등이 이커머스 검색에 본격 들어올 때 어떻게 대응할지. 글로벌 플레이어(Profound/Azoma)는 한국어에 약함. 이게 Wayne의 기회이자 리스크.

### 6.3 구체적 권고 (비판적)
- **브랜드 단위 추적은 하지 마라.** 체인시프트가 이미 대기업 선점. 모니터링 경쟁은 패배 게임.
- **제품 단위, 특히 한국 이커머스(네이버/쿠팡) 카탈로그 최적화로 좁혀라.** 여기가 Wayne의 기존 창업 경험(배달 서비스 2년 + 7개 스타트업)과 공인중개사 자격을 포함한 한국 시장 이해와 가장 맞닿는다.
- **Ecomtent → Azoma의 경로를 모방할 가능성을 두라.** 중소 셀러용 SaaS로 PMF 잡고, 대기업 엔터 라인은 별도 브랜드로 분리.
- **MVP에서 Query Fanout 실측 또는 확률성 보정 신뢰구간을 포함하라.** 이게 측정 신뢰도 문제에 대한 정직한 기술적 응답이 된다.
- **용어 선점**: AiEO를 한국 표준 용어로 밀 거라면, 2026년 상반기 내에 한국어 리서치 리포트/블로그/세미나를 통해 일관되게 확산시켜야 한다. 책이 이미 나왔기 때문에(2026.3 『된다! AI 상위 노출』) 용어 선점 자체는 불가능에 가깝고, **"제품 단위 AiEO"**로 정의를 좁히는 게 더 실용적.

---

## 7. 참고 자료 (Reference List)

공식 홈페이지/블로그:
- Profound: https://www.tryprofound.com
- Scrunch AI: https://scrunch.com
- Evertune: https://www.evertune.ai
- AthenaHQ: https://athenahq.ai
- Ecomtent: https://www.ecomtent.ai
- Azoma: https://www.azoma.ai
- 체인시프트: https://www.trychainshift.ai
- Adobe LLM Optimizer: https://business.adobe.com/products/llm-optimizer.html

주요 시장 리서치/리포트:
- Plate Lunch Collective, "AEO & GEO Tools: 52 AI Search Visibility Platforms Compared" (2026.4, 매달 갱신)
- SparkToro, "AIs Are Highly Inconsistent When Recommending Brands" (2026.1)
- Carnegie Mellon, "Estimating LLM Consistency" (ACL 2025)
- Amazon, "A Shopping Agent for Addressing Subjective Product Needs" (2024)
- Bain, "Marketing's New Middleman: AI Agents"
- FTI Consulting, "Great Visibility Reset"
- TechCrunch: Profound ("move over SEO", 2024.8), Scrunch AI (2025.3)
- VentureBeat: Azoma AMP 발표 기사 (2026.3)
- 다음/매일경제/네이트뉴스: 체인시프트 TIPS 선정 (2025.11)

---

**끝. 추가로 특정 회사의 기술 스택, 리크루팅 흐름, 또는 Wayne의 AiEO 포지셔닝 문서(예비창업패키지 지원용 섹션 구성)가 필요하면 별도로 작업해.**
