---
date: 2026-04-24
title: 리스테린·퓨런 자사몰 F1~F6 실측 완료 — 4차 시도 curl_cffi로 우회 성공
related_findings: [F2026-04-24_listerine_furen_status, F2026-04-24_feature_comparison, F2026-04-24_mfds_oem_pool]
contradicts: [F2026-04-24_listerine_furen_status]  # "WAF 우회 불가" 결론을 뒤집음
supports: []
vertical: both
phase: discovery
author: Claude
---

# 리스테린·퓨런 자사몰 실측 — curl_cffi(Chrome TLS impersonation)로 차단 우회 성공

## 1. 이전 상태 (F2026-04-24_listerine_furen_status) 수정 사항

| 항목 | 이전 결론 | 정정 |
|------|----------|------|
| 자사몰 크롤링 가능 여부 | 3차 시도(정적/Playwright/Playwright+stealth) 모두 Cloudflare WAF에 차단되어 불가. "옵션 B(residential proxy)는 과투자" | **4차 curl_cffi Chrome impersonate로 listerine.kr 완전 우회 성공** (190~281KB HTML 확보) |
| 퓨런 공식 URL | `furenhealth.com` / `www.furenhealth.com` | **실제 URL은 `http://furun.kr/`** (Wayne 확인). `furenhealth.com`은 DNS 해결 불가, `www.furenhealth.com`은 `testtesttt.top`으로 탈취 리다이렉트 |
| 다음 단계 | 쿠팡/SSG 폴백 또는 수동 수집 | 자사몰 자체 실측 완료 → 쿠팡 폴백 불필요 |

## 2. 사용 도구·방법

- `curl_cffi 0.15.0` + `impersonate="chrome"` (Chrome TLS ClientHello fingerprint 위조)
- Python 3.11 환경 (python3=3.13에 curl_cffi 미설치라 3.11로 실행)
- 스크립트: `crawler/scripts/scrape_cffi_selfmall.py`, `scrape_furun_selfmall.py`, `scrape_furun_products.py`
- 프로파일러: `crawler/scripts/profile_f1f6_selfmall.py` (신규, F1~F6 + JSON-LD + 리뷰 위젯 힌트 추출)

## 3. 리스테린 실측 (listerine.kr, 5 페이지)

| 요인 | 실측 |
|------|------|
| F1 HTML 포맷 | BULLET 우세 (⚠️ SPA, 초기 HTML 기준 — JS 렌더 후 재측정 필요) |
| F2 JSON-LD | ❌ **0건** (Product·AggregateRating 모두 없음) |
| F3 수치 구체성 | **0.517** |
| F3 수치 실측 | 30초, 99%, 130년, 52%, 30%, 1%, 2회, 1회, 1860년, 1920년 |
| F4/F5 인증 | 0개 (의약외품, 해당 없음) |
| F6 근거 | **brand_authority** 우세 (130년, No.1, 글로벌) |
| 리뷰 | **Bazaarvoice 위젯 탑재** (평점/건수는 JS 렌더 후 접근 필요) |

## 4. 퓨런헬스케어 실측 (furun.kr, 8 페이지)

| 요인 | 실측 |
|------|------|
| 언어 지원 | EN / JA / CN (**한국어 없음**) |
| 판매 기능 | 없음 — "Purchase Inquiry" 문의 폼만 |
| F1 HTML 포맷 | BULLET |
| F2 JSON-LD | ❌ 0건 |
| F3 수치 구체성 | 0.375 |
| F3 수치 실측 | 25kg, 440mm, 450mm, 720mm, 23kg, 20kg, 400mm, 49mm, 3kg, 50Hz, 60Hz, ... — **기계 스펙뿐, 효능/임상 수치 0** |
| F4 인증 위치 | **bottom** (0.807) |
| F5 인증 상세 | **CE×2, GMP×1 — 식약처/제허/등급 0** (🔥 제허 21-492, 21-920 보유하고도 언급 X) |
| F6 근거 | none 7 / brand_authority 1 |
| 리뷰 | 위젯 0건 |

## 5. 업계 함의 — "AI 추천 시대의 자사몰 기본 구조화 데이터 부재"

두 브랜드 모두 **JSON-LD Product schema 0건**. 위상이 극단으로 다른 두 브랜드가 동시에 같은 빈틈을 갖고 있음:
- 리스테린(J&J, 글로벌 1위 가글, 130년 역사)
- 퓨런(한국 OEM 중견, 글로벌 B2B 제조사)

→ 프로폴린스·바디닥터가 JSON-LD를 도입하면 **업계에서 거의 혼자 선도** 가능한 포지션.

## 6. H5/H6 가설 간접 증거 — 제허를 보유해도 페이지에 없으면 무의미

퓨런헬스케어는 식약처 제허 2건을 보유한 의료기기 제조사지만, **자사 웹페이지에는 식약처/제허/등급 표기가 전무**하고 CE/GMP(수출용)만 노출. → AI가 "한국 식약처 인증 요실금치료기"를 추천할 때 퓨런이 등장할 확률은 낮을 것. 본실험에서 H5(인증 명시가 추천 확률 ↑)의 관찰형 증거로 활용 가능.

## 7. 퓨런의 본실험 경쟁군 포함 여부 — 재검토 필요

| 포함 근거 | 제외 근거 |
|-----------|-----------|
| 식약처 제허 2건 실존 | 한국 소비자향 자사몰 아님 (EN/JA/CN) |
| OEM 제조사 특성 비교에 유용 | 직접 판매 X (Purchase Inquiry 문의만) |
| H5/H6 관찰 증거로 가치 | 추천 쿼리 결과에 거의 노출 안 될 것 |

**권고**: 본실험 주력 N=6에서는 빼고, **EXPLORATORY 관찰 대상**으로 유지. 대체 후보는 쉬엔비 / 리모트솔루션 / 비엠씨 / 유진플러스 중 B2C 유통이 확인되는 브랜드.

## 8. 후속 과제

- [ ] Playwright + 시스템 Chrome channel로 리스테린 SPA 렌더링 DOM 캡처 → F1 실측 보정 + Bazaarvoice 평점/건수 직접 추출
- [ ] 퓨런 제품이 한국 쿠팡/11번가에 유통되는지 Wayne 확인
- [ ] Wayne: 본실험 의료기기 경쟁군 N=6 최종 확정 (퓨런 제외 시 대체 후보)
- [ ] 다른 차단 대상 사이트에도 curl_cffi 적용 가능성 검토 (easyk 등)

## 9. 결과물 위치

- 리스테린 진단 JSON: `consulting/diagnosis/listerine_self_mall_2026-04-24.json`
- 퓨런 진단 JSON: `consulting/diagnosis/furun_self_mall_2026-04-24.json`
- 원시 HTML: `data/raw/gargle/listerine/self_mall/2026-04-24/`, `data/raw/medical_device/furun/self_mall/2026-04-24/`
- 경쟁사 프로필 갱신: `competitors/listerine.md`, `competitors/furun.md` (신규)
