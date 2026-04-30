---
date: 2026-04-30
type: competitor_research
status: verified
sources: 4 parallel agent research tracks (general-purpose subagents)
url_verification: 1차 출처 cross-reference (Wayne의 URL 검증 룰 준수, 검증 실패 시 unverified로 표기)
related:
  - docs/knowledge/findings/AiEO_경쟁사_리서치.md (2026-04-24, 선행)
  - docs/knowledge/findings/ai_product_visibility_landscape_2026-04-24.md (선행)
  - consulting/action_roadmap.md (12주 실행 로드맵)
---

# AiEO/GEO 경쟁사 풍경 갱신 — 2026-04-30

기존 두 리서치(2026-04-24)가 미국 위주였던 점을 보완해 **JP/CN/healthcare 갭**을 메우고, 그 사이 발생한 **펀딩·메서드 변화**를 추가 검증.

## 1. 시장 funding 갱신

| 회사 | 누적 펀딩 | 최근 라운드 | 평가 |
|------|---------|-----------|------|
| Profound | $151M+ | Series C $96M @ $1B (2026-02, Kleiner) | 유니콘 도달 |
| Bluefish | $68M | Series B $43M (2026-04, NEA·Threshold) | Fortune 500 고객 (Adidas/Amex/LVMH/Ulta) |
| Evertune | $20M+ | Series A $15M (2025-08, Felicis) | NYC, 엔터프라이즈 |
| AthenaHQ | $2.7M+ | Seed (YC backed) | self-serve $95/월 + 엔터프라이즈, Coinbase/SoFi 고객 |
| Azoma (구 Ecomtent) | $4M | pre-Series A (eBay Ventures, Techstars) | CPG·뷰티 강함, L'Oréal/Unilever/Mars |
| Daydream (withdaydream) | $50M | Seed (Forerunner+Index, 2024) | 인간 SEO 전문가 + AI agent hybrid |

**해석**: 2026 상반기에 자본 유입 가속. Profound 유니콘 + Bluefish Fortune 500 진입 = 시장이 본격 enterprise화. Wayne의 GN 컨설팅 시급성 근거.

## 2. SKU/이커머스 특화 — Wayne 핵심 카테고리

| 회사 | URL | SKU-level 메커니즘 | 한국 적용 가능성 |
|------|-----|------------------|----------------|
| **Azoma** | https://www.azoma.ai/ | 가장 명시적 — "Syncing 212 SKUs" 대시보드, GEO blocker 감사(schema/JS-only/crawlability/속성), AMP 프로토콜 발표 | 직접 흡수: GEO blocker audit 패턴, 의료기기 vertical 적용 |
| **Goodie** | https://higoodie.com/ | "individual product mention frequency, ranking position, competitor placement, price accuracy". one-click feed remediation + auto FAQ + schema injection | **유일하게 정량 인과(revenue attribution + incrementality)** 주장 |
| **Bluefish** | https://www.bluefishai.com/ | ACP(Agentic Commerce Protocol) 1급 시민. enterprise 비공개 | Fortune 500 narrative entry, 한국 직접 적용 어려움 |
| AthenaHQ | https://athenahq.ai/ | brand 중심, PDP 자동수정 약함 | self-serve 진입가 낮음 |
| Daydream B2B | https://www.withdaydream.com/ | SEO 에이전시 모델 | 의료기기엔 부적합 |

**핵심**: SKU-level은 사실상 **Azoma + Goodie 2개 엔진**이 시장 정의 중. 한국 의료기기 vertical은 양사 모두 미진입.

## 3. 일본·중국 (신규 스캔)

### 일본 (3개 본격 플레이어)
- **Mieruka GEO** (Faber Company) — https://mieru-ca.com/geo/ — 자사+경쟁사 AI 노출률 비교 + **무료 진단 입구** 영업 깔때기
- **AKARUMI** — https://akarumi.jp — ChatGPT/Gemini/Claude/Perplexity/AIO 답변 저장→트렌드
- **LLM Insight** — https://llm-insight.com — 인보이스 결제 등 일본 로컬 친화

### 중국 (2개 검증)
- **加搜科技 (Jiasou/TideFlow)** — https://jiasou.cn — 글로벌 LLM + 文心一言(ERNIE) 동시 커버
- **广拓时代 (Cantotimes)** — https://www.cantotimes.com — DeepSeek/豆包/文心/通义/Kimi/腾讯元宝 6대 中国 LLM

**관찰**: 일본은 한국보다 모니터링 SaaS가 ~1년 앞서 성숙. 중국은 로컬 LLM 전용 커버리지가 글로벌 도구의 진입장벽으로 작동. **두 시장 모두 healthcare 특화는 0**.

## 4. 미국 SEO 인큐먼트의 AI 확장 (변화 큰 영역)

| 인큐먼트 | 신규 제품 | 핵심 메서드 |
|---------|---------|-----------|
| **Ahrefs** | Brand Radar (Lite $129~) | **350M+ 실제 검색 행동 데이터로 prompt corpus 자동 생성** — 차별 메서드 |
| **Semrush** | AI Visibility Toolkit ($99/월) | 25-200 커스텀 prompt, 인용 URL 집계 |
| **Conductor** | AgentStack (2026-04 출시) | ChatGPT/Claude 안에서 **native LLM 앱 + MCP 서버** |
| **BrightEdge** | AI Hyper Cube + AI Agent Insights | "AI agent 요청이 인간 organic의 88% 도달, 2026 말 추월 예상" |

**흡수 가치 1순위**: **Ahrefs의 real-search-behavior 기반 prompt corpus**. 우리 Q1×Q2가 합성이라 약점 — 네이버 데이터랩/Google Trends/(가능하면) panel로 보강하는 단계 신설 검토.

**Watch-list (즉시 X)**: Conductor MCP 서버 — 컨설팅 산출물의 미래 형태(LLM 안에서 도구로 작동)를 시사하나 우리 단기 로드맵엔 과함. 분기별 모니터.

## 5. Healthcare/의료기기 도메인 — 글로벌 갭 확정

본 리서치 검증 범위 내 healthcare 자체 측정 엔진을 가진 GEO SaaS = **0개**. healthcare-specific 영업하는 곳은 모두 *에이전시형*(MarketEngine, Inbound Medic, EOS, True North 등)이고 자체 도구 없음.

| 후보 | 정직 평가 |
|------|---------|
| MarketEngine LLM Visibility Medical Device Case Study | 블로그성 사례, 자체 도구 부재 |
| Inbound Medic | 콘텐츠 마케팅 only |
| EOS Healthcare / True North | 마케팅 에이전시 메뉴 추가 |

healthcare-vertical SaaS 진영(Doximity, Healthgrades, ZocDoc) **GEO 미진입**. **Wayne의 의료기기 컨설팅 포지션은 한국이 아니라 글로벌 차원으로 비어있음** — 이게 컨설팅 차별화 메시지 1순위.

## 6. Methodology 정렬 — 인과 vs 관찰

전체 11+ 글로벌 GEO 도구를 메서드 차원으로 분해하면:

| 차원 | 글로벌 vendor 99% | Wayne 우리 | 평가 |
|------|------------------|----------|------|
| Prompt 측정 | 매일 자동 호출 시계열 | 직교배열 + 15-20반복 + R1-R10 | 동등(우리가 더 엄격) |
| 인과 추론 | **없음** (관찰 대시보드만) | F1~F6 통제 실험 + 로지스틱 회귀 + odds ratio + 교호작용 | **Wayne 단독 우위** |
| 예측 모델 | "billions of signals" 마케팅 (블랙박스) | XGBoost + SHAP, 버티컬 분리, 해석가능성 | **Wayne 우위** |
| Agent Analytics (서버 로그) | Profound만 | 미구현 | **흡수 후보** |
| 데이터 기반 prompt | Ahrefs/Profound | 합성 쿼리 | **흡수 후보** |
| AXP cloaking | Scrunch만 | 안 함 | **의식적 회피 (의료 컴플라이언스 위험)** |

**컨설팅 차별화 메시지 정렬**:
1. "글로벌 GEO 도구 11+ 모두 *관찰*. 페이지 요인을 *인과*로 분해하는 곳은 0개."
2. "의료기기 vertical 자체 측정 엔진은 글로벌 0개. 한국 GN 컨설팅 = 글로벌 첫 사례."
3. "AXP 같은 cloaking은 학술/의료 컴플라이언스 양쪽에서 회피. 통제 실험 + 인과 결론으로 방어."

## 7. 기존 action_roadmap.md에 끼울 항목 (delta)

- **Stage 1.6 — 쿼리셋 데이터 기반 보강 (신설, 1주)**: Ahrefs Brand Radar 메서드 부분 차용. 네이버 데이터랩 + Google Trends + (가능 시) 실 panel로 한국 의료기기 prompt corpus 추출 → Q1×Q2 외부 타당성 보강
- **§2.5 — 인과 vs 관찰 차별화 메시지 명시 (신설)**: 위 6번 표를 컨설팅 슬라이드 1장으로 별도 제작
- **§4 타임라인 — watch-list 칼럼 추가**: AMP/ACP, Conductor MCP, Profound Index 신규 산업 — 분기별 모니터
- **§7 관련 문서**: 본 finding(F2026-04-30) 추가

## 8. 의식적으로 안 흡수 (위험 회피)

- **Scrunch AXP cloaking**: LLM-only 페이지 서빙 — 의료기기 광고 규제·OpenAI 정책 양쪽 위험. 권고 X.
- **"billions of signals" 식 블랙박스 reasoning model 마케팅**: 학술 정당화·재현성 룰(R8 raw 보존)과 충돌
- **AMP/ACP 즉시 대응**: 의료기기는 표준 안정화까지 watch만. 2026 후반~2027 재검토
- **Skylar**: getskylar.com은 영업 코칭이라 GEO 카테고리 아님 — 추정 적층 금지

## 9. 검증 실패 / 보류

- 한국 "랭크잇" AI 확장 (공식 발표 미확인)
- 중국 透镜GEO (TIMUS.AI 도메인 검증 실패)
- 일본 Pascal/Keywordmap GEO 기능 (LLMO 라벨 사용 1차 미확인)
- "Lumar" GEO 모듈 (URL 검증 1차 단계 통과 후 재확인 권장)

추가 검증 후 본 finding 업데이트 권고.

## Sources (1차 출처만)

### Funding · 메서드
- https://fortune.com/2026/02/24/exclusive-as-ai-threatens-search-profound-raises-96-million-to-help-brands-stay-visible/
- https://www.tryprofound.com/blog/series-b
- https://www.tryprofound.com/blog/data-driven-prompt-recommendation
- https://www.tryprofound.com/features/agent-analytics
- https://www.prnewswire.com/news-releases/bluefish-raises-43-million-series-b-to-power-agentic-marketing-for-the-fortune-500-302741124.html
- https://www.nea.com/blog/bluefish-the-ai-marketing-platform-for-the-agentic-era
- https://www.globenewswire.com/news-release/2025/08/12/3132022/0/en/Evertune-Raises-15-Million-Series-A-to-Scale-Its-AI-Marketing-and-Discovery-Platform.html
- https://venturebeat.com/infrastructure/how-to-make-your-e-commerce-product-visible-to-ai-agents-use-this-new-system
- https://www.businesswire.com/news/home/20260312137127/en/Azoma-launches-new-merchant-side-standard-for-brand-friendly-agentic-commerce
- https://nicklafferty.com/blog/profound-vs-scrunch/
- https://revenuezen.com/scrunch-ai-generative-engine-optimization/

### 인큐먼트
- https://www.semrush.com/kb/1493-ai-visibility-toolkit
- https://ahrefs.com/brand-radar
- https://ahrefs.com/blog/brand-radar-methodology/
- https://www.cmswire.com/digital-experience/conductor-launches-agentstack-for-aeo/
- https://www.businesswire.com/news/home/20260218569189/en/Conductor-Leads-the-Enterprise-AEO-Market-as-Global-Demand-Surges-Closing-FY2026-With-Record-Expansion
- https://www.globenewswire.com/news-release/2026/03/10/3252895/0/en/BrightEdge-Launches-AI-Hyper-Cube-Pulling-Back-the-Curtain-on-How-Brands-Show-Up-in-AI-Search.html

### JP/CN
- https://mieru-ca.com/geo/
- https://akarumi.jp/
- https://llm-insight.com/en/
- https://jiasou.cn/
- https://www.cantotimes.com/

### Healthcare 갭 확인
- https://www.inboundmedic.com/blog/llm-visibility-for-healthcare/
- https://marketengine.ai/blogs/index.php/2026/04/15/llm-visibility-medical-device-marketing-case-study/

### SKU 특화
- https://www.azoma.ai/, https://www.azoma.ai/enterprise
- https://higoodie.com/, https://higoodie.com/features/agentic-commerce-optimizer
- https://www.bluefishai.com/, https://www.bluefishai.com/solutions
- https://athenahq.ai/, https://athenahq.ai/plans
- https://www.withdaydream.com/, https://daydream.ing/, https://partners.daydream.ing/
