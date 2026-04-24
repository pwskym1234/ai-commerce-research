---
topic: L54 직교배열 본실험 설계 (v2 확정본)
supersedes: methods/orthogonal_array_L36.md (v1)
references:
  - experiments/design_matrix.py
  - experiments/synthetic_pages/design_matrix.csv
  - experiments/synthetic_pages/_template.html.j2
last_updated: 2026-04-24
---

# L54 직교배열 — 실제 구현 채택안

## 0. 구현 접근

정통 L54 표(2^1 × 3^25)는 R `DoE.base` 기반. Python 직접 구현 어려움.

**채택안**: **L27(3^13) Taguchi 표 + replication 2회 = 54 runs**

### 왜 이 방식이 L54 동등?
- L27은 Taguchi 표준 표로 **3수준 요인 13개까지 주효과 + 일부 교호작용** 검정 가능
- 복제 2회 = 54 runs → **오차 추정 + 검정력 2배 향상**
- **모든 2요인 페어의 9 조합이 6회씩 균등 출현 (실측 직교성 검증 완료)**
  - F1×F2, F3×F4, ..., F5×F6 15페어 모두 `min=6, max=6`
- H3(F1×F2), H15(Q×F), F4×F6 등 2차 교호작용 **전부 검정 가능**

### 정통 L54 대비 차이
- 정통 L54: 54개 서로 다른 조합 (복제 없음)
- 우리 L27×2: 27개 조합을 2회씩 (복제 有)
- **장점**: 순수 오차(pure error) 추정 가능 → 모델 적합도 평가 강화
- **단점**: 27개만 고유 조합이라 일부 고차 교호작용 검정 불가 (우리 가설엔 필요 없음)

## 1. 설계 매트릭스

### 생성 스크립트
[`experiments/design_matrix.py`](../../../experiments/design_matrix.py)

### 실측 직교성 리포트
```
Runs: 54
주효과 균등: ✅ 모든 F (F1~F6) 각 수준 18회 출현
2요인 페어 균등 (9 조합 × 6회 기대):
  ✅ F1×F2: min=6 max=6
  ✅ F1×F3: min=6 max=6
  ...
  ✅ F5×F6: min=6 max=6
(15 페어 전부 balanced)
```

### 저장 위치
- CSV: [`experiments/synthetic_pages/design_matrix.csv`](../../../experiments/synthetic_pages/design_matrix.csv)
- 54행 × (page_id + F1~F6 수준명 + F1~F6 수준 인덱스)

## 2. 요인 & 수준 (최종)

| 요인 | 수준 0 | 수준 1 | 수준 2 |
|------|--------|--------|--------|
| F1 HTML 포맷 | TABLE | BULLET | PARAGRAPH |
| F2 JSON-LD | MedicalDevice-Full | Product-Minimal | None |
| F3 수치 구체성 | Accurate | Partial | Ambiguous |
| F4 인증 위치 | Top | Bottom | None |
| F5 인증 상세 | Full (3등급+허가번호) | Partial (인증완료만) | None |
| F6 근거 | Clinical (RCT 수치) | Reviews (후기+셀럽) | None |

## 3. 가상 페이지 생성

### 템플릿
[`experiments/synthetic_pages/_template.html.j2`](../../../experiments/synthetic_pages/_template.html.j2)

Jinja2 기반. F1~F6 수준 조합에 따라 조건부 렌더.

### 공통 제품 정보
[`experiments/synthetic_pages/_product.json`](../../../experiments/synthetic_pages/_product.json)

- 가상 브랜드 "TestBrand X" (실제 경쟁사 충돌 회피)
- spec 3버전 (정확/부분/모호) 사전 정의 — F3 수준에 매핑

### 생성 실행
```bash
python experiments/synthetic_pages/render_pages.py
```
→ `page_001.html` ~ `page_054.html` 생성 완료 (2026-04-24)

## 4. 본실험 실행 계획

### 파일럿 모드 (Week 3 초반)
```bash
python experiments/runner.py --mode pilot
```
- L27 (첫 27개 페이지) × 2쿼리(BRD, CAT) × 5회 = **270 호출**
- 예상 비용: ~$3.4
- 목적: 변동성 측정 + Y 변수 파싱 검증

### 본실험 모드 (Week 3 후반~Week 4)
```bash
python experiments/runner.py --mode main
```
- L54 × 8쿼리 × 20회 = **8,640 호출**
- 예상 비용: ~$108
- gpt-5.4 기본 (.env `OPENAI_MODEL_VERSION=gpt-5.4`)

### 비용 안전장치
- 응답 캐시: `experiments/api_runs/_cache/` — 같은 (model, prompt, seed) 호출 한 번만
- Dry-run: `--dry-run` 옵션으로 호출 수·비용 사전 확인
- jsonl append — 중간 실패 시 재개 가능

## 5. 가설 검정 매핑

| 가설 | 검정 모델 |
|------|---------|
| H1~H7 (주효과) | 각 F 계수 logit(Y2a) ~ F1+F2+...+F6 |
| H3 (F1×F2 교호) | F1:F2 interaction term |
| H8 (Y1 ≠ Y2a) | Y1-Y2a Pearson r |
| H9 (경쟁 규모) | 별도 실험 (N 변화) |
| H10 (의료기기/비의료기기) | 경쟁군의 drk 포함/제외 비교 |
| H11 (키워드 명시) | SYM vs CAT 쿼리 비교 |
| H12 (SPN) | USE × F6 교호작용 |
| H14 (외부 증거) | 데마 관찰형 — 본실험 외 |
| H15 (Q×F) | Q:F interaction terms |

## 6. 한계 고백

1. **L54가 정통 Taguchi 표는 아님** — L27×2 복제. 하지만 직교성은 실측으로 동일 보장.
2. **F3 수준 3개지만 spec의 난이도 분포가 문학적**: "정확/부분/모호"는 주관적 구분. Wayne 검수 필요.
3. **가상 페이지는 한국어 텍스트**: 한국어 LLM 토크나이저 특성은 영어와 다를 수 있음. gpt-5.4는 다국어이나 편향 존재.
4. **경쟁사 이름(바디닥터/이지케이 등)을 쿼리에 포함**: AI가 학습한 prior을 상기시켜 페이지 효과를 부분적으로 희석 가능. **쿼리 버전 A(브랜드명 없음) + 버전 B(브랜드명 포함)** 로 분리 실험 권고.
