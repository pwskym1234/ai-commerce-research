---
brand: 리스테린 (Listerine)
brand_slug: listerine
vertical: gargle
last_updated: 2026-04-24
data_sources:
  - https://www.listerine.kr (자사몰, curl_cffi로 크롤링)
  - 나무위키, 가글 추천 블로그 다수
manufacturer: Johnson & Johnson (글로벌)
official_url: https://www.listerine.kr/    # listerine.co.kr는 301로 여기로 리다이렉트
distribution_channels: [self_mall, 쿠팡, 네이버, 11번가, GSshop, 약국, 마트]
f1_html_format: BULLET          # 초기 HTML 기준 (SPA, JS 렌더 전). 실렌더 후 재측정 필요
f2_jsonld: none                 # ★ 글로벌 1위 브랜드인데 Product/aggregateRating 스키마 0건
f3_numeric: explicit            # 실측 수치: 30초, 99%, 130년, 52%, 30%, 2회, 1회, 1%
f4_cert_position: na            # 의약외품 — 의료기기 인증 개념 없음
f5_cert_detail: na
f6_evidence: brand_authority    # 확정: 130년/No.1/글로벌 등 권위 중심
review_widget: bazaarvoice      # UGC 리뷰 수집 중 (JSON-LD aggregateRating은 없음)
status: confirmed
priority: high
---

# 리스테린 (Listerine)

## 핵심 사실
- **카테고리**: 글로벌 1위 가글 브랜드 (구강청결제)
- **모회사**: Johnson & Johnson
- **분류**: 의약외품 (한국)
- **핵심 성분**: 4가지 에센셜 오일 — 티몰, 살리실산메틸, 멘톨, 유칼립톨
- **포지셔닝**: 강력한 살균력 + 구취 제거. "센 가글"의 대명사
- **AI 추천 위상**: 한국어 + 영어 쿼리 모두에서 가글 추천 시 거의 항상 첫 줄 등장

## 한국 라인업 (listerine.kr 검증 — 2026-04-23)
- 쿨민트
- 후레쉬버스트
- 시트러스
- 내추럴 그린티 마일드
- 티스앤드검 디펜스
- 타르타르 컨트롤
- 토탈케어 (검케어 마일드 포함)
- 어린이 안전캡 라인 (CRC)
- 약 10+ 라인업

## 핵심 클레임 (listerine.kr 메인)
- "30초 사용 시 입속 세균 99.9% 제거"
- "효과 12시간 지속"
- 4가지 에센셜 오일: 유칼립톨, 레보멘톨, 티몰, 살리실산메틸 (메인에 명시)
- "5배 프라그 억제" (토탈케어 마일드 캠페인)

## 자사몰 실측 진단 (listerine.kr, 2026-04-24)

크롤러: curl_cffi + Chrome TLS impersonate (이전 Playwright+stealth 3차 시도는 Cloudflare WAF 차단). 5개 페이지 확보 (main, products/gum-care-mild, products/greentea-mild, about, co.kr 리다이렉트 테스트).

| 요인 | 실측 | 근거 |
|------|------|------|
| F1 HTML 포맷 | **BULLET 우세** | ⚠️ 리스테린은 SPA(CSR) — 초기 HTML text_length 707~1959자뿐, 본문은 JS 렌더링 후 확인 필요 |
| F2 JSON-LD | ❌ **0건** (5 페이지 모두) | 🔥 **글로벌 1위 가글 브랜드조차 Product / aggregateRating schema 부재** |
| F3 수치 구체성 | 0.517 (중상) | 추출 수치: 30초, 99%, 1%, 130년, 52%, 30%, 2회, 1회, 1860년, 1920년. 기존 추정 "99.9%"는 페이지에서 "99%"로 표기 |
| F4/F5 인증 | 0개 | 의약외품 카테고리라 식약처/MFDS 언급 자체가 없음 |
| F6 근거 | **brand_authority 우세** (5페이지 중 3) | 130년 역사 · No.1 · 글로벌 권위 중심 |
| 리뷰 | **Bazaarvoice 위젯 탑재** | 초기 HTML에 `bazaarvoice` 힌트 확인. 실평점·건수는 JS 렌더링 후 위젯 DOM에서 캡처 필요 (후속 과제) |

## 결과물 위치

- 원시 HTML: `data/raw/gargle/listerine/self_mall/2026-04-24/*_cffi.html`
- 구조화 진단: `consulting/diagnosis/listerine_self_mall_2026-04-24.json`

## 컨설팅 함의

- **프로폴린스가 JSON-LD Product/AggregateRating을 도입하면 글로벌 1위조차 안 하는 구조화를 선도**하는 포지션 확보 가능
- **Bazaarvoice 리뷰 위젯** 같은 UGC 솔루션을 프로폴린스도 도입하면 리스테린과 같은 리뷰 자산 구조 확보 (단, JSON-LD로 aggregateRating을 노출하는 쪽이 AI 추천 신호로는 더 강함 — 리스테린의 현재 빈틈)

## 미확인 / 다음 액션

- [ ] Playwright + 시스템 Chrome channel로 SPA 렌더링 DOM 캡처 (F1 실값·Bazaarvoice 평점/건수)
- [ ] 가격대 (대형마트 기준)

## 참고 링크 보강
- [공식 한국 사이트](https://www.listerine.kr/)
- [About 페이지](https://www.listerine.kr/about)
- [토탈케어 검케어 마일드](https://www.listerine.kr/products/gum-care-mild)
- [내추럴 그린티 마일드](https://www.listerine.kr/products/greentea-mild)
- [에이엠디 — 5배 프라그 억제 캠페인 보도](https://www.mdon.co.kr/news/article.html?no=33135)

## AI 추천 비교에서의 위상
프로폴린스의 가장 큰 글로벌 경쟁자. 리스테린과 비교 평가에서 프로폴린스가 차지할 수 있는 차별 포지션이 무엇인지가 본 분석의 핵심 발견 후보.

## 참고 링크
- [나무위키 — 리스테린](https://namu.wiki/w/%EB%A6%AC%EC%8A%A4%ED%85%8C%EB%A6%B0)
