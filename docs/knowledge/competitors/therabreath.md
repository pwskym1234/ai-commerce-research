---
brand: 테라브레스 (TheraBreath)
brand_slug: therabreath
vertical: gargle
last_updated: 2026-04-30
data_sources:
  - https://www.therabreath.com (글로벌 본사, Church & Dwight)
  - https://www.therabreath.co.kr (한국 공식, 온누리H&C 운영, ECONNREFUSED 발생)
  - 나무위키, 위키트리, 세계일보, 브런치
  - https://en.wikipedia.org/wiki/TheraBreath_(brand)
manufacturer: Church & Dwight Co., Inc. (미국, 2021년 인수). 한국판은 LSC 위탁 제조
official_url: https://www.therabreath.com/
korea_official_url: https://www.therabreath.co.kr/
korea_distributor: 온누리H&C
distribution_channels: [therabreath.co.kr, 쿠팡, 올리브영, 코스트코, iHerb, 마켓컬리, 29CM, pilly]
f1_html_format: BULLET           # 글로벌 본사 페이지 — 카드형 grid + 불릿
f2_jsonld: unknown               # 메인 페이지에서는 미발견 (제품 페이지는 미확인 — 후속 검증)
f3_numeric: explicit             # 99.9% germs, 24 hours, 6-in-1, $5.99~$15.97 명시
f4_cert_position: na             # 한국판은 의약외품, 미국판은 FDA OTC 카테고리
f5_cert_detail: cert_diverse     # Vegan, Gluten-Free, Kosher, Halal, BPA-Free, Not Animal Tested. 그러나 ADA Seal 없음
f6_evidence: founder_authority   # Dr. Harold Katz(California Breath Clinics) 권위 + GMA/Fox/NBC 노출
korea_mfds_status: 의약외품 (한국판만, 성분 다름)
formulation_difference: 해외판 OXYD-8 (특허 NaClO2) vs 한국판 CPC + NaF (가그린 유사)
status: confirmed
priority: high
---

# 테라브레스 (TheraBreath)

## 핵심 사실

- **카테고리**: 미국 발 구취·잇몸 케어 가글 — "미국 1위 성장 가글" (2026.02 보도, Church & Dwight 발표)
- **창업자**: Dr. Harold Katz (California Breath Clinics, 30+년 전 창업)
- **모회사**: Church & Dwight Co., Inc. (2021년 인수, 콘돔 Trojan·Arm & Hammer 같은 OTC 포트폴리오)
- **포지셔닝**: "치과의사가 만든 임상 가글" + "구취 원인 박테리아 정밀 타겟"
- **핵심 차별 성분**: OXYD-8 (Dr. Katz 특허, 아염소산나트륨 NaClO2 개량). 그러나 한국에서는 식약처 의약외품 허가 못 받음 — 한국판은 다른 처방
- **글로벌 가격대**: $5.99~$15.97 (자사몰 기준)
- **AI 추천 위상**: 영어권에서 "best mouthwash for bad breath" 쿼리 시 거의 항상 첫 줄. Listerine 다음으로 자주 언급되는 글로벌 가글

## 한국 진출 구조 (검증 완료 2026-04-30)

| 항목 | 내용 |
|------|------|
| 공식 한국 사이트 | [therabreath.co.kr](https://www.therabreath.co.kr/) (개별 fetch는 ECONNREFUSED — 차단/서버 이슈, 추후 curl_cffi 재시도) |
| 한국 유통사 | **온누리H&C** (테라브레스 한국 공식 유통) |
| 한국판 제조 | **LSC** (Onnuri H&C 위탁 제조) — 즉, 한국판은 미국에서 수입 X, 한국에서 별도 생산 |
| 식약처 의약외품 | **승인 받음 (한국판만)**. 단 OXYD-8은 허가 X → CPC + NaF로 대체 처방 |
| 해외 직구판 vs 한국판 차이 | ⚠️ **주성분이 완전히 다름**. 해외판 = OXYD-8, 한국판 = 가그린과 유사한 CPC/NaF. 소비자 혼란 보도 다수 (위키트리 2건) |
| 가격 | 쿠팡 473ml 약 11,900원, 1L+473ml 묶음 약 32,290원. **경쟁사 대비 2~3배 고가** (나무위키) |
| 오프라인 채널 | 올리브영, 코스트코, 마켓컬리, 29CM |
| 한국어 페이지 | ✅ 존재 (therabreath.co.kr) |

**판별 팁**: 라벨에 한국어 표기 = 한국판(OXYD-8 미함유). 영어만 = 해외 직구판(OXYD-8 함유)

## 글로벌 본사 페이지 진단 (therabreath.com, 2026-04-30 fetch)

| 요인 | 실측 | 근거 |
|------|------|------|
| F1 HTML 포맷 | **BULLET 우세** | 메인 nav + 제품 grid + 불릿형 benefit 리스트. TABLE 없음 |
| F2 JSON-LD | ❌ **0건** (메인 기준) | 글로벌 1위 성장 브랜드도 메인 페이지 schema 0. 제품 상세 페이지는 후속 확인 필요 (`/oral-rinse` URL은 404) |
| F3 수치 구체성 | **explicit (높음)** | "kills 99.9% of germs", "24 hour gumline plaque", "6-in-1 Benefits", "24/7 sensitivity relief", $5.99~$15.97 |
| F4 인증 위치 | **다수 노출** (메인 + 푸터) | Vegan, Gluten-Free, Kosher, Halal, BPA-Free, Not Animal Tested |
| F5 인증 상세 | **다양하지만 ADA Seal 없음** | American Vegetarian Association vegan cert. Halal/Kosher cert. 그러나 ADA Seal of Acceptance는 페이지에서 미확인 |
| F6 근거 | **founder_authority** | Dr. Katz "breakthrough research into the causes of bad breath" 중심. GMA·Fox·NBC 미디어 노출. 구체 임상 인용은 메인엔 부재 |
| 추가 신호 | "100% Money-Back Guarantee" + "Shop with Confidence" 반복 노출 |

## 같은 효능 영역

프로폴린스 anchor와 직접 경쟁: **구취 (bad breath)**, **잇몸 케어 (healthy gums)**, **충치 예방** (한국판 NaF 함유 시), **치주염 예방**. 단, 프로폴린스가 차별화 포인트로 삼는 "단백질 흡착 시각화"는 테라브레스에 없음.

## 영문 콘텐츠 풍부도

✅ **매우 풍부**. 자사몰 카테고리만 6개(Toothpaste, Oral Rinses, Lozenges & Gum, Travel, Kids), 라인업 20+. About 페이지에 Dr. Katz 스토리, Bad Breath 원인 가이드 등 educational content 적층. 영문 LLM이 "TheraBreath" 호출할 컨텍스트가 풍부함.

## AI 추천 비교에서의 위상

- **영어 쿼리**: 리스테린 + 테라브레스 양강 구도. 특히 "halitosis", "chronic bad breath", "dentist recommended"같은 specific intent 쿼리에서 테라브레스 우위
- **한국어 쿼리**: 가그린·리스테린·페리오에 비해 호출 빈도 떨어질 가능성 (한국판 인지도 낮음, 가격 2~3배). 그러나 "치과의사 추천 가글" 같은 권위 쿼리에선 호출 가능
- **프로폴린스 대비 위협 포인트**: 영문 컨텐츠 + Dr. Katz 권위 + Church & Dwight backing → AI에게 "trustworthy oral health authority" 신호 강함

## 주의 — Wayne 사고 재발 방지

- 한국판/해외판 구분 명확히. 컨설팅 시 "테라브레스 = 일관된 처방"으로 단정 금지
- 식약처 의약외품 허가는 **한국판 한정** (해외 직구판은 의약외품 분류 자체가 적용 안 됨)
- ADA Seal **없음** (있을 것 같지만 실제로 미국 본사 페이지에서 미확인). 인증 신호로 ADA를 단정 금지

## 참고 링크

- [TheraBreath 글로벌 본사](https://www.therabreath.com/)
- [TheraBreath Korea 공식](https://www.therabreath.co.kr/)
- [Wikipedia — TheraBreath brand](https://en.wikipedia.org/wiki/TheraBreath_(brand))
- [위키트리 — 한국산/해외 직구 성분 다름 보도](https://www.wikitree.co.kr/articles/535879)
- [세계일보 — 온누리H&C 한국 완판 보도](https://www.segye.com/newsView/20200521519253)
- [나무위키 — 테라브레스](https://namu.wiki/w/%ED%85%8C%EB%9D%BC%EB%B8%8C%EB%A0%88%EC%8A%A4)
- [Church & Dwight 인수 보도](https://www.mediapost.com/publications/article/369001/church-dwight-will-add-therabreath-to-oral-care.html)
- [Target Eucalyptus Mint 신제품 (2026.02)](https://www.prnewswire.com/news-releases/therabreath-unveils-target-exclusive-eucalyptus-mint-oral-rinse-blending-premium-botanicals-with-the-brands-iconic-freshness-302697368.html)

## 미확인 / 다음 액션

- [ ] therabreath.co.kr 한국판 페이지 curl_cffi 재시도 (현재 ECONNREFUSED) — F1~F6 한국판 실측
- [ ] therabreath.com `/products/...` 제품 상세 페이지 fetch (Product JSON-LD, AggregateRating 위젯 확인)
- [ ] ADA Seal of Acceptance 진짜로 없는지 페이지 search (단정 회피용)
- [ ] 한국 시장 점유율 자료 (한국갤럽 의약외품 가글 인지도 등)
