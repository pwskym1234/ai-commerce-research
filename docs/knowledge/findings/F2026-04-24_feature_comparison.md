---
date: 2026-04-24
title: Playwright 크롤링 + 11+ 피처 추출 — 바디닥터·프로폴린스 모두 경쟁사 대비 취약
related_findings: [F2026-04-23_empty_product_pages, F2026-04-24_mfds_oem_pool]
contradicts: []
supports: [H1, H2, H4, H5, H6, H7, H8]
vertical: both
phase: discovery
author: Claude
sources_summary: data/processed/features.jsonl (15 rows)
---

# 버티컬별 경쟁사 vs 우리 측 피처 비교

## 1. 데이터 수집 현황

Playwright JS 렌더링 크롤러로 양 버티컬 수집.

| vertical | brand | channel | text_length | jsonld | cert | clinical | explicit_num | price_krw |
|---------|-------|---------|------------:|--------|-----:|---------:|-------------:|----------:|
| medical_device | **bodydoctor** | gncosshop (4 SKU) | 2,500~2,700 | Product | 5 | 0 | **0** | 20,000* |
| medical_device | easyk | coreatech | **10,149** | Product | 11 | 0 | **4** | 27,900 |
| medical_device | ceragem | self_mall | 1,429 | - | 6 | 0 | 0 | - |
| medical_device | furenhealth | self_mall (차단) | 37 | - | 0 | 0 | 0 | - |
| gargle | **propolinse** | self_mall | 2,734 | **-** | 7 | 2 | 51 | 20,000 |
| gargle | listerine | self_mall (차단) | ~230 | - | 0 | 0 | 0 | - |
| gargle | garglin | dapharm + dmall | 3,466+15,303 | Product | 8 | 2 | 100 | 2,300 |
| gargle | perio | lghnh | 2,638 | - | 1 | 1 | 4 | - |
| gargle | 2080 | ssg | **66,981** | Product | 1 | 0 | **243** | 3,540 |

*가격 20,000원은 배송비 기준 쿠폰 표기 — 단독가 별도(280만원)

## 2. ★ 의료기기 버티컬 핵심 발견

**이지케이(coreatech)가 바디닥터 대비 AiEO 측면 앞섬**:
- text_length: 이지케이 10,149 vs 바디닥터 2,500~2,700 (**4배**)
- cert keyword: 이지케이 11 vs 바디닥터 5 (**2배**)
- explicit number: 이지케이 **4개** vs 바디닥터 **0개**
- JSON-LD: 둘 다 Product 스키마 (동률)

→ **바디닥터는 같은 3등급 의료기기 경쟁자(이지케이)에게도 AiEO 최적화로 뒤짐**.
→ H8 (Y1=파싱 ≠ Y2=추천) 검정에 강한 사전 신호.
→ 컨설팅 Before/After의 구체 목표: **바디닥터 text_length를 10,000+, explicit number 10+로 끌어올리기**.

세라젬·퓨런은 bot 차단으로 불완전 수집. 다음 턴에 stealth 옵션으로 재시도.

## 3. ★ 가글 버티컬 핵심 발견

**프로폴린스 자사몰이 경쟁사 대비 AiEO 취약**:
- JSON-LD: 프로폴린스 **없음**, 가그린·2080은 **Product 스키마 有** ← 가장 큰 격차
- cert keyword: 프로폴린스 7 (가그린 dmall 8, 2080 SSG 1)
- explicit number: 프로폴린스 51 (2080 SSG 243, 가그린 dmall 100)
- text_length: 프로폴린스 2,734 (가그린 dmall 15,303, 2080 SSG 66,981)

→ **프로폴린스는 자사몰(propolinse.co.kr)에 JSON-LD 추가만 해도 AiEO 큰 리프트 가능**.
→ 텍스트 밀도도 경쟁사 대비 낮음 — 상품 상세 콘텐츠 강화 필요.

특이: 가그린 제조사 페이지(dapharm.com)는 clinical_keyword=20 — "12시간 지속" 같은 근거 표현 반복. 자사 쇼핑몰(dmall.co.kr)에는 Product 스키마 + text 15KB로 이커머스 최적화.

## 4. 한계 및 정교화 필요 사항

현재 피처 추출의 정확도 한계:
1. **cert_keyword_count**: "인증" 같은 일반 단어도 카운트. 정확도 낮음. "식약처 3등급", "제허 XX-XXX호" 같은 구체 패턴 regex 필요
2. **clinical_keyword**: "임상" 단어만 잡음. 실제 RCT 인용 vs 일반 마케팅 표현 구분 안 됨
3. **explicit_number_count**: 단위 패턴 한정 (Hz, 단계, mm 등). "99% 살균" 같은 % 조합 일부 누락 가능
4. **bot 차단**: listerine·furenhealth는 Playwright stealth 미적용으로 차단. 다음 턴 강화

→ Wayne의 외부 사례(제품 단위 AI 노출 최적화 회사들) 정리 후, 그 내용을 반영해 F 요인 정밀화 + feature 추출 로직 고도화 예정.

## 5. 본실험 가상 페이지 설계에 미치는 영향

이 비교 데이터가 F1~F6 수준 정의의 **baseline**이 됨:

| F 요인 | "없음" baseline (우리 현 상태) | "최적" 상한 (경쟁사 최고치) |
|--------|---------------------------|----------------------------|
| F1 HTML 포맷 | 이미지 중심, 텍스트 2.5KB | 이커머스 수준 60KB |
| F2 JSON-LD | 없음 (프로폴린스) / Product (바디닥터) | MedicalDevice 풀 스키마 |
| F3 수치 구체성 | 0 (바디닥터 explicit) | 243 (2080 SSG) |
| F5 인증 상세 | keyword 5 (general "의료기기") | 실제 허가번호 풀 텍스트 |
| F6 근거 | clinical 0 | RCT 수치 인용 |

→ 산공통 가상 페이지 제작 시 "F=없음"은 현 바디닥터와 동일, "F=풀"은 실측 경쟁사 최고치 기준으로 설정.

## 6. 다음 액션

1. **stealth 옵션 추가** — listerine, furenhealth 재크롤링
2. **피처 추출 로직 정교화** — Wayne 외부 사례 반영 후
3. **competitors/ceragem.md, furenhealth.md** 신설 (OEM 풀 단순 리스트를 실제 경쟁 분석으로 격상)
4. 수집된 rendered HTML의 JSON-LD 상세 필드 파싱 (현재 단순 타입만 카운트)
