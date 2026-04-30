---
brand: Perifit
brand_slug: perifit
vertical: medical_device
last_updated: 2026-04-30
data_sources:
  - https://perifit.co/ (글로벌 공식 D2C)
  - https://perifit.co/products/kegel-exerciser-with-app (Care 모델 페이지)
  - https://perifit.co/products/new-kegel-exerciser-with-app-perifit-plus (Care+ 모델 페이지)
  - https://perifit.co/pages/kegel-exercisers (FDA-cleared 명시 페이지)
  - https://perifit.co/pages/faq-perifit
  - https://www.accessdata.fda.gov/cdrh_docs/pdf22/K221476.pdf (FDA 510(k) 원문 — 1차 출처)
  - https://fda.innolitics.com/submissions/GU/subpart-b%E2%80%94obstetrical-and-gynecological-diagnostic-devices/HIR/K221476
  - https://femtechinsider.com/fda-510k-clearance-perifit/
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC10956527/ (2024 Women's Health Reports 임상논문)
  - https://accessgudid.nlm.nih.gov/devices/03770014642448 (FDA GUDID 디바이스 등록)
manufacturer: X6 Innovations (등록명) / Perifit (브랜드)
manufacturer_country: 프랑스 파리 (개발·제조)
distributor_kr: 없음 (한국 정식 수입사·총판 미확인. 한국어 페이지/매뉴얼도 미확인)
official_urls:
  global: https://perifit.co
  product_care: https://perifit.co/products/kegel-exerciser-with-app
  product_care_plus: https://perifit.co/products/new-kegel-exerciser-with-app-perifit-plus
  fda_510k: https://www.accessdata.fda.gov/cdrh_docs/pdf22/K221476.pdf
note_url_dot_com: perifit.com이 아니라 perifit.co가 공식 도메인 — Wayne URL 검증 룰 따라 추정 금지
distribution_channels:
  - perifit.co (D2C 글로벌)
  - Amazon.com (US)
  - CMT Medical, Veterans Medical (US 의료유통)
  - Pelvicfloorexercise.com.au (호주)
  - 한국: 정식 채널 없음 (직구만 가능)
fda_grade: Class II                       # 21 CFR 884.1425 Perineometer
fda_clearance_number: K221476             # ★ 확정 (FDA accessdata 1차 출처)
fda_clearance_date: 2023-02-10
fda_product_code: HIR
fda_review_panel: Obstetrical and Gynecological
ce_mark: likely_yes                       # 프랑스 본사 + 유럽 판매 → 보유 강한 추정. 페이지 명시 fetch에선 미확인
mhra_registration: unknown
mfds_grade: 없음 (한국 미등록 추정)
mfds_status: 한국 식약처 등록 없음 — 의료기기 정식 수입 절차 미확인
gmp_certified: unknown
price_usd_care: 119.20                    # 세일가. 정가 $149.00
price_usd_care_plus: unknown              # 별도 페이지 fetch 필요
korea_direct_purchase: 가능 (개인 직구) — 의료기기 개인 사용 직구 한도/통관 절차 확인 필요
f1_html_format: bullet_paragraph_mixed    # 표 없음, 불릿+본문 단락 혼합
f2_jsonld: unknown_likely_partial         # Shopify 기반 → Product schema 자동 생성 가능성. 직접 raw HTML 검증 필요
f3_numeric: explicit_with_citation        # ★ 강점 — "85% 개선", "6,060명 코호트", PubMed 25349943 인용
f4_cert_position: medium                  # FAQ 섹션에 FDA-Cleared 명시. 헤더/가격 근처 배지는 없음
f5_cert_detail: explicit_partial          # FDA-Cleared 텍스트 명시. 510(k) 번호 K221476은 페이지에 미명시 (FDA 데이터베이스에선 확정)
f6_evidence: clinical_with_user_reviews   # ★ 임상연구(2024 Women's Health Reports, n=6,060) + 2,814 후기 + 85% 5★
english_content_richness: high            # 가이드/FAQ/블로그/매뉴얼 전부 영어 풍부
clinical_study_n: 6060                    # 2024 Women's Health Reports 코호트 크기
status: confirmed
priority: 글로벌_벤치마크
---

# Perifit — 게임화 케겔 의료기기, 임상 근거 강한 글로벌 D2C

## 핵심 사실 (검증 완료)

### 회사 구조
- **법인 등록명**: X6 Innovations (FDA 510(k) 신청자명)
- **브랜드**: Perifit
- **본사**: 프랑스 파리 (개발·제조)
- **공식 도메인**: [perifit.co](https://perifit.co) — **`.com` 아님**. Wayne URL 검증 룰 적용 (퓨런 furenhealth.com 사고 재발 방지).

### 제품 라인업
- **Perifit Care** ($149 정가 / $119.20 세일) — 본 분석 대상. Original Kegel Exerciser.
- **Perifit Care+** — 업그레이드 모델. 별도 페이지 fetch 필요.

### ★ 인증 (1차 출처 확정)
- **FDA 510(k) clearance**: **K221476** (2023-02-10 결정)
- **신청자**: X6 Innovations, Lina Kontos (Hogan Lovells 자문)
- **분류**: Class II Perineometer (21 CFR § 884.1425)
- **Product Code**: HIR (Obstetrical and Gynecological Diagnostic)
- **Substantially Equivalent** 판정, 검토 266일 소요
- **GUDID 디바이스 ID**: 03770014642448 ([accessgudid.nlm.nih.gov](https://accessgudid.nlm.nih.gov/devices/03770014642448))
- **CE**: 프랑스 본사 + EU 판매 → 보유 강한 추정. 페이지 명시 미확인.
- **한국 식약처**: **미등록**. 정식 수입 채널 없음.

### 스펙 / 가격
- **메커니즘**: 실리콘 시스 안의 sensor가 골반저근 수축 강도 측정 → Bluetooth로 스마트폰 앱 전송 → 게임화 biofeedback.
- **크기**: 길이 8.3cm × 직경 3.1cm.
- **소재**: medical-grade silicone, BPA·프탈레이트 free.
- **사용**: 주 3~5회 × 10분.
- **가격**: Care $119.20 (세일가), 정가 $149.00.
- **반품 정책**: 100일 무료 반품 (이례적으로 관대함 — 임상 근거 자신감 시그널).

### 한국 시장
- 정식 수입사·총판 **없음**.
- 한국어 페이지·매뉴얼 미확인 (Elvie와 달리 한국어 PDF조차 없음 — Elvie 대비 한국 인지도 낮을 만한 구조).
- 직구 가능하나 의료기기 통관 한도/절차 확인 필요.

## 페이지 진단 — perifit.co/products/kegel-exerciser-with-app (2026-04-30 직접 검증)

| 항목 | 현재 상태 | F 등급 매칭 |
|------|----------|-----------|
| 가격 | $119.20 (세일) / $149.00 (정가) 명시 | — |
| FDA-Cleared | **FAQ 섹션에 명시** ("FDA-Cleared devices") | F4=**medium** |
| 510(k) 번호 K221476 | **페이지 미명시** (FDA 데이터베이스에서만 확정) | F5=**explicit_partial** |
| CE 표기 | 미명시 | — |
| 스펙 표현 | 불릿 리스트 + 본문 단락. **표 없음** | F1=bullet/paragraph 혼합 |
| 수치 구체성 | ★ "85% 개선", "6,060명 코호트", "1/4 부정확 운동 위험", "50% 여성 케겔 잘못 수행" — **PubMed 인용 포함** | F3=**explicit_with_citation** |
| 임상 인용 | PubMed 25349943 직접 링크. 2024 Women's Health Reports 별도 인용 | F6=**clinical_with_user_reviews** |
| JSON-LD | Shopify 기반 → Product schema 자동 가능성. 직접 fetch raw HTML 검증 필요 | F2=**unknown_likely_partial** |
| 사용자 후기 | 2,814 reviews, 85% 5★ | — |
| 보증/반품 | 100일 무료 반품 | — |

→ **Elvie 대비 강점**: 임상 근거 인용(F6), 수치 출처 표기(F3). FDA-Cleared **텍스트** 명시. 단, 510(k) 번호와 등급은 페이지에서 보이지 않음.

## ★★ 결정적 발견 — LLM 응답 vs 한국 검색 *역전* 패턴

| 채널 | 노출량 |
|------|-------|
| LLM 응답 mention (Phase B1) | **40회** |
| 한국 NAVER 검색 결과 | **74회** |

**Elvie와 정반대 패턴** — Perifit은 **NAVER 검색이 LLM mention보다 많음**.

**격차 역전 가설**:

1. **NAVER 검색이 더 많은 이유** — 한국 블로그/카페/리뷰 사이트에서 게임화 케겔 트레이너 컨텐츠로 회자. 직구 후기 + "재밌는 케겔" narrative가 한국 여성 커뮤니티에서 공유 가능성. (검증: NAVER 카페·블로그 키워드 추출 필요)
2. **LLM mention이 상대적으로 낮은 이유** — Elvie 대비 후발주자(2018 창업 vs 2013), 영문 매체 보도 분량 적음, "first kegel trainer" 정의자 지위 없음. 그러나 **임상 근거(n=6,060 PubMed)** 가 LLM 응답 신뢰도엔 강하게 작동.
3. **결론**: 한국 직구 커뮤니티에선 "게임화 + 가성비"가 떴지만, 글로벌 영문 코퍼스에선 카테고리 정의자(Elvie) 그늘에 가려진 패턴. 바디닥터K 입장에선 **"임상 인용을 페이지에 명시한다"는 전략이 LLM 추천에 효과적일 수 있다는 후보 가설**의 1차 증거.

## AiEO 본실험 함의

- **F3 (수치 구체성) + F6 (근거)**: Perifit은 PubMed 직링크 인용을 페이지에 노출. **이 디테일이 LLM 신뢰도 시그널로 작동하는지 본실험에서 검증 가치 높음**. H1·H2 가설(수치 구체성 → 추천 ↑)의 강력한 자연 실험 사례.
- **F5 (인증 명시)**: Perifit은 "FDA-Cleared" 텍스트를 명시했지만 **510(k) 번호 자체는 페이지에 없음**. 바디닥터K가 "제허XX-XXX호"를 페이지에 명시했을 때 효과가 있는지 vs 단순 "식약처 인증" 텍스트만 있는 경우 비교 가설로 활용 가능.
- **F4 (인증 위치)**: FAQ 섹션 위치 → 헤더/가격 근처가 아닌 footer 영역. 위치별 가시성 효과 검증 가능.
- **글로벌 D2C 벤치마크**: Shopify 기반 영문 D2C의 표준 구조 → 바디닥터K 페이지 리뉴얼 시 참고 가능.
- **버티컬 비교 (Elvie vs Perifit)**:
  - Elvie: 글로벌 카테고리 정의자, 영문 콘텐츠 압도, 페이지 인증 명시 약함 → LLM mention 44
  - Perifit: 임상 근거 강함, 페이지 FDA 명시, 후발주자 → LLM mention 40
  - **두 변수(영문 콘텐츠 풍부도 vs 페이지 인증 명시도)가 LLM 추천에 미치는 상대적 가중치**가 본실험의 핵심 검증 포인트.

## 미확정 / 다음 액션
- [ ] perifit.co raw HTML fetch (curl_cffi) → JSON-LD 실제 schema 종류 확인
- [ ] Care+ 모델 페이지 별도 fetch 및 가격 확인
- [ ] CE mark + EU 인증 1차 출처 확인 (EUDAMED 데이터베이스)
- [ ] Care 모델 GBP / EUR 가격 (지역 IP 우회)
- [ ] 한국 NAVER 카페·블로그 mention 74건의 출처 분해 — 어디서 한국 인지도가 형성됐나
- [ ] Elvie와 공통 직구 후기 사이트 교차 비교

## 참고 링크
- [Perifit Care 공식 페이지](https://perifit.co/products/kegel-exerciser-with-app)
- [Perifit FDA-cleared 페이지](https://perifit.co/pages/kegel-exercisers)
- [FDA 510(k) K221476 원문 PDF](https://www.accessdata.fda.gov/cdrh_docs/pdf22/K221476.pdf)
- [FDA Innolitics 510(k) 검색 결과](https://fda.innolitics.com/submissions/GU/subpart-b%E2%80%94obstetrical-and-gynecological-diagnostic-devices/HIR/K221476)
- [FDA GUDID 디바이스 등록](https://accessgudid.nlm.nih.gov/devices/03770014642448)
- [2024 Women's Health Reports 임상논문 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10956527/)
- [Femtech Insider — FDA clearance 보도](https://femtechinsider.com/fda-510k-clearance-perifit/)
