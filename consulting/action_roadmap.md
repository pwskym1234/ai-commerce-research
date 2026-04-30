;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           # 바디닥터 AiEO 실제 개선 액션 로드맵

**작성일**: 2026-04-24
**기반**: 업계 리서치 2건 (AiEO_경쟁사_리서치.md + ai_product_visibility_landscape_2026-04-24.md) + 프로젝트 실측 데이터
**대상**: Wayne + GN 본사
**범위**: 학기 프로젝트 외적 실무 개선 (본실험 분석 결과를 기다리지 않고 병렬 실행 가능한 것들)

---

## 0. 왜 병렬 실행?

프로젝트 본실험 결과(5~6주 후)를 기다리기엔 시장 변화가 빠름 — 2026년 상반기 중 ChatGPT Shopping card 트리거 로직·AMP 표준·Profound Asset Hierarchies 등이 빠르게 안정화. 지금 당장 **업계 공통 로직**만으로도 명확한 개선 방향이 있고, 본실험은 그 방향의 **효과 크기를 정량화**하는 역할.

---

## 1. 측정 (Measurement) — 무엇을 집중해서 봐야 하는가

업계(Profound/Alhena/체인시프트) 공통 측정 축. GN은 현재 아무것도 측정 안 함. 최소 다음 5개는 도입 권장.

### 1.1 프롬프트별 노출률 (Mention Frequency over Time)

**무엇**: 쿼리 유형별 (카테고리/비교/증상해결/가격) × 주요 3 LLM (ChatGPT/Gemini/Perplexity) × 월 N회 반복 후 바디닥터 멘션 비율

**왜 필요**: Profound·체인시프트 표준 지표. 경쟁사 대비 SoV (Share of Voice) 추적의 기반.

**어떻게**: 본 프로젝트의 API 실험 코드(`experiments/_RUNNER_SPEC.md`)를 확장해 월 1회 자동 실행. 30분·$5 수준.

**GN 요청 사항**: 경영진 보고용 대시보드 포맷 합의 (주간/월간).

### 1.2 Rendering 구분 (Mention vs Rich Card)

**무엇**: 단순 텍스트 멘션 vs ChatGPT Shopping·Perplexity Pro의 rich card(가격/리뷰/이미지) 렌더링 분리 카운트

**왜 필요**: Alhena 핵심 주장 — "rendering이 실제 구매 전환에 직결". 텍스트 멘션만으론 인지, 카드 렌더링이 실제 매출 유발.

**어떻게**: ChatGPT Shopping·Perplexity 응답 구조 파싱(Playwright 필요). 초기엔 수동 관찰, MVP 나오면 자동화.

### 1.3 Citation Source 분석

**무엇**: AI가 바디닥터 추천 시 인용하는 URL 분류 (자사몰 / 서울신문 / 블로그 / Reddit / 맘카페)

**왜 필요**: Profound Enhanced Citation Categories·체인시프트 "플랫폼별 인용 출처 분석"의 핵심 지표. **어느 채널에 투자해야 하는지** 의사결정 근거.

**어떻게**: 응답 본문에서 URL 추출 → 도메인 카테고리화.

### 1.4 Attribute Coverage (속성 필드 완성도)

**무엇**: GN코스몰·네이버 스마트스토어·자사몰 페이지에서 Schema.org Product 권장 필드 중 실제 채운 필드 수/전체 × 100%

**왜 필요**: Azoma·Salsify 공통 축 — "속성 필드 누락은 AI가 제품을 못 이해함"의 정량 지표. Mirakl도 동일 접근.

**어떻게**: Google Rich Results Test + 자체 크롤러. 월 1회 측정.

### 1.5 AI 크롤러 방문 로그

**무엇**: GPTBot/OAI-SearchBot/Google-Extended/PerplexityBot 등 AI 크롤러가 우리 페이지에 몇 회 방문했는지

**왜 필요**: Profound Agent Analytics 핵심. 개선 액션의 **선행 지표** (크롤러 방문 ↑ → 몇 주 후 멘션 ↑ 기대).

**어떻게**: GN코스몰 서버 액세스 로그 확보 + User-Agent 파싱. Cloudflare/Nginx 로그면 가능.

**GN 요청 사항**: 서버 로그 접근 권한 또는 월간 AI 크롤러 방문 수 요약 제공.

### 1.6 Query Corpus 데이터 기반 보강 (Ahrefs Brand Radar 메서드 차용, 2026-04-30 신설)

**무엇**: 현재 산공통/데마 쿼리셋(Q1×Q2, queries_medical_B1보존.yaml)이 합성 — Wayne·팀이 "사용자가 이렇게 묻겠지" 추정. Ahrefs Brand Radar는 **350M+ 실 검색 행동 데이터**로 prompt corpus 자동 생성. 우리도 부분 차용해서 실제 한국 사용자의 의료기기/가글 정보 탐색 패턴으로 쿼리셋 *외부 타당성* 보강.

**왜 필요**: 합성 쿼리가 실제 검색 빈도·표현 분포와 어긋나면 본실험 결과의 generalizability 약함. 발표/컨설팅 시 "이 쿼리가 진짜 시장 데이터냐"는 질문에 방어 어려움.

**어떻게**:
- 네이버 데이터랩 검색어 트렌드 (요실금 / 케겔 / EMS / 가글 / 프로폴리스 등) 빈도 매핑
- Google Trends 한국 (보조)
- (가능하면) 실제 ChatGPT/Perplexity 사용자 panel — 한국엔 panel 없음. 영문은 Profound 트라이얼/Ahrefs Brand Radar 검토
- 도출된 빈도·표현으로 Q1×Q2 가중치 보정 → queries_medical_네이버검색반영.yaml, queries_gargle_네이버검색반영.yaml

**산출**: queries_*_네이버검색반영.yaml, 데이터 출처·빈도 명시 메타데이터
**소요**: 1주, $0 (네이버 데이터랩 무료) ~ $129 (Ahrefs Brand Radar Lite 1개월)
**근거**: [F2026-04-30_competitor_landscape_update.md §4](../docs/knowledge/findings/F2026-04-30_competitor_landscape_update.md)

---

## 2. 개선 (Improvement) — 어떻게 고칠 것인가

업계 공통 **8단계 실행 루프** (Ingest→Evaluate→Enrich→Distribute→Measure from ReFiBuy + Azoma 공통). 단계별 GN 액션:

### Stage 1: Catalog Ingest (1주 내)

**무엇**: 현재 제품 정보(이름·스펙·이미지·리뷰·인증)를 한 곳에 정리된 마스터 PIM 형태로 수집

**왜**: 여러 채널(GN코스몰/스마트스토어/SK스토아/11번가)에 흩어진 정보가 불일치하면 AI가 "어느 버전이 맞나" 혼란 → 추천 확률 ↓

**액션**:
- [ ] **Product master spreadsheet** 작성: 모델명/허가번호/등급/스펙/가격/이미지/리뷰 수/평점
- [ ] 채널별 현재 노출 정보 비교표 — 불일치 항목 식별
- [ ] (GN 요청) 정식 허가번호 + 임상 자료 + 고품질 제품 이미지 10장 이상

### Stage 2: AI-Readiness Evaluate (1주 내)

**무엇**: 현 페이지가 AI가 이해하기 적합한 상태인지 Sixthshop 방식 점수화

**점수 배점 (Sixthshop 기준)**:
- Schema & Data Trust: 35점
- Content & Intent Match: 25점
- Media & Visual Signals: 20점
- Commerce & Eligibility: 20점

**현재 예상 바디닥터 점수** (실측 기반):
- Schema: JSON-LD Product만 (MedicalDevice 아님) → **10/35**
- Content: 스펙/임상/SPN 맥락 없음 → **5/25**
- Media: 이미지 많음 but alt 부족 → **10/20**
- Commerce: 리뷰 0개, 재고 정보 없음 → **5/20**
- **총 30/100** (추정)

**목표**: 3개월 내 70/100 달성.

**액션**:
- [ ] Sixthshop 무료 audit 실행 (레퍼런스)
- [ ] 자체 점수 산출 스크립트 (본 프로젝트 `extract_features.py` 확장)

### Stage 3: Content/Catalog Enrich (2~4주)

**가장 큰 개선 여지**. 현재 단독 페이지에 텍스트 거의 없음 ([F2026-04-23_empty_product_pages.md](../docs/knowledge/findings/F2026-04-23_empty_product_pages.md)).

**3.1 JSON-LD 풀 스키마 추가** (Azoma·Profound 공통 1순위):
```json
{
  "@context": "https://schema.org",
  "@type": "MedicalDevice",
  "name": "바디닥터 요실금치료기",
  "brand": { "@type": "Brand", "name": "바디닥터" },
  "manufacturer": { "@type": "Organization", "name": "(GN 확인 필요)" },
  "model": "(GN 확인 필요)",
  "identifier": { "@type": "PropertyValue", "propertyID": "KFDA", "value": "제허 XX-XXX 호" },
  "purpose": "요실금 치료, 골반저근 강화, 자동 케겔운동",
  "contraindication": "(해당 시)",
  "indication": "출산 후 회복, 요실금, 골반장기탈출 예방",
  "offers": {
    "@type": "Offer",
    "price": "2800000",
    "priceCurrency": "KRW",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2026-12-31"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "(리뷰 확보 후)",
    "reviewCount": "(리뷰 확보 후)"
  }
}
```

→ ChatGPT Shopping card 트리거 요건 충족. `aggregateRating`이 없으면 카드 렌더링 거의 안 됨.

**3.2 Rufus SPN 5 facet 명시** (Ecomtent·Amazon 논문):
- **Subjective Properties**: "간편한, 안정적인, 무소음"
- **Event Relevance**: "출산 후 회복기, 갱년기 케어"
- **Activity Suitability**: "앉아있는 동안 자동 운동, TV 시청 중 사용"
- **Goal/Purpose**: "골반저근 강화, 요실금 예방·치료, 성기능 개선"
- **Target Audience**: "출산 후 여성, 40~60대 여성, 골반약해진 남성"

→ PDP 본문에 자연스럽게 녹여 작성. AI가 "누가 왜 언제 쓰는지" 명확히 파싱 가능.

**3.3 FAQ 섹션 추가** (Scrunch·AthenaHQ 공통):
- Q&A 형식 5~10개 ("임산부가 써도 되나요?" / "식약처 3등급이 무슨 의미인가요?" / "이지케이와 차이는?")
- JSON-LD FAQPage 스키마 병기

**3.4 비교 콘텐츠** (Recomaze·Goodie 공통):
- "바디닥터 vs 이지케이 비교표" 섹션 (등급/가격/차별점)
- AI가 비교형 쿼리에 쉽게 인용 가능

**3.5 인증 정보 상단 배너** (F4·F5 풀):
- 페이지 상단 Hero 바로 아래 "식약처 3등급 + 허가번호 제허 XX-XXX 호 + FDA Class 1·2 등록" 풀 텍스트

**3.6 스펙 TABLE**:
- "99단계 강도, 5단계 자동 프로그램, 주파수 XX Hz, 사용 시간 15분/회" 구조화

### Stage 4: External Evidence (1~3개월, 가장 중요)

리서치 §10.4 반복: **"페이지만 고쳐서는 부족. External Evidence War"**.

**4.1 리뷰 확보 캠페인** (필수):
- 기존 구매 고객 대상 리뷰 작성 요청 (쿠폰·샘플 보상)
- 목표: 1개월 내 리뷰 수 50+, 평균 4.0+

**4.2 전문가 감수 콘텐츠** (차별):
- 산부인과 의사 1~2명과 협업해 "산후 회복 가이드" 콘텐츠 제작
- 의사 실명·소속 명시 → Schema.org `reviewedBy`
- 블로그/네이버 지식iN 배포

**4.3 맘카페·Reddit 시딩** (Azoma·Evertune 전략):
- 맘스홀릭·시크하우스 등 육아 커뮤니티에 "산후 요실금 리얼 후기" 시리즈
- Reddit r/Korea / r/AskKorea에 영문 케이스 (해외 AI 학습 편향 대응)
- **명시 원칙**: PR 표기 + 실사용 후기. 조작 금지 (정당성 + 플랫폼 처벌 회피)

**4.4 의료·헬스 전문지**:
- 코메디닷컴·헬스조선 등에 기고 (요실금 통계/PFMT 중요성)
- 자사 링크는 한 번만. 주로 브랜드 언급 + 의료 전문성 어필.

**4.5 유튜브 리뷰**:
- 건강·의료 유튜버 섭외 (특정 거래 표기 필수)
- 홈쇼핑 방영본과 별도 구축

### Stage 5: Distribute (채널 전반)

**무엇**: 위 콘텐츠·개선을 모든 판매 채널에 일관되게 반영

**채널별 우선순위**:
1. **GN코스몰** (자체 운영) — 가장 빠름, 바로 JSON-LD 추가 가능
2. **네이버 스마트스토어** — SEO·AiEO 모두 강함, 반드시
3. **쿠팡** — 검색량 큰 채널
4. **11번가/SK스토아** — 홈쇼핑 연계 (세라젬·이지케이 전례)

**GN 요청 사항**:
- 각 채널 수정 권한 위임 or 개선안 승인 프로세스

### Stage 6: Measure Lift (매월)

- 1.1~1.5 측정 지표 월간 추적
- Before/After 비교 (3개월 베이스라인 vs 개선 후)
- 매출 귀속: GA4 + 주문 경로 분석 (AI referral 추적 difficult but 가능)

---

## 2.5 메서드 차별화 framing — 인과 vs 관찰 (2026-04-30 신설)

본 프로젝트의 학술·컨설팅 양쪽 차별축. 발표/제안서 슬라이드 1장으로 별도 제작 권장.

글로벌 GEO 도구 11+ (Profound·Bluefish·Scrunch·Otterly·AthenaHQ·Goodie·Azoma·Daydream·Conductor AgentStack·BrightEdge AI Hyper Cube·Semrush AI Toolkit·Ahrefs Brand Radar) **모두 관찰형 대시보드**. 페이지 요인을 *인과*로 분해하는 곳은 0개.

| 차원 | 글로벌 vendor 99% | 우리 (산공통+데마) | 평가 |
|------|------------------|---------------------|------|
| Prompt 측정 | 매일 자동 호출 시계열 | 직교배열(L54) + 15-20반복 + R1-R10 강제 | 동등(우리 더 엄격) |
| **인과 추론** | **없음** (visibility/SoV/sentiment 대시보드만) | F1~F6 통제 실험 + 로지스틱 회귀 + odds ratio + 교호작용 | **우리 단독 우위** |
| 예측 모델 | "billions of signals" 마케팅 (블랙박스) | XGBoost + SHAP + 버티컬 분리 | 우리 우위 (해석가능성) |
| Agent Analytics | Profound만 (서버 로그) | 미구현 | 흡수 후보 (§1.5) |
| Data 기반 prompt | Ahrefs/Profound | 합성 (보정 권장) | 흡수 후보 (§1.6) |
| AXP cloaking | Scrunch만 | 안 함 | 의식적 회피 (의료 컴플라이언스 위험) |

**컨설팅·발표 메시지 정렬**:
1. "글로벌 GEO 도구 11+ 모두 관찰형. 페이지 요인을 *인과*로 분해하는 곳은 0개 — 우리만의 차별축."
2. "의료기기 vertical 자체 측정 엔진은 글로벌 0개. 한국 GN 컨설팅 = 글로벌 첫 사례."
3. "AXP cloaking은 의료 컴플라이언스 위험으로 회피. 통제 실험 + 인과 결론으로 방어."

**근거**: [F2026-04-30_competitor_landscape_update.md §6](../docs/knowledge/findings/F2026-04-30_competitor_landscape_update.md)

---

## 3. GN 본사에 요청할 것 (정리)

위 내용 중 GN 측 입력 필요 항목 최종 정리:

### 필수 (P0, 프로젝트 진행에 필요)
1. **식약처 정확한 허가번호 + 품목명 + 제조사 법인명**
2. **FDA 등록 번호 (Class 1·2 각각)**
3. **임상 자료** (사내 or 파트너 RCT)
4. **페이지 수정 권한** (GN코스몰/스마트스토어/자사몰)
5. **서버 로그** (AI 크롤러 User-Agent 분석용)

### 강 권장 (P1, 개선 실효성 차이)
6. **리뷰 캠페인 예산** (쿠폰·샘플 10만원~) + 허가
7. **고품질 제품 이미지 재촬영** (Hero·lifestyle·세부 부품 각 장면)
8. **전문가 감수 파트너 섭외** (산부인과 1~2명)
9. **판매 실적 공유** (월별/채널별) — AiEO 기여도 분석용

### 협의 필요 (P2, 중기 투자)
10. **외부 시딩 콘텐츠 예산** (맘카페·Reddit·유튜브)
11. **AMP/ACP 프로토콜 대응** 로드맵 (장기)
12. **차세대 제품 로드맵 공유** — AiEO 차별축 설계 근거
13. **경쟁사 정보 공유** (영업팀 내부 자료)

→ 자세한 문항은 [gn_requests.md](gn_requests.md) 참조.

---

## 4. 타임라인

| 주차 | 측정 | 개선 | GN 요청 |
|------|------|------|---------|
| W1 | Baseline 측정 (현재 상태) | Ingest 완료 | P0 항목 전부 |
| W2 | - | JSON-LD 풀 스키마 적용 | 페이지 수정 권한 |
| W3 | 1차 재측정 | SPN + FAQ + 비교 콘텐츠 추가 | - |
| W4 | - | 인증 배너 + 스펙 테이블 | - |
| W5 | 2차 재측정 | 리뷰 캠페인 시작 | 리뷰 예산 확보 |
| W6~8 | - | 맘카페·Reddit 시딩 | P2 예산 협의 |
| W9~12 | 3차 재측정 (Before/After 산출) | 전문가 감수 콘텐츠 | - |

→ **12주 후 유의미한 Before/After 측정 가능**. 본 프로젝트 발표(7주)와 병행해, **발표엔 W1~W6 결과가 포함** → "개선 시작 후 6주 만에 X% 변화" 임팩트.

### 4.1 Watch-list (분기별 모니터, 2026-04-30 신설)

GEO/AiEO 시장 변동 빠름 — Profound가 한 라운드에 $96M 받은 게 두 달 전(2026-02). 분기마다 한 번 점검.

| 항목 | 변동 빈도 | 다음 검토 | 트리거 시 액션 |
|------|---------|---------|--------------|
| AMP (Azoma) / ACP (Bluefish) 표준 | 분기 | 2026-07-30 | 의료기기 어댑터 사양 검토, GN 공유 |
| Conductor AgentStack + MCP 서버 (LLM 안에서 native 도구) | 분기 | 2026-07-30 | 산출물 미래 형태 시사, 컨설팅 산출물 포맷 재고 |
| Profound Index 신규 산업 (현 12개) — 한국 healthcare 진입 시 | 분기 | 2026-07-30 | 즉시 컨설팅 차별화 메시지 갱신 |
| 한국 healthcare GEO vendor 진입 (현 0개) | 분기 | 2026-07-30 | 컨설팅 first-mover 윈도우 종료 — 영업 가속 |

**근거**: [F2026-04-30_competitor_landscape_update.md §4-7](../docs/knowledge/findings/F2026-04-30_competitor_landscape_update.md). 자동 분기 모니터링은 background agent 스케줄 검토 중 (Wayne 결정 대기).

---

## 5. 예상 효과 크기 (업계 벤치마크)

| 개선 항목 | 업계 벤치마크 lift | 우리 예상 |
|---------|----------------|--------|
| JSON-LD MedicalDevice 전면 추가 | Ecomtent 고객 평균 +30~60% AI mention | +40% (보수적) |
| Rufus SPN 5 facet 추가 | Amazon 논문 효과 크기 ~2x | +50% |
| 리뷰 50+ 확보 | ChatGPT Shopping card 트리거 가능 → rich render +300% | (rich card 측정은 MVP 이월) |
| 인증 풀 명시 | 업계 일반 ~+15% | +15~25% |
| 맘카페 시딩 3개월 | Evertune programmatic 사례 ~+20% | +10~20% (한국 특화 미검증) |

### ⚠️ Before/After baseline 수정 (2026-04-24)

**변경 전**: Wayne 진단 리포트(dashboard-ruby-kappa.vercel.app)의 CAT 추천율 14.5%를 Before baseline으로 사용.

**변경 사유**: 진단 리포트의 **쿼리 프롬프트 구성이 이상**하다는 Wayne 피드백. 수치 자체 신뢰 X. **쿼리 유형 분류 구조(BRD/CAT/SYM/CMP/COM)만 참고**로 제한.

**새 baseline**: **본실험(L54 × 8쿼리 × 20회 = 8,640 호출) 결과를 Before baseline으로 사용**. F=현 바디닥터 수준(= F1 PARAGRAPH, F2 None or Product-Minimal, F3 Ambiguous, F4 None, F5 None, F6 None) 조합의 Y2a 값이 실제 현재 추천율.

**After 목표**: 본실험 "F=풀 명시 조합"(F1=TABLE, F2=MedicalDevice-Full, F3=Accurate, F4=Top, F5=Full, F6=Clinical) Y2a 수준까지 도달. **정량 목표는 본실험 결과 후 확정**.

**핵심 차별**: 수치 기반 주장 대신 **본실험의 인과 효과 크기**로 정량 제시. 이게 학술적으로도 컨설팅적으로도 훨씬 방어 가능.

---

## 6. 위험 & 대응

| 위험 | 대응 |
|------|------|
| GN이 페이지 수정 권한 안 줌 | 개선안 문서화 후 GN 대행사 협업 또는 경영진 설득 |
| 리뷰 캠페인 법적 이슈 (공정위 표시광고법) | 리뷰 작성자에 대가성 명시 + "내돈내산" 조작 금지 |
| 경쟁사 (세라젬 등 대기업)의 빠른 벤치 | 차별축 (의료기기 3등급 + FDA 풀 패키지) 조기 선점 |
| 측정 도구 MVP 미완 | Profound·체인시프트 상용 툴 1개월 유료 체험으로 초기 데이터 확보 |

---

## 7. 관련 문서

- [gn_requests.md](gn_requests.md) — GN에 전달할 질문 리스트
- [docs/knowledge/findings/AiEO_경쟁사_리서치.md](../docs/knowledge/findings/AiEO_경쟁사_리서치.md) — 업계 리서치 1 (2026-04-24)
- [docs/knowledge/findings/ai_product_visibility_landscape_2026-04-24.md](../docs/knowledge/findings/ai_product_visibility_landscape_2026-04-24.md) — 업계 리서치 2 (2026-04-24)
- **[docs/knowledge/findings/F2026-04-30_competitor_landscape_update.md](../docs/knowledge/findings/F2026-04-30_competitor_landscape_update.md) — 경쟁사 풍경 갱신 (delta 5개): Profound Series C, Bluefish Series B, JP/CN 시장, 인과 vs 관찰 framing, healthcare 글로벌 갭**
- [docs/knowledge/findings/F2026-04-24_hypothesis_upgrade.md](../docs/knowledge/findings/F2026-04-24_hypothesis_upgrade.md) — 가설·F 요인 고도화
- [docs/knowledge/findings/F2026-04-24_feature_comparison.md](../docs/knowledge/findings/F2026-04-24_feature_comparison.md) — 실측 피처 비교
