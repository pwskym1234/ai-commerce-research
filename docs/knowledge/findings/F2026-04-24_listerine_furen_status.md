---
date: 2026-04-24
title: 리스테린·퓨런헬스케어 크롤링 목적 + 시도 이력 + 결과 + 다음 단계
related_findings: [F2026-04-24_feature_comparison]
contradicts: []
supports: []
vertical: both
phase: discovery
author: Claude
---

# 리스테린·퓨런헬스케어 — 상태 정리

## 1. 왜 이 두 브랜드 크롤링이 필요한가

### 리스테린 (가글 버티컬)
- 본실험 가글 N=6 중 **필수 경쟁자** (글로벌 1위 가글 브랜드)
- 수집 목적:
  1. **페이지 F1~F6 수준 실측** (Sixthshop 점수 baseline)
  2. **JSON-LD 유무 확인** → 프로폴린스 대비 구조화 데이터 격차
  3. **리뷰 수·평점** (H14 external evidence 변수)
  4. 4가지 에센셜 오일 / 99.9% 살균 같은 수치 클레임 실제 페이지 노출 확인

### 퓨런헬스케어 (의료기기 버티컬)
- 본실험 의료기기 N=6 중 **확정 경쟁자** (식약처 제허 21-492, 21-920 두 건 보유)
- 수집 목적:
  1. 페이지 F1~F6 수준 실측
  2. **세라젬(대기업) vs 퓨런(중견 전문)** 차별 포지셔닝 확인
  3. 제품명/모델명/가격/리뷰 (본실험 prompt 구성 재료)

## 2. 시도 이력

### 2-1. 1차: 정적 fetch (2026-04-23)
- `requests.get(...)` 직접 호출
- 결과: 둘 다 응답 받았으나 **JS 미실행 상태라 빈 페이지**

### 2-2. 2차: Playwright (2026-04-24 오전)
- Chromium headless + `wait_until="networkidle"`
- 결과:
  - listerine.kr: **294 bytes** (bot 차단)
  - listerine.kr/products/gum-care-mild: **316 bytes**
  - furenhealth.com: **795 bytes** (timeout + 차단)

### 2-3. 3차: Playwright + stealth (2026-04-24 오후)
- `playwright-stealth` v2 설치 + context에 apply
- `wait_until="domcontentloaded"` + timeout 40초로 완화
- 결과: **동일 bytes**로 완전 차단
  - listerine 292/314
  - furenhealth 795
- 해석: **WAF 또는 Cloudflare Advanced Bot Protection** 수준의 방어. stealth 우회 불가.

## 3. 현재 확보된 정보 (검색 + 기타 자료)

### 리스테린
- **공식 한국 사이트**: listerine.kr (차단되어 fetch 실패, 검색 결과로 정보 수집)
- 라인업: 쿨민트 / 후레쉬버스트 / 시트러스 / 내추럴 그린티 마일드 / 티스앤드검 디펜스 / 타르타르 컨트롤 / 토탈케어
- 핵심 클레임: "30초 사용 시 입속 세균 99.9% 제거", "효과 12시간 지속", "5배 프라그 억제"
- 4가지 에센셜 오일: 유칼립톨, 레보멘톨, 티몰, 살리실산메틸
- [competitors/listerine.md](../competitors/listerine.md)에 정리됨

### 퓨런헬스케어
- 식약처 등록: 제허 21-492, 21-920 (비이식형 요실금 신경근 전기자극장치)
- 공식 사이트(furenhealth.com) fetch 차단
- [competitors/_medical_device_oem_pool.md](../competitors/_medical_device_oem_pool.md)에 목록만 확인

## 4. 다음 단계 (권고)

### 옵션 A — 3rd party 채널 우회 (권장)
두 브랜드 모두 **쿠팡/SSG/코스트코/11번가**에 상품 페이지 존재. 이커머스 플랫폼은 Cloudflare 차단 덜 함.

**Wayne 또는 데마 팀 작업**:
- 리스테린: 쿠팡의 인기 모델 1~2개 직접 검색 후 URL 공유 → 크롤러 실행
- 퓨런: 쿠팡/11번가에서 "퓨런헬스케어 요실금치료기" 검색 후 URL 공유

**장점**: 실구매 페이지 + 리뷰 수 직접 수집 가능  
**단점**: 자사몰의 JSON-LD 구조 확인 못 함 (그러나 이커머스 플랫폼의 JSON-LD는 다 동일한 Product 스키마라 큰 문제 아님)

### 옵션 B — 본격 bot-bypass 투자
- 유료 residential proxy ($20~50/월)
- Puppeteer stealth + CDP 저수준 제어
- 실제 Chrome 프로필 + 사용자 인터랙션 시뮬레이션

**판단**: 본 프로젝트 scope에 과투자. 옵션 A로 충분.

### 옵션 C — 수동 수집
Wayne이 브라우저로 직접 페이지 열어 HTML Save As → data/raw에 투입

**단점**: 자동화 안 됨, 재현성 약함. 그러나 1회성 baseline 측정엔 OK.

## 5. 본실험·컨설팅 영향

### 본실험
**영향 미미**. 이유:
- 가설 검정은 **가상 페이지 통제 실험**이 메인
- 리스테린·퓨런 데이터는 **데마 관찰 분석**용 (H14 외부 증거)
- 자사몰 대신 쿠팡 페이지로 대체해도 **Sixthshop 점수 산출 가능**

### 컨설팅
**Before/After 비교표 한 줄이 아쉬움**. 
- "바디닥터 vs 세라젬 vs 퓨런" 의료기기 풀 비교 못 함
- "프로폴린스 vs 리스테린 vs 가그린" 가글 풀 비교 못 함

**대체**: 쿠팡 상품 페이지 기준으로 비교 (충분).

## 6. Wayne 결정 대기

- [ ] 옵션 A (쿠팡/SSG 우회) 채택? — 권장
- [ ] 리스테린 쿠팡 모델 1~2 URL 공유
- [ ] 퓨런 쿠팡/11번가 URL 공유 (퓨런은 온라인 유통 범위 자체가 좁을 수 있음 — 확인 필요)
