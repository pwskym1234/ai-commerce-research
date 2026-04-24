---
name: 훌스 HOOL'S 음파방석
description: (주)하이리빙의 네트워크마케팅 공산품 케겔 방석. 네이버 스마트스토어 전용 브랜드명 + 공식 제조사몰 확보.
type: competitor
brand_id: hools
category: consumer_product
vertical: medical_device
mfds_registered: false
sku_representative: hools_sonic_300751
last_checked: 2026-04-24
---

# 훌스 HOOL'S 음파방석

## 포지셔닝

- **제조사**: (주)하이리빙 — 1996년 창립, 네트워크 마케팅 전문 생활유통 기업
- **브랜드명 "훌스(HOOL'S)"**: 네이버 스마트스토어 전용 작명. 공식 제조사몰에서는 "음파방석"으로만 표기.
- **식약처 미등록**: 의료기기 아님, 골반/케겔/진동 마사지기 공산품.

## 판매 채널 구조 (2026-04-24 확인)

| 채널 | URL | 접근성 | 상태 |
|------|-----|-------|------|
| 네이버 스마트스토어 | `smartstore.naver.com/hilivingmall/products/12549951735` | **로그인 벽** | 네이버가 성인/민감 카테고리로 분류 — 비로그인 접근 시 `nid.naver.com/nidlogin.login`로 강제 리다이렉트 (Playwright stealth / curl_cffi 모두 동일 결과) |
| 하이리빙 공식몰 | `www.hiliving.co.kr/goods/detail?code=300751` | ✅ 로그인 불요 | 62KB 정적 페이지 응답, 일반 Chrome UA 기반 `requests.get()`으로 접근 가능 |
| 11번가 / 쿠팡 / 지마켓 | — | 없음 | wowoo.co.kr 리뷰 확인: 네이버 스마트스토어 단일 채널 운영 |

## 가격

- 네이버 스마트스토어 게시가: **799,000원** (wowoo.co.kr 리뷰 기준)
- 하이리빙 공식몰 공개 페이지: `50,000원` 만 노출 (사은품 가격으로 추정, 본체 회원가 가려짐)
- → AI 추천용 가격 참조는 스마트스토어 게시가 799,000원 사용

## 크롤링 기록

- v3 (2026-04-24): `naver.me/5kPKhrYo` 단축 URL → 리다이렉트 전환 후 Sixthshop 4점 (컨텐츠 거의 없음)
- v4 (2026-04-24): smartstore long URL + Playwright networkidle → 60s timeout (AJAX 무한 폴링)
- v5 (2026-04-24): smartstore long URL + domcontentloaded → 22KB, **네이버 로그인 페이지** (Sixthshop 0점)
- v6 (2026-04-24): **하이리빙 공식몰 `goods/detail?code=300751`** → 62KB, **Sixthshop 31점** (A=0, B=6, C=10, D=15)

## AiEO 평가 기준점

- **페이지 품질 31/100**: 의료기기 경쟁사 평균(60~75) 대비 낮음, A(JSON-LD) 부재가 큼.
- **브랜드 노출 변수**: 공식몰은 "음파방석"만 표기 → AI가 "훌스(HOOL'S)"로 응답할지 "하이리빙 음파방석"으로 응답할지 실험에서 관측 필요.
  - runner.py COMPETITOR_KEYWORDS에 `["훌스", "HOOL", "hool"]` 등록됨
  - 하이리빙 브랜드명도 응답에 자주 등장하면 `KNOWN_OTHER_BRANDS` 에 추가 고려

## 의사결정

- 경쟁군 N=14에서 훌스 포함 유지.
- 대표 SKU URL = 하이리빙 공식몰 `www.hiliving.co.kr/goods/detail?code=300751`.
- 스마트스토어 로그인 벽 이슈는 **데이터 수집 측 제약**으로 문서화 (연구 한계 섹션).
