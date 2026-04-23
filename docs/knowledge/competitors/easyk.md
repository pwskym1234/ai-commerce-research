---
brand: 이지케이 (EASY-K)
brand_slug: easyk
vertical: medical_device
last_updated: 2026-04-23
data_sources:
  - https://easyk.kr (자사 공식몰)
  - https://coreatech-rental.com (유통/렌탈)
  - http://www.amedic.co.kr (제조사 알파메딕)
  - 11번가/SK스토아 상품 페이지
  - 의학신문/k-health 보도
manufacturer: ㈜알파메딕 (Alphamedic)
distributor: ㈜코리아테크 (Coreatech) — 렌탈/판매
official_urls:
  brand: https://easyk.kr
  rental: https://coreatech-rental.com/product/요실금치료-의료기기-easy-k/415/
  manufacturer: http://www.amedic.co.kr
distribution_channels:
  - easyk.kr (자사몰)
  - coreatech-rental.com (렌탈)
  - 11번가
  - SK스토아
  - 롯데홈쇼핑
mfds_grade: 3                          # ★ 바디닥터와 같은 등급
mfds_category: 비이식형 요실금 신경근 전기자극장치
mfds_license_number: 제허15-329호      # ★ 확정
gmp_certified: true
fda_grade: unknown                      # 미확인 — 글로벌 인증 여부 추가 조사 필요
spec_steps: 99                          # 99단계 강도 + 5단계 프로그램 (k-health 보도)
celebrity_endorsement: 김상중           # 11번가/SK스토아 광고
price_rental: 1088100                   # 월 27,900원 × 39개월
price_lump_sum_estimate: 1000000        # 추정 (홈쇼핑/11번가 일시불)
f1_html_format: unknown                 # 자사몰 fetch 추가 필요
f2_jsonld: unknown
f3_numeric: explicit                    # 99단계 + 5단계 + 월 27,900원 등 구체 수치
f4_cert_position: unknown               # 자사몰 직접 확인 필요
f5_cert_detail: unknown_likely_partial  # "식약처 GMP 적합 인증" 보도. 등급/허가번호 페이지 명시 여부는 직접 확인 필요
f6_evidence: user_reviews               # 홈쇼핑 매체 특성 + 김상중 등 마케팅 모델 중심 추정
status: confirmed_high_priority
priority: 필수
---

# 이지케이 (EASY-K) — 바디닥터의 가장 정면 경쟁자

## 핵심 사실 (검증 완료)

### 회사 구조
- **제조**: ㈜알파메딕 ([amedic.co.kr](http://www.amedic.co.kr))
- **유통/렌탈**: ㈜코리아테크 ([coreatech-rental.com](https://coreatech-rental.com))
- **브랜드 자사몰**: [easyk.kr](https://easyk.kr)

### 제품 라인업 (코리아테크 카탈로그 기준)
- **easy K** — 요실금치료 의료기기 (메인)
- **easy K7** — 후속/업그레이드 모델
- (참고) easy Claire (LED마스크), easy Hairfull (탈모), easy S (척추 매트), easy Clair Neck — 다른 카테고리

### ★ 인증 (확정)
- **식약처 3등급** 의료기기
- **품목명**: 비이식형 요실금 신경근 전기자극장치
- **허가번호**: **제허15-329호**
- **GMP 적합 인증**

### 스펙
- 99단계 강도 조절
- 5단계 자동 프로그램
- 자동 케겔운동 유도

### 가격
- 렌탈: 월 27,900원 × 39개월 = 1,088,100원
- 일시불: 100만원대 추정 (홈쇼핑/11번가 직접 확인 필요)

### 마케팅
- **김상중 광고** (11번가/SK스토아 페이지에 명시)
- 롯데홈쇼핑/SK스토아 라이브 마케팅
- "쉬운 케겔" 네이밍 (의학신문 네이밍 스토리 기사)

## ★★ 결정적 발견 — 바디닥터와 같은 식약처 3등급, 같은 카테고리

| 항목 | 바디닥터 | 이지케이 |
|------|---------|---------|
| 식약처 등급 | 3등급 | 3등급 |
| 품목 카테고리 | 비이식형 요실금 신경근 전기자극장치 (+저주파 의료용 조합 자극기) | 비이식형 요실금 신경근 전기자극장치 |
| 허가번호 | 미확인 (공공데이터 API로 조회 예정) | 제허15-329호 |
| 강도 단계 | 99단계 | 99단계 |
| 가격 | 추정 100만원~ | 100만원대 (렌탈) |
| 마케팅 모델 | 미확인 | 김상중 |

→ **"인증 등급" 자체로는 차별화 안 됨**. 두 브랜드 다 같은 3등급.
→ AiEO 본실험 가설 H5/H6/H7의 진짜 의미가 정밀해짐:
  - H5 ("인증 명시가 추천 ↑") = "**같은 3등급 의료기기 사이에서, 페이지에 등급+허가번호를 명시한 쪽이 추천 ↑인가?**"
  - 이게 진짜 의미. 아래 새 finding [F2026-04-23_same_grade_competition.md](../findings/F2026-04-23_same_grade_competition.md) 참조.

## 미확정 / 다음 액션
- [ ] easyk.kr 자사몰 직접 fetch (F1~F6 정밀 진단)
- [ ] coreatech-rental.com 제품 상세 페이지 fetch
- [ ] 일시불 가격 확정 (11번가/SK스토아)
- [ ] FDA 인증 여부 (글로벌 시장 진출했나)
- [ ] 알파메딕 자사 사이트(amedic.co.kr) 점검 — B2B 브랜딩 vs B2C 코리아테크 분리

## 참고 링크
- [easyk.kr 본사 페이지](https://easyk.kr/product/본사-이지케이-김상중의-요실금치료기/28/)
- [코리아테크 EASY-K 상품](https://coreatech-rental.com/product/요실금치료-의료기기-easy-k/415/)
- [알파메딕 제품소개](http://www.amedic.co.kr/?menu_code=101)
- [k-health 롯데홈쇼핑 런칭 보도](https://www.k-health.com/news/articleView.html?idxno=20757)
- [의학신문 네이밍 스토리](http://www.bosa.co.kr/news/articleView.html?idxno=2081378)
- [11번가 김상중 EASY-K](https://www.11st.co.kr/products/4000137215)
- [다나와 알파메딕 이지케이](https://prod.danawa.com/info/?pcode=5087873)
