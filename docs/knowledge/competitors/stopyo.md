---
name: 스탑요 자동 케겔 운동기구
description: 쿠팡 단독 유통 공산품 케겔 운동기구. Akamai Bot Manager로 자동 크롤 제한 — 페이지 피처는 수동 수집 or 제외.
type: competitor
brand_id: stopyo
category: consumer_product
vertical: medical_device
mfds_registered: false
sku_representative: coupang_8637377284
last_checked: 2026-04-24
---

# 스탑요 자동 케겔 운동기구

## 포지셔닝

- **카테고리**: 공산품 케겔/골반저근 운동기구 (식약처 미등록)
- **유통 채널**: 쿠팡 단독 확인 (11번가/지마켓/옥션/스마트스토어 공개 채널 없음)
- **실재 확인**: Wayne 2026-04-24 — 쿠팡 itemId 8637377284 URL 제공
- **역할**: 경쟁군 레이블 유지 (AI 응답에서 언급되는지 관측), 페이지 피처는 수집 불가

## 확정 URL

```
https://www.coupang.com/vp/products/8637377284
```

## 크롤링 제약

- **쿠팡 Akamai Bot Manager**로 자동 접근 차단
  - curl_cffi Chrome124: HTTP 403 Access Denied
  - Playwright + playwright-stealth v2 domcontentloaded: 315 bytes (Access Denied 페이지)
- **우회 옵션**:
  - (a) Wayne 수동 저장 → `data/raw/medical_device/stopyo/coupang/2026-04-24/` 드랍 (5분)
  - (b) 쿠팡 로그인 쿠키 주입 (Wayne 개인 계정, privacy 리스크)
  - (c) undetected-playwright 등 고급 회피 도구 (ROI 낮음)
- **2026-04-24 결정**: (a) 여유 있을 때 실행, 우선은 페이지 피처 없이 **경쟁군 레이블로만 포함**

## AiEO 분석에서의 취급

| 영역 | 포함 여부 |
|------|--------|
| `runner.py` COMPETITORS 리스트 | ✅ 포함 (AI 응답에 "스탑요"가 언급되는지 관측) |
| `COMPETITOR_KEYWORDS["stopyo"]` | ✅ `["스탑요"]` 등록 |
| 데마 feature 모델 입력 | ❌ 페이지 피처 수집 불가 → 해당 row 제외 (전체 18→17 브랜드) |
| SHAP/벤치마크 비교 | ⚠️ 외부 증거(NAVER API) 있으면 "언급 빈도 기반 관측"만 가능 |

## 향후 액션

- Wayne 여유 있을 때 쿠팡 페이지 수동 저장 → 즉시 features 재처리 & 데마 모델 재학습 가능
- 쿠팡 다른 itemId(같은 브랜드 다른 SKU) 있으면 제공 요청
