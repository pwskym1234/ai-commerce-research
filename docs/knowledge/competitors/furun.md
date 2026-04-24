---
brand: 퓨런헬스케어 (Furun Healthcare)
brand_slug: furun
vertical: medical_device
last_updated: 2026-04-24
data_sources:
  - http://furun.kr/ (자사몰, curl_cffi로 크롤링)
  - 식약처 제허 21-492, 21-920 (_medical_device_oem_pool.md)
manufacturer: (주)퓨런헬스케어
official_url: http://furun.kr/
# 주의: 이전에 knowledge base에 기록됐던 furenhealth.com / www.furenhealth.com은
# DNS 해결 불가 또는 testtesttt.top으로 탈취 리다이렉트. Wayne이 furun.kr로 정정 (2026-04-24)
distribution_channels: [inquiry_only]  # 직접 판매 아님, Purchase Inquiry 문의 채널
f1_html_format: BULLET
f2_jsonld: none
f3_numeric: machine_spec_only   # 25kg/440mm/50Hz 류만 있음, 효능/임상 수치 0
f4_cert_position: bottom        # 0.807 비율, 페이지 하단
f5_cert_detail: partial_foreign # CE, GMP만 노출 — 식약처/제허/등급은 자사 페이지에 없음
f6_evidence: none               # 임상/논문/후기 모두 부재
status: confirmed
priority: medium                # 본실험 주력 N=6에서는 빠질 수 있음 (소비자 판매 X)
---

# 퓨런헬스케어 (Furun Healthcare)

## 정정 기록 (2026-04-24)

이전 knowledge base에 기록됐던 공식 URL 후보(`furenhealth.com`, `www.furenhealth.com`)는 모두 부정확했음.
- `furenhealth.com`: DNS 해결 불가
- `www.furenhealth.com`: `testtesttt.top`으로 redirect (도메인 만료/탈취 추정)
- **정정**: Wayne 확인 → `http://furun.kr/` (HTTPS는 자체 서명 인증서 경고, HTTP만 정상 동작)

## 핵심 사실

- **법인**: (주)퓨런헬스케어 — 의료기기 제조업체
- **식약처 등록**: 제허 21-492 (2021-06-21) + 제허 21-920 (2021-11-18) — 비이식형요실금신경근전기자극장치 2건
- **제품 라인업**:
  - **HNJ-350** (Urinary Incontinence — Pelvic Floor Muscle Training Device)
  - **HNJ-1000** (요실금 치료기)
  - **HNJ-7000** (Medical Device 분류)
  - IM.GYM-3000 / IM.GYM-7000 (Smart Home Gym — 비의료기기)
- **자사몰 성격**: **글로벌 B2B 제조사 전시 홈페이지** (소비자 직접 판매 X)

## 자사몰 실측 진단 (furun.kr, 2026-04-24)

크롤러: curl_cffi + Chrome impersonate. 8개 페이지 확보 (main, about/company, about/certificates, products/, HNJ-350, HNJ-1000, HNJ-7000, cs/purchase-inquiry).

| 요인 | 실측 | 근거 |
|------|------|------|
| 언어 지원 | EN(기본) / JA / CN | `lang="en-US"` + hreflang, **한국어 서브도메인 없음** |
| 판매 기능 | 없음 | 모든 구매 플로우가 "Purchase Inquiry" 폼으로 귀결 |
| F1 HTML 포맷 | **BULLET** | 다수 페이지에서 `<ul>/<li>` 기반 스펙 나열 |
| F2 JSON-LD | ❌ **없음** | 8페이지 모두 `<script type="application/ld+json">` 0건 |
| F3 수치 구체성 | 0.375 (중하) | 추출 수치: 25kg, 440mm, 450mm, 720mm, 23kg, 20kg, 400mm, 49mm, 3kg, 50Hz, 60Hz, 680mm, 775mm, 150mm, 50kg — **기계 크기·전원 스펙뿐, 효능/임상 수치 0** |
| F4 인증 위치 | **bottom** (0.807) | 인증 관련 키워드가 본문 텍스트 80% 지점 이후 등장 |
| F5 인증 상세 | **CE×2 + GMP×1만** | 🔥 자사 제허 2건 보유하고도 페이지에 "식약처/제허/등급" 언급 전무 |
| F6 근거 | none 7 / brand_authority 1 | 임상·논문·사용자 후기 완전 부재 |
| 리뷰 | 위젯 없음 | Bazaarvoice/Yotpo 등 UGC 솔루션 0건 |

## 결과물 위치

- 원시 HTML: `data/raw/medical_device/furun/self_mall/2026-04-24/*.html`
- 구조화 진단: `consulting/diagnosis/furun_self_mall_2026-04-24.json`

## 본실험·컨설팅 함의

### 본실험 (산공통·데마)
- **주력 비교군 N=6에서는 빠질 수 있음**: 소비자가 자사몰을 통해 검색·구매할 일이 없어 AI 추천 답변에도 거의 등장하지 않을 것. 실제 쿼리("요실금치료기 추천") 결과에 `furun.kr`가 노출될 확률 ≈ 0.
- **H14 관찰 분석에는 가치**: "식약처 제허를 보유하고도 자사 페이지에서 이를 전혀 드러내지 않으면 AI는 해당 업체를 인증 기업으로 인식하지 않는다" — F4/F5의 강력한 EXPLORATORY 근거.

### 컨설팅
- **바디닥터 화이트라벨 가설의 간접 증거**: 한국 요실금치료기 OEM 제조사들은 기업 홈페이지에서 한국 소비자 대응을 거의 하지 않음. 바디닥터처럼 유통사 브랜드가 소비자 대응을 전담하는 구조가 보편.
- **Before/After 비교 대상으로는 부적절**: 비교 포인트 자체가 너무 벌어져 컨설팅 사례로는 약함.

## 미확인 / 다음 액션

- [ ] 식약처 DB에 등록된 제허 21-492, 21-920의 정식 모델명이 HNJ-350/1000/7000 중 어느 것과 매핑되는지 확인 (현재 자사 사이트에는 제허 번호 표기 없음)
- [ ] 쿠팡/11번가에 "퓨런헬스케어" 또는 "HNJ-350" 같은 제품명으로 판매 중인 상품이 있는지 Wayne 확인
- [ ] 본실험 경쟁군 N=6에서 퓨런을 빼고 대체할 후보 결정 (쉬엔비 / 리모트솔루션 / 비엠씨 / 유진플러스 중)

## 참고 링크

- [공식 홈페이지](http://furun.kr/)
- [HNJ-350 제품 페이지](http://furun.kr/products/pelvic-floor-muscle-training-device/hnj-350/)
- [식약처 DB — 비이식형요실금신경근전기자극장치 풀](_medical_device_oem_pool.md)
