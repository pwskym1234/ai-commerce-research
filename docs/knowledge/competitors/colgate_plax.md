---
brand: 콜게이트 플렉스 (Colgate Plax)
brand_slug: colgate_plax
vertical: gargle
last_updated: 2026-04-30
data_sources:
  - https://www.colgate.com/en-us/products/mouthwash (글로벌 본사 카탈로그)
  - https://www.colgate.com/en-gb/products/mouthwash/plax-cool-mint-mouthwash (영국 Plax Cool Mint 페이지)
  - https://www.costco.co.kr/Colgate/c/Colgate (한국 코스트코 — 치약만, Plax 미입점)
  - 나무위키, 한국 위키백과
manufacturer: Colgate-Palmolive Company (글로벌)
official_url: https://www.colgate.com/
korea_official_url: ❌ 한국 공식 자사몰 없음 (colgate.co.kr는 검증 실패)
korea_distributor: ❌ 한국 공식 법인 없음. 병행수입·해외직구만
distribution_channels: [costco_kr (치약만), iHerb, ubuy.kr, caretobeauty.com, 마켓COL/맥그로서 등 병행수입몰]
f1_html_format: BULLET           # 글로벌 본사 mouthwash 카탈로그 — 카드 grid + 불릿
f2_jsonld: unknown               # 메인 카탈로그 미발견. 제품 상세는 후속 검증 필요
f3_numeric: explicit             # 99% bacteria, 24 hours, 12 hours, CPC 0.075%, 2% Hydrogen Peroxide
f4_cert_position: explicit       # ADA-accepted 명시 (Total Gum Health에서)
f5_cert_detail: ADA_seal         # "the only ADA-accepted alcohol-free oral rinse with CPC" — Total Gum Health 라인 한정
f6_evidence: clinical_marketing  # "clinically proven" + "rigorously tested" 표현 다수, 그러나 구체 논문 인용 없음
korea_mfds_status: ❌ 의약외품 허가 미확인 (병행수입 = 의약외품 정식 절차 우회)
status: confirmed_global_pending_korea
priority: medium
---

# 콜게이트 플렉스 (Colgate Plax)

## 핵심 사실

- **카테고리**: 글로벌 가글 — Colgate-Palmolive의 mouthwash 메인 라인 (Colgate Total과 더불어 양대 라인)
- **모회사**: Colgate-Palmolive Company (미국, 1806년 창업, 200여국 진출)
- **포지셔닝**: "24/7 plaque protection" + "fights 99% of bacteria" + "alcohol-free no burn"
- **글로벌 라인업**: Plax Cool Mint, Peppermint Fresh, Soft Mint 등 (지역별 변형). Total Gum Health는 별도 라인
- **한국 공식 진출 여부**: ⚠️ **공식 진출 없음**. 한국에 Colgate-Palmolive Korea 같은 공식 법인 부재. 모든 한국 판매는 병행수입/해외직구

## 한국 시장 진출 검증 (2026-04-30)

| 항목 | 검증 결과 |
|------|----------|
| 공식 한국 사이트 (colgate.co.kr) | ❌ **fetch 실패 (ECONNREFUSED)**. 도메인 자체가 활성/공식인지 불명. URL 사용 금지 |
| 한국 공식 법인 | ❌ 없음 (P&G Korea와 같은 한국 법인 없음, 병행수입만) |
| 코스트코 코리아 | ⚠️ **콜게이트 치약만 입점**, Plax 가글은 미입점 (검증: costco.co.kr/Colgate 카테고리 페이지) |
| 식약처 의약외품 등록 | ❌ **불명**. 정식 수입 채널이 없으므로 등록 동기 부재 |
| 병행수입 채널 | ✅ iHerb 코리아, ubuy.kr, caretobeauty.com/kr, 맥그로서, marketcol.com 등 |
| 한국어 페이지 | ❌ 없음 (병행수입몰의 상품 설명문만 한국어) |
| 가격대 | 영국 코스트코 4×500ml = £약 12, 한국 병행수입 단병 약 8,000~15,000원 추정 (정식 가격 부재) |

**결론**: 콜게이트 Plax는 **글로벌에선 강자지만 한국 시장은 사각지대**. 직접 경쟁사라기보단 "한국 시장에 들어오면 위협이 될 잠재 경쟁사" 포지션.

## 글로벌 본사 페이지 진단 (colgate.com/en-us/products/mouthwash, 2026-04-30 fetch)

| 요인 | 실측 | 근거 |
|------|------|------|
| F1 HTML 포맷 | **BULLET 우세** | 제품 카드 grid + benefit 불릿. FAQ도 불릿. TABLE 없음 |
| F2 JSON-LD | ❌ 메인 카탈로그 페이지에서 미발견 | Plax 단독 상세 페이지 fetch는 후속 과제 |
| F3 수치 구체성 | **explicit (높음)** | "24-hour protection against bacteria", "12-hour germ protection after eating and drinking", "2% Hydrogen Peroxide", CPC 0.075% (Total Gum Health) |
| F4 인증 위치 | **상품 카피 본문 내 노출** | "ADA-accepted" 텍스트가 Total Gum Health 설명에 들어감 |
| F5 인증 상세 | **ADA Seal of Acceptance** | "the only ADA-accepted alcohol-free oral rinse with CPC as an active ingredient" — 강력한 인증 신호 |
| F6 근거 | **clinical_marketing** | "clinically proven", "rigorously tested" 표현 다수. 구체적 논문/임상 인용은 메인 카탈로그에서 부재 |
| 리뷰 | "Ratings and Reviews" 섹션 헤더는 있지만 메인 카탈로그엔 별점/건수 미노출 (제품 상세에서 확인 필요) |

**참고**: Plax Cool Mint 영국판 페이지(`colgate.com/en-gb/products/mouthwash/plax-cool-mint-mouthwash`)는 검색에 노출되지만 직접 fetch는 미수행. 후속 과제로 남김.

## 같은 효능 영역

프로폴린스 anchor와 직접 경쟁: **구취**, **잇몸 케어**, **plaque/tartar 컨트롤**, **충치 예방**(F함유 라인). 다만 한국 시장 진출 X → 직접 경쟁 강도는 약함.

## 영문 콘텐츠 풍부도

✅ **매우 풍부**. 200국 진출 글로벌 브랜드답게 colgate.com은 멀티-region(en-us, en-gb, en-sg, ko-sg 등). Total/Plax/Optic White/PerioGard/Peroxyl 등 라인업 다양. educational content(K-Beauty Whitening 같은 cross-region 콘텐츠도 운영)도 풍부 → 영문 LLM 컨텍스트 풍부함.

## AI 추천 비교에서의 위상

- **영어 쿼리**: Listerine + Colgate + TheraBreath 3강 구도. ADA Seal 보유로 "dentist recommended" intent에서 강함
- **한국어 쿼리**: ⚠️ **호출 빈도 낮을 가능성**. 한국 공식 진출 부재 → 한국어 콘텐츠 빈약 → 한국어 LLM이 호출할 컨텍스트 부족
- **프로폴린스 대비 위협 포인트**: ADA Seal은 한국 의약외품 인증과 다른 차원의 신호. 만약 콜게이트가 한국 정식 진출하면 즉시 위협
- **현 상태에서의 약점**: 한국 시장 분석에서는 "이론적 경쟁사", 실제 한국 AI 추천에서는 빈도 낮을 것 (가설 — 본실험에서 검증)

## 주의 — Wayne 사고 재발 방지 (퓨런 사례 교훈)

- ❌ **colgate.co.kr는 공식 URL로 사용 금지** (fetch ECONNREFUSED, 1차 출처 미확인)
- ❌ "콜게이트 한국 식약처 의약외품 등록"은 단정 금지 — 검증 안 됐고 정식 수입 채널 부재
- ✅ 사용 가능 URL: colgate.com (글로벌 본사), costco.co.kr/Colgate (치약만), iHerb 등 병행수입몰
- ✅ Plax Cool Mint 글로벌 제품 페이지: [colgate.com/en-gb/products/mouthwash/plax-cool-mint-mouthwash](https://www.colgate.com/en-gb/products/mouthwash/plax-cool-mint-mouthwash) (en-gb)

## 참고 링크

- [Colgate 글로벌 본사](https://www.colgate.com/)
- [Colgate-Palmolive 미국 mouthwash 카탈로그](https://www.colgate.com/en-us/products/mouthwash)
- [Colgate Plax Cool Mint (UK)](https://www.colgate.com/en-gb/products/mouthwash/plax-cool-mint-mouthwash)
- [Colgate Total Gum Health (US, ADA-accepted)](https://www.colgate.com/en-us/products/mouthwash/colgate-total-gum-health-mouthwash-clean-mint)
- [코스트코 코리아 Colgate 카테고리](https://www.costco.co.kr/Colgate/c/Colgate) — 치약만
- [Caretobeauty Colgate Korea](https://www.caretobeauty.com/kr/colgate/) — 병행수입몰
- [나무위키 — 콜게이트](https://namu.wiki/w/%EC%BD%9C%EA%B2%8C%EC%9D%B4%ED%8A%B8)

## 미확인 / 다음 액션

- [ ] colgate.com `/en-gb/products/mouthwash/plax-cool-mint-mouthwash` 직접 fetch (F1~F6 실측, JSON-LD 확인)
- [ ] 식약처 의약품안전나라(nedrug.mfds.go.kr)에서 "Colgate" 또는 "콜게이트" 키워드 검색 — 진짜 의약외품 등록 0건인지
- [ ] 한국 가글 시장 점유율 보고서에서 콜게이트 점유율 명시 자료 확보 (현재 자료엔 한국 점유율 0% 가정)
- [ ] AI 추천 본실험에서 "한국 가글 추천" 쿼리 시 Colgate 호출 빈도 측정 — 가설 검증
