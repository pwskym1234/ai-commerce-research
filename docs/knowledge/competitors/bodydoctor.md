---
brand: 바디닥터 (Body Doctor) — 우리 측 anchor
brand_slug: bodydoctor
vertical: medical_device
last_updated: 2026-04-23
data_sources: [bodydoctor.co.kr 메인, gncosshop.com/product/list.html?cate_no=26, 서울신문 2024-12-26]
manufacturer: 제너럴네트 (GN)
official_urls:
  - https://bodydoctor.co.kr (자사 공식몰)
  - https://gncosshop.com (GN코스몰)
  - http://gnbodydoctor.co.kr (별도 도메인 — 현재 ECONNREFUSED)
distribution_channels: [bodydoctor.co.kr, gncosshop.com, 네이버 스마트스토어 gncosshop, GSshop]
mfds_grade: 3                      # 식약처 3등급 (조합 의료기기)
mfds_category: 비이식형 요실금 신경근 전기 자극 장치 + 저주파 의료용 조합 자극기
fda_grade: [1, 2]                  # FDA Class 1 + 2 모두 등록
spec_steps: 99                     # 99단계 저주파 자극
f1_html_format: unknown_likely_paragraph   # 메인 페이지 카피 텍스트 중심 추정. 제품 상세 fetch 후 확정
f2_jsonld: none                    # bodydoctor.co.kr 메인에 JSON-LD 미발견
f3_numeric: partial                # "99단계" 같은 수치는 있으나 메인 노출 약함
f4_cert_position: bottom_or_none   # ★ GN코스몰 카테고리 페이지에 인증 표기 없음 (EMS 허리벨트만 FDA 표기)
f5_cert_detail: none               # ★ 메인/카테고리 페이지에 등급/허가번호 명시 없음
f6_evidence: marketing_only        # 임상 데이터 인용 없음 (서울신문 기사 기준)
status: anchor_brand
priority: anchor
---

# 바디닥터 (Body Doctor) — 우리 측 anchor

## 핵심 사실 (검증 완료)
- **회사**: 제너럴네트(GN). 2001년 설립. 2016년 1000만불 수출의 탑. 2020년 수출 유공기업 국무총리 표창. 연 매출 500억원.
- **제품 라인업** (GN코스몰 바디닥터 카테고리, 12개):
  - 바디닥터 3종 세트 (요실금치료기 + 좌훈기 + 허리벨트) — **6,320,000원**
  - 바디닥터 요실금치료기 단독
  - 바디닥터 EMS 트레이닝 무선 허리벨트 — 720,000원~
  - 바디닥터 고주파 리페어 (별도 라인)
  - 액세서리(캐링백/물티슈/크림 등)
- **인증**:
  - 식약처 **3등급 조합 의료기기**: 비이식형 요실금 신경근 전기 자극 장치 + 저주파 의료용 조합 자극기
  - FDA **1등급 + 2등급** 모두 등록
  - **허가번호는 미확보** — 식약처 공공데이터 API([data.go.kr/data/15057456](https://www.data.go.kr/data/15057456/openapi.do))로 조회 예정
- **기술**: 99단계 저주파 자극, 자동 케겔운동 유도, EMS 방식

## ★ 페이지 진단 1차 결과 (Wayne 컨설팅 직결)

GN코스몰 바디닥터 카테고리(`gncosshop.com/product/list.html?cate_no=26`)와 메인 페이지(`bodydoctor.co.kr`)에서 다음을 확인:

| 항목 | 현재 상태 | F 등급 매칭 |
|------|----------|-----------|
| 인증 표기 | EMS 허리벨트에만 "미국 FDA등록" 명시. **요실금치료기 자체 카테고리/메인에 인증 표기 없음** | F4=하단/없음, F5=없음 |
| JSON-LD | 메인 페이지 미발견 | F2=none |
| 임상 인용 | 서울신문 기사에도 임상 데이터 인용 없음 | F6=마케팅/후기 |
| 스펙 수치 | 99단계 같은 수치는 광고에 있으나 메인 노출 약함 | F3=partial |

→ **3등급 의료기기인데 그 사실을 페이지에서 강하게 안 알리고 있음**. AiEO 관점 잠재 손실 영역.
→ **컨설팅 Before/After 핵심 후보**: F4 상단 명시 + F5 등급+허가번호 표기 추가 + F6 임상 데이터 인용 추가 시 추천율 변화 측정.

## 미확정 / 다음 액션
- [ ] 식약처 허가번호 — 공공데이터 API로 조회 (다음 task)
- [ ] 요실금치료기 단독 가격 — `gncosshop.com/product/detail.html?product_no=190` 등 직접 fetch
- [ ] 자사 공식몰 bodydoctor.co.kr의 요실금치료기 단독 상세 페이지 fetch (정확한 F1 HTML 포맷 확정)
- [ ] gnbodydoctor.co.kr 도메인 운영 상태 확인 (현재 ECONNREFUSED)
- [ ] 마스터 §2.2 정정 PR ✅ 완료
- [ ] 임상 데이터가 실제로 존재하는지 GN 측 확인 (있다면 페이지 추가 가능)

## 참고 링크
- [서울신문 — 바디닥터 요실금치료기 (2024-12-26)](https://www.seoul.co.kr/news/economy/business-news/2024/12/26/20241226500020)
- [GN코스몰 바디닥터 카테고리](https://gncosshop.com/product/list.html?cate_no=26)
- [공공데이터포털 의료기기 품목허가 API](https://www.data.go.kr/data/15057456/openapi.do)
