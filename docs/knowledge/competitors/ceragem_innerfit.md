---
brand: 세라젬 이너핏 (CERAGEM INNERFIT Medi-TECH)
brand_slug: ceragem_innerfit
vertical: medical_device
last_updated: 2026-04-30
data_sources:
  - https://www.ceragemmall.co.kr/goods/goods_view.php?goodsNo=1000001039
  - https://www.ceragem.co.kr/aboutus/history.asp
  - https://m.edaily.co.kr/News/Read?newsId=01794166638856776&mediaCodeNo=257
  - https://m.ekn.kr/view.php?key=20240416028186490
  - https://www.youtube.com/watch?v=hp3EtnF96Uo
manufacturer: ㈜세라젬 (CERAGEM Co., Ltd.)
representative: 이경수
hq_address: 서울특별시 강남구 테헤란로 231 (코퍼레이트) / 충남 천안시 서북구 성거읍 정자1길 10 (공장)
official_urls:
  corporate: https://www.ceragem.co.kr
  shopping_mall: https://www.ceragemmall.co.kr
  product_page: https://www.ceragemmall.co.kr/goods/goods_view.php?goodsNo=1000001039
distribution_channels: [ceragemmall.co.kr, 세라젬 렌탈, 롯데홈쇼핑, G마켓 미니샵]
mfds_grade: "검증 필요"
mfds_license_number: "검증 필요"
mfds_purpose: "요실금 치료 + 근육통 완화 (2가지 사용목적, 보도 명시)"
launch_date: 2024-04-16
price_lump_sum: 990000
price_msrp: 1600000
f1_html_format: BULLET_dominant
f2_jsonld: none
f3_numeric: explicit_partial
f4_cert_position: bottom
f5_cert_detail: partial
f6_evidence: marketing_only
status: confirmed_high_priority
priority: 필수
---

# 세라젬 이너핏 (INNERFIT Medi-TECH)

## 핵심 사실 (검증 완료)

- **법인**: ㈜세라젬 — 안마의자 본업 매출 4,400억대 대기업, 코퍼레이트 본사 강남구 테헤란로
- **제품**: "요실금 치료 의료기기 이너핏 메디테크" — 2024년 4월 16일 출시
- **카테고리**: 식약처 허가 의료기기 (요실금 치료 + 근육통 완화 2가지 사용목적)
- **기술**: 저주파 자극 자동 케겔 트레이닝 + 최대 42℃ 온열 + 진동. 자체 "세라펄스 엔진" (바이탈/타이트닝/릴렉스 펄스) 브랜딩
- **공식 URL** (1차 fetch 검증): `ceragem.co.kr` (코퍼레이트) / `ceragemmall.co.kr` (쇼핑몰)
- **NAVER 검색**: 세라젬 브랜드 159,152 (대기업 인지도 — 단 이는 안마의자 본업 포함)

## ★ Wayne 검증 룰 이슈 — 허가번호 매칭

이전 `_medical_device_oem_pool.md`에 기록된 *제허 23-785 호 (2023-07-17 등록)* 가 이 INNERFIT 제품과 매칭되는지 **현재 1차 출처로 확인 안 됨**. 출시일(2024-04-16) vs 허가일(2023-07-17) 시간차로 별도 제품 또는 사전 허가 가능성. **udiportal.mfds.go.kr 또는 emed.mfds.go.kr 직접 조회 필요**.

## 페이지 진단 (자사몰 제품 페이지 fetch)

| 요인 | 실측 | 비고 |
|------|------|------|
| F1 HTML 포맷 | BULLET 우세 (~60%) + PARAGRAPH(~30%) + TABLE(~10%) | 텍스트 빈약, 이미지 중심 |
| F2 JSON-LD | **none** | Product/MedicalDevice schema 미적용 |
| F3 수치 구체성 | explicit_partial | 가격·출시일·유병율 통계만 명시. 효능·임상 수치 0 |
| F4 인증 위치 | **bottom** | KC + CCM + ISMS-P 페이지 하단. **식약처 인증 표기 자체가 페이지에 없음** |
| F5 인증 상세 | **partial** | KC 인증번호만 (R-R-poc-PoT-nR232). 식약처 등급·허가번호 미명시 |
| F6 근거 | marketing_only | 임상·논문·후기 0건. 자체 브랜딩 펄스명 위주 |

텍스트 길이: ~15,000자 (HTML 포함 ~50,000자) / 이미지 ~15-20장

## 가격·채널

- 자사몰 판매가 **990,000원** (정가 1,600,000원, 할인 38%)
- 자사 렌탈 채널 보유 (월 단가 미공개)
- 롯데홈쇼핑 특별기획전 노출 확인

## 본실험·컨설팅 함의

- **직접 경쟁 우선순위 1순위 추가** — 대기업 인지도 + 의료기기 카테고리 정합 + 같은 효능. 현재 `_medical_device_oem_pool.md`에만 1줄 있던 것을 자체 페이지로 격상.
- **AiEO 가설 H5 (인증 명시 → 추천 ↑)**: 세라젬조차 의료기기 등급·허가번호를 페이지에 명시 안 함 → easyk·furun과 동일한 한국 의료기기 시장 보편 약점
- **컨설팅 비교표 후보**: 세라젬을 코웨이 테라솔보다 우선. NAVER 검색량 159k 대 코웨이 테라솔 673 → 시장 인지도 격차 absolute

## 미확정 / 다음 액션

- [ ] 식약처 udiportal에서 "이너핏" / "INNERFIT" / "세라젬 요실금" 직접 조회 → 정확한 허가번호·등급 확정
- [ ] 의료기기 등급 (2등급 추정 vs 3등급 — 바디닥터/이지케이는 3등급)
- [ ] 렌탈 월 단가
- [ ] FDA / CE / GMP 보유 여부 (세라젬 마스터 V9 안마의자는 FDA 보유, INNERFIT은 별도 확인 필요)
- [ ] Phase B2 본 크롤링 시 curl_cffi 또는 Playwright로 raw HTML 재 fetch (JSON-LD 더 깊은 검증)

## 참고 링크

- [세라젬 코퍼레이트 — 회사 연혁](https://www.ceragem.co.kr/aboutus/history.asp)
- [세라젬몰 INNERFIT 제품 페이지](https://www.ceragemmall.co.kr/goods/goods_view.php?goodsNo=1000001039)
- [이데일리 — 세라젬 이너핏 메디테크 출시 (2024-04-16)](https://m.edaily.co.kr/News/Read?newsId=01794166638856776&mediaCodeNo=257)
- [에너지경제 — 세라젬 이너핏 보도](https://m.ekn.kr/view.php?key=20240416028186490)
- [공식 제품 영상 (YouTube)](https://www.youtube.com/watch?v=hp3EtnF96Uo)
