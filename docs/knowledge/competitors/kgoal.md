---
brand: kGoal (Minna Life)
brand_slug: kgoal
vertical: medical_device                    # ★ 주의 — 실제로는 "general wellness" 분류, 의료기기 아님
last_updated: 2026-04-30
data_sources:
  - https://www.kgoal.com/ (자사몰 공식)
  - https://www.kgoal.com/products/kgoal-smart-kegel-exerciser (Classic 대표 SKU)
  - https://www.kgoal.com/pages/where-to-buy (한국 distributor 명시 출처)
  - https://www.kgoal.com/products/kgoal-boost-kegel-trainer-for-men
  - https://www.kgoal.com/products/kgoal-intimflex-kegel-trainer-for-women
  - https://www.kickstarter.com/projects/892018590/kgoal-smart-kegel-trainer (창업 1차 소스)
  - https://www.prnewswire.com/news-releases/minna-life-launches-kickstarter-campaign-to-bring-kgoal-boost-to-men-300172644.html
  - https://www.biospace.com/b-minna-life-b-release-smart-kegel-training-app-device-for-your-lady-parts
  - https://www.vitalitymedical.com/kgoal-kegel-exerciser.html (US 의료유통 채널)
manufacturer: Minna Life
manufacturer_country: 미국 캘리포니아 샌프란시스코
founded_circa: 2014 (Kickstarter 캠페인 2014, 출시 2015)
kickstarter_backers: 2221
kickstarter_pledged_usd: 266917
official_urls:
  global: https://www.kgoal.com
  product_classic: https://www.kgoal.com/products/kgoal-smart-kegel-exerciser
  product_boost_men: https://www.kgoal.com/products/kgoal-boost-kegel-trainer-for-men
  product_intimflex: https://www.kgoal.com/products/kgoal-intimflex-kegel-trainer-for-women
  where_to_buy: https://www.kgoal.com/pages/where-to-buy
  korea_distributor: https://kgoal.co.kr      # ★ 1차 출처(자사 where-to-buy 페이지)에서 명시. 실 도메인 응답은 ECONNREFUSED — 사이트 운영 상태 재검증 필요
note_url_verification: "minnalife.com 추정 금지 — 자사몰은 kgoal.com이며 minnalife는 회사명·브랜드 컨테이너. 'Where to Buy' 페이지에서 한국 distributor를 kgoal.co.kr로 명시"
distribution_channels:
  - kgoal.com (D2C 글로벌)
  - Amazon US (kGoal seller)
  - Walmart.com
  - Vitality Medical / USA Wheelchair (US 의료유통)
  - PelviCoach (EU)
  - Pisces Healthcare Solutions
  - 한국: kgoal.co.kr (Where-to-Buy 페이지에 명시. 운영 상태 재검증 대상)
fda_grade: general_wellness                # ★★ 핵심 — FDA 의료기기 미규제. "general wellness" 분류
fda_510k: 없음                              # ★ 명시적 미보유. 자사 FAQ에서 "not regulated by the FDA"
ce_mark: unknown                           # 자사 페이지 미명시. EU 판매 PelviCoach 통해 간접 확인 필요
mhra_registration: unknown
mfds_grade: 없음 (한국 미등록 추정)
mfds_status: 한국 식약처 등록 없음 — kgoal.co.kr distributor도 "general wellness" 톤 추정
clinical_claim: "study of 400 women, 6 weeks, 3x/week → significant improvement" (자사 페이지 명시. 동료심사 논문 미인용)
spec_diameter_in: 1.5
spec_battery_life_hours: 2
spec_charge_time_hours: 1.5
warranty_years: 2
return_window_days: 90
price_usd_classic: 179.00                 # 자사몰 정가. 25% 프로모로 변동 (홈페이지 $80 OFF 표기)
price_usd_boost_men: unknown              # 별도 fetch 필요
korea_direct_purchase: 가능 — 한국 distributor 페이지(kgoal.co.kr) 운영 시 정식 채널, 미운영 시 D2C 직구
celebrity_or_pro_endorsement: IDEA Award + Spark Award (디자인 어워드). 의료 전문가 추천 명시 없음
f1_html_format: bullet_simple              # 스펙 영역이 단순 ul 리스트. 스펙 표 없음
f2_jsonld: not_detected                    # WebFetch 응답에 JSON-LD 미감지 (Shopify 자동 삽입 가능성은 raw 검증 필요)
f3_numeric: explicit_minimal               # "1.5 inches", "2 hours", "$179" 등 명시. 단 "Hz/mA" 같은 의료기기 spec 부재 (의료기기 아니므로 자연스러움)
f4_cert_position: none                     # ★ FDA/CE 인증 표기 자체가 없음 (general wellness이므로 의도적)
f5_cert_detail: none                       # 인증 클레임 0
f6_evidence: clinical_summary              # "400명 6주 임상" 자체 인용. 동료심사 논문 링크는 미확인
status: confirmed
priority: 글로벌 wellness D2C 비교군 (의료기기 아닌 wellness 포지션 비교 reference)
---

# kGoal (Minna Life) — 미국발 스마트 케겔의 wellness 포지션

## 핵심 사실 (검증 완료)

### 회사 구조
- **법인**: Minna Life (미국 캘리포니아 샌프란시스코)
- **설립 시점**: Kickstarter 캠페인 2014년, 출시 2015년 — Perifit(2018), Elvie(2017)보다 **글로벌 1세대 스마트 케겔**
- **Kickstarter**: 2,221명 후원, 총 $266,917 펀딩 (성공 사례)
- **수상**: IDEA Award, Spark Award (디자인 어워드)
- **포지셔닝**: "the world's first fitness tracker for your kegels" — 의료기기 아닌 *fitness/wellness* 포지션

### URL 검증 (Wayne 룰 준수)
- ✅ **kgoal.com** — 자사몰 공식 도메인. 모든 제품·distributor 정보 1차 출처
- ⚠️ "minnalife.com을 자사몰로 추정 금지" — Minna Life는 회사명, 자사몰은 kgoal.com (Wayne 사례: 퓨런 furenhealth.com 오류 패턴 회피)
- ⚠️ **kgoal.co.kr** — 한국 distributor로 자사 Where-to-Buy 페이지에 명시되어 있으나, 실제 fetch는 `ECONNREFUSED`. 운영 중단 가능성 — Phase B2 전 재검증 필수

### 라인업 (Wayne 요청대로 대표 1개만 진단)
대표 SKU: **kGoal Classic** (자사 main, $179)
- kGoal Classic — 여성용 인서트 (본 진단 대상)
- kGoal Boost — 남성용 sit-on 외부 센서
- kGoal IntimFlex — Irina Pivtsaikina LiBDO 프로그램 협업판

### ★ 인증 (확정) — 의료기기 아님 ★
- **FDA**: ❌ **미규제** (general wellness 분류). 자사 페이지에서 "not regulated by the FDA and has not been tested in published clinical studies" 명시
- **CE / MHRA**: 페이지 미명시 (EU 판매는 PelviCoach 채널 통해서만)
- **한국 식약처**: 등록 없음
- → 의료기기 클레임 0, "fitness tracker for kegels" 포지션이 일관됨

### kGoal Classic 스펙 (자사몰 검증)
- **최대 직경**: 1.5 inches (3.8cm)
- **배터리 사용 시간**: at least 2 hours
- **충전 시간**: 1.5 hours
- **보증**: 2년 제조사 보증
- **반품**: 90일 환불
- 앱 연동 (Bluetooth biofeedback, 360도 센싱, 공기쿠션 압력 감지)

### 임상 주장 (자사 인용)
- "A study of 400 women exercising with kGoal 3x per week for 6 weeks found significant improvements in pelvic floor muscle strength, endurance and control"
- → **동료심사 저널 링크 없음**. Perifit(2024 PMC PubMed 논문 인용)과 대조적

### 가격 (검증)
- **kGoal Classic**: $179.00 (자사몰 정가)
- 프로모: 25% OFF / "$80 OFF Boost and kGoal Classic"
- 한국 직구: 자사몰 international shipping 가능 ("Shipments outside of the US may be subject to additional taxes and customs fees"). 한국 distributor kgoal.co.kr 운영 상태 재검증 필요

## 페이지 진단 — kGoal Classic 자사몰 (F1~F6)

| 항목 | 상태 (검증) | F 등급 |
|------|------------|-------|
| HTML 포맷 | 단순 `<ul>/<li>` 불릿. 스펙 표 없음. 본문 단락은 마케팅 문구 위주 | F1 = **bullet_simple** |
| JSON-LD | WebFetch 응답에 미감지. Shopify 자동 삽입 가능성은 raw 검증 필요 | F2 = **not_detected** |
| 수치 구체성 | 직경 1.5", 2h 배터리, 1.5h 충전, $179, 6주 임상 등 명시. Hz/mA 같은 의료 spec 부재 (의도적) | F3 = **explicit_minimal** |
| 인증 위치 | **없음** (general wellness 포지션과 일관) | F4 = **none** |
| 인증 상세 | **없음** | F5 = **none** |
| 임상/근거 | "400명, 6주, 3x/week" 자체 인용. 동료심사 링크·임상시험 등록번호 부재 | F6 = **clinical_summary** |

## ★★ 발견 — "wellness 포지션 D2C"의 깨끗한 대조군

| 비교 항목 | 바디닥터K | 이지케이 | Kegel8 (UK) | Perifit (FR) | **kGoal (US)** |
|----------|----------|---------|-------------|--------------|---------------|
| 의료기기 등급 | 식약처 3등급 | 식약처 3등급 | UK Class IIa | FDA Class II (K221476) | **분류 없음 (wellness)** |
| 인증 페이지 명시 | 부분 | 거의 없음 | 본문 명시 | FAQ 명시 | **의도적 0** |
| 임상 근거 | 후기 위주 | 셀럽 광고 | NHS 인용 + Trustpilot | PubMed 논문 K221476 | 자체 임상 (저널 링크 없음) |
| 가격 | 100만원대 (렌탈) | 100만원대 (렌탈) | £139.99 D2C | $119 D2C | **$179 D2C** |
| 페이지 톤 | 홈쇼핑 | 홈쇼핑 | medical-consumer | clinical-academic | **fitness-app** |

→ **kGoal = "의료기기 인증 0인데 LLM에 10번 mention" 사례** — AiEO 본실험에 결정적 데이터포인트
→ 가설 H5(인증 명시 → 추천 ↑)에 *반례*. F4·F5가 모두 none인데도 LLM 추천 발생
→ 해석 후보:
  1. LLM이 "Kickstarter 1세대 + IDEA Award + 영문 PR 풍부"를 권위 신호로 학습
  2. "fitness tracker for kegels" 톤이 LLM 답변 스타일과 잘 매칭 (의료 면책 회피)
  3. 2014~2015 출시 시점의 영문 미디어 보도(Engadget, Dezeen, Medical Daily 등) 누적량이 SEO·학습 데이터에 진입

## LLM 학습 데이터 진입 시사 (Phase B1 10 mention 해석)

- 영문 콘텐츠 풍부도: ★★★ (Kickstarter PR + 2014~2017 테크 미디어 보도 다수)
- Engadget·Dezeen·Medical Daily·BioSpace 등 메이저 영문 매체 다수 언급 — LLM 학습 코퍼스 진입 강함
- "Smart Kegel"이라는 카테고리 자체를 처음 정의한 brand → 카테고리 명사 검색 시 등장
- NAVER 40 검색은 매우 낮음 — 한국어 콘텐츠 거의 없음. 그럼에도 LLM이 영문 코퍼스 기반으로 한국어 답변에 spillover

## 한국 시장 진출 여부

- **공식 distributor 명시**: kgoal.co.kr (자사 Where-to-Buy 페이지 1차 출처)
- ⚠️ 그러나 실 도메인 fetch는 `ECONNREFUSED` — Phase B2 전 도메인 운영 상태 직접 재검증 필요
- 한국 식약처 등록 부재 → 한국 내 의료기기 클레임 불가 (단, kGoal 자체가 의료기기 아니므로 wellness 톤으로 판매 시 규제 회피 가능)
- 한국어 마케팅·NAVER 가시성 거의 없음. NAVER 40 검색은 영문 인지가 한국어로 흘러든 결과로 해석

## 미확정 / 다음 액션

- [ ] **kgoal.co.kr 도메인 운영 상태 재검증** (Wayne 직접 브라우저 확인 — 퓨런 furenhealth.com 패턴 재발 방지)
- [ ] 자사몰 raw HTML fetch (curl_cffi 또는 Playwright) — Product JSON-LD 실제 삽입 여부 확정
- [ ] CE Mark 보유 여부 (PelviCoach EU 판매 페이지 fetch)
- [ ] kGoal Boost (남성용) 가격 + Phase B1에서 mention된 10건 중 Boost vs Classic 분포
- [ ] "400명 6주 임상" 출처 추적 — 자체 데이터인지, 미발표 화이트페이퍼인지

## 참고 링크
- [kGoal Classic 자사몰](https://www.kgoal.com/products/kgoal-smart-kegel-exerciser)
- [Where to Buy (한국 distributor 출처)](https://www.kgoal.com/pages/where-to-buy)
- [Kickstarter 캠페인 (2014)](https://www.kickstarter.com/projects/892018590/kgoal-smart-kegel-trainer)
- [PR Newswire - kGoal Boost 출시](https://www.prnewswire.com/news-releases/minna-life-launches-kickstarter-campaign-to-bring-kgoal-boost-to-men-300172644.html)
- [BioSpace 보도](https://www.biospace.com/b-minna-life-b-release-smart-kegel-training-app-device-for-your-lady-parts)
- [Vitality Medical (US 의료유통 채널)](https://www.vitalitymedical.com/kgoal-kegel-exerciser.html)
