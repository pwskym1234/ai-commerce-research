# H1~H15 가설 ↔ 태깅 차원 / 자동 X 매핑

> Wayne 지적 (2026-04-25): "태깅 요소에 H1~H15 가설들이 반영된 부분들이 있나?"
> → 매핑 명시 안 했던 누락. 본 문서로 정리.
>
> 데마 / 산공통 분석 시 어떤 X 변수로 어떤 가설을 검정할지 명확히.

## 매핑 테이블

| H | 가설 한 줄 | 핵심 X 변수 | 우선순위 |
|---|---------|-----------|--------|
| H1 | HTML 포맷이 파싱 정확도 영향 | **T1 주도 포맷** (TABLE/BULLET/PARAGRAPH/IMAGE_HEAVY) + 자동 table_count·list_item_count·paragraph_count | P0 |
| H2 | JSON-LD 스키마가 파싱 정확도 영향 | 자동 `has_jsonld` + `jsonld_field_count` + Sixthshop A1~A6 | P0 |
| H3 | F1×F2 교호작용 (HTML × JSON-LD) | T1 × has_jsonld interaction term in 회귀 | P0 |
| H4 | 수치 구체성이 파싱 정확도 영향 | 자동 `numeric_specificity_ratio` + `explicit_number_count` + **G2 유효 성분 함량** | P0 |
| H5 | 인증 명시가 추천 확률 ↑ | **T2 cert_position** + 자동 `cert_keyword_count` + `cert_grade_mentioned` + **M3 KFDA 등급** + **Q7 trust_claim_tone** | P0 |
| H6 | 인증 명시가 Y4 안전 회피 ↓ | T2 + **M5 부작용 표기** + **Q2 safety_disclaimer** + Y4 (parsed_claude `safety_avoidance`) | P0 |
| H7 | 임상 인용 > 사용자 후기 | **T3 evidence_type (CLINICAL vs REVIEWS)** + **M2 clinical_evidence (OWN_TRIAL/LITERATURE/EXPERT/TESTIMONIAL)** + 자동 `clinical_keyword_count` | P0 |
| H8 | Y1 ≠ Y2 (GEO 정확도 ≠ AiEO 추천률) | 메타 가설 — 분석 단계 (산공통 본실험 두 Y 비교) | — |
| H9 | 경쟁 상황(CMP/COM 쿼리)에서 구조화 효과 ↑ | qtype (CMP/COM) × T1·has_jsonld interaction term | P1 |
| H10 | AI는 의료기기·비의료기기 구분 못해 점유율 희석 | 자동 mfds_registered (의료/공산품 라벨) + parsed_claude `mentioned_brands` (Elvie/Perifit 등 글로벌 NER) | P0 |
| H11 | 쿼리에 "의료기기" 명시 시 카테고리 좁힘 | 쿼리 텍스트 분석 (의료기기 키워드 포함 여부) — 쿼리 변형 실험 | P1 |
| H12 | Rufus SPN × F6 (USE 쿼리) 교호작용 | Rufus SPN 5 facet 매핑: **Q1 콘텐츠 깊이**=quality / **T10 USP**=value / **M4 타겟 환자군**=fit / **M5 부작용**=safety / **Q4 소셜 프루프**=community | P0 |
| H13 | ~~Rich card rendering~~ | 드롭 (API 구조 파싱 한계) | — |
| H14 | 외부 증거(리뷰·인용·커뮤니티)가 추천 ↑ | **external_evidence.jsonl** (NAVER blog_total / cafe_total / news_total / shop_total) — 25 브랜드 수집 완료 | P0 |
| H15 | 쿼리 × F 교호작용 | qtype × 모든 X interaction term in 회귀 | P0 |

## 데마 vs 산공통 검정 분리

### 데마 (관측형 — 실제 페이지 + B1 응답)
- **검정 가능**: H1, H2, H4, H5, H7, H10, H12, H14, H15 (관측형 상관)
- **검정 어려움**: H3, H6, H9 (교호작용은 통제 실험이 더 적합)
- 분석 방법: SHAP 기여도 + 단변량 상관 + Bootstrap CI

### 산공통 (통제 실험 — L54 가상 페이지 + 본실험)
- **인과 검정 가능**: H1, H2, H3, H4, H5, H6, H7, H9, H12, H15
- 분석 방법: 로지스틱 회귀 + odds ratio + 95% CI + 교호작용항 + 다중비교 보정

### 두 프로젝트 공통 (메타)
- H8 (Y1 vs Y2): 산공통 본실험에서 두 Y 변수 비교
- H10, H11: 데마 NER 분석 + 산공통 쿼리 변형 검정
- H14: 데마 외부 증거 feature + 산공통 페이지 외부 증거 메타 변수

## 태깅 시 우선순위 재해석

P0 17 차원 (전체 매뉴얼 가이드와 일치):
- T1, T2, T3, T7, T10 (페이지 구조)
- Q1, Q2, Q4, Q7 (공통 정성)
- M1, M2, M3, M4, M5 (의료기기 특화)
- G1, G2, G3, G4 (가글 특화)

→ **이 17개가 H1, H2, H4, H5, H6, H7, H10, H12 직접 검정 입력**.

P1·P2 차원은 H 가설과 직접 연결 약함 — 시간 부족 시 후순위로 미룰 수 있음.

## 분석 시 적용

```python
# B2 baseline (데마)
X = features_auto + manual_tags  # 자동 22 + 수동 17 = ~40 차원
Y = mention_rate_per_brand_query

# H5 검정 (인증 명시 → 추천 ↑)
import statsmodels.api as sm
X_h5 = X[["T2_cert_position", "cert_keyword_count", "M3_kfda_class", "Q7_trust_claim_tone"]]
model = sm.Logit(Y, sm.add_constant(X_h5)).fit()
print(model.summary())  # odds ratio + 95% CI

# H7 검정 (임상 > 후기)
X_h7 = pd.get_dummies(X["T3_evidence_type"])  # CLINICAL/REVIEWS/MARKETING/...
# CLINICAL coefficient > REVIEWS coefficient 인지 검정
```

## 갱신 이력

- 2026-04-25 v1: Wayne 지적 받고 매핑 추가
