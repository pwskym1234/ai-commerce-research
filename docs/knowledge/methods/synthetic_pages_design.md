---
topic: 가상 페이지 36개 제작 기준 — 산공통 통제 실험용
when_to_use: 산공통 본실험 시작 전 가상 페이지 일괄 제작 시 표준 가이드
not_to_use: 데마 실제 크롤링 데이터 가공 (다른 트랙)
references:
  - PROJECT_MASTER.md §4.1
  - methods/orthogonal_array_L36.md
  - findings/F2026-04-23_empty_product_pages.md (실제 baseline 참조)
last_updated: 2026-04-23
---

# 가상 페이지 36개 제작 기준 — 산공통 통제 실험

## 0. 목적

L36 직교배열에 따른 36개 가상 의료기기 제품 페이지를 제작.
- 각 페이지 = (F1, F2, F3, F4, F5, F6) 6개 요인의 특정 수준 조합
- 같은 "허구의 의료기기" 제품을 6요인만 변형해서 36가지 버전으로 표현
- **변하지 않는 것**: 제품의 본질 (브랜드 X 요실금치료기, 기본 효능, 가격대)
- **변하는 것**: 6요인의 *표현 방식* (HTML 포맷, JSON-LD, 수치 구체성, 인증 위치/상세, 임상 근거)

## 1. 가상 제품 정의 (모든 페이지 공통)

```
브랜드명: TestBrand X (실제 경쟁사와 충돌 안 하도록 가상)
제품명: TestBrand X 케겔운동기 / 요실금치료기
카테고리: 비이식형 요실금 신경근 전기자극장치 (의료기기)
가격: 250만원 (실제 시장가에 맞춤 — 바디닥터 280만, 이지케이 100만대 사이)
모델 번호: TBX-100
제조사: Test Corp (가상)
```

핵심: **실제 경쟁사 페이지의 baseline 진단 결과**(인증 표기 없음, 텍스트 거의 없음)를 *F=없음 수준*에 정확히 대응시키고, 그보다 위의 수준들은 우리가 컨설팅으로 제안하는 모범 형태로 설계.

## 2. 6요인 수준 정의 (정밀)

### F1 HTML 포맷 (3수준)

| 수준 | 설명 | 마크업 패턴 |
|------|------|-----------|
| TABLE | 스펙을 `<table>` 행/열로 | `<tr><th>주파수</th><td>50Hz</td></tr>` |
| BULLET | `<ul><li>` 리스트 | `<ul><li>주파수: 50Hz</li>...</ul>` |
| PARAGRAPH | 산문 단락 | `<p>본 제품은 50Hz 저주파 자극을...</p>` |

스펙 항목 (모두 동일): 주파수, 단계 수, 사용 시간, 모드 수, 무게, 크기 — 6개 항목

### F2 JSON-LD (3수준)

| 수준 | 설명 |
|------|------|
| MedicalDevice | `<script type="application/ld+json">{"@context":"https://schema.org","@type":"MedicalDevice","name":"TBX-100",...}</script>` |
| Product | `{"@type":"Product","name":"TBX-100",...}` (일반 Product 스키마) |
| 없음 | JSON-LD 태그 자체 미삽입 |

각 변형의 필드 수는 동일 (name, brand, description, price, image 5개)

### F3 수치 구체성 (3수준 — F3 확장 권고 적용)

| 수준 | 예시 |
|------|------|
| 정확 | "주파수 50Hz, 99단계 강도 조절, 5단계 자동 프로그램, 사용 시간 1회 15분" |
| 부분 | "저주파 자극, 다단계 강도 조절, 자동 프로그램, 짧은 시간 사용" (수치 일부) |
| 모호 | "강력한 EMS, 다양한 강도, 편리한 자동 모드" (수치 0) |

### F4 인증 정보 위치 (3수준)

| 수준 | 페이지 위치 |
|------|----------|
| 상단 | 페이지 상단 배너 영역에 인증 정보 표시 (스크롤 안 해도 보임) |
| 하단 | 페이지 하단 푸터/마지막 섹션에 표시 |
| 없음 | 인증 정보 자체를 페이지에서 누락 |

### F5 인증 명시 수준 (3수준)

| 수준 | 텍스트 |
|------|------|
| 풀 | "식약처 3등급 의료기기 — 비이식형 요실금 신경근 전기자극장치 (허가번호 제허XX-329호) / FDA Class 1·2 등록" |
| 인증완료만 | "식약처 인증 의료기기" |
| 없음 | (텍스트 자체 없음) |

### F6 임상/효과 근거 (3수준)

| 수준 | 콘텐츠 |
|------|------|
| 임상 | "2024년 OO대학병원 RCT 임상시험: 4주 사용 후 골반저근 근력 평균 32% 향상 (n=120, p<0.01)" |
| 후기 | "사용자 후기: '한 달 사용 후 일상이 편해졌어요' — 30대 여성 외 200건" |
| 없음 | 근거 영역 자체 없음 |

## 3. 직교배열 → 36개 페이지 매핑

[methods/orthogonal_array_L36.md](orthogonal_array_L36.md) 표 사용. 각 행이 하나의 페이지.

예시 (실제는 pyDOE2로 생성):

| Page # | F1 | F2 | F3 | F4 | F5 | F6 |
|--------|----|----|----|----|----|----|
| 01 | TABLE | MedicalDevice | 정확 | 상단 | 풀 | 임상 |
| 02 | TABLE | Product | 부분 | 하단 | 인증완료 | 후기 |
| 03 | TABLE | 없음 | 모호 | 없음 | 없음 | 없음 |
| ... | ... | ... | ... | ... | ... | ... |
| 36 | PARAGRAPH | 없음 | 모호 | 하단 | 인증완료 | 후기 |

## 4. 파일 명명 규칙

```
experiments/synthetic_pages/
├── design_matrix.csv          ← 36개 조합 표 (page_id, F1~F6 수준)
├── page_001.html              ← 첫 조합
├── page_002.html
├── ...
├── page_036.html
└── _shared/
    ├── images/                ← 모든 페이지 공통 이미지 (제품 사진)
    ├── style.css              ← 공통 스타일
    └── product_metadata.json  ← 공통 제품 정보
```

## 5. Jinja2 템플릿 골격

```jinja
{# experiments/synthetic_pages/_template.html.j2 #}
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{{ product.name }}</title>
  
  {% if f2_jsonld != "none" %}
  <script type="application/ld+json">
  {{ jsonld_block(f2_jsonld, product) | tojson }}
  </script>
  {% endif %}
</head>
<body>
  
  {% if f4_position == "top" and f5_detail != "none" %}
    {{ cert_block(f5_detail, product) }}
  {% endif %}
  
  <h1>{{ product.name }}</h1>
  <img src="_shared/images/product.jpg">
  
  <section class="spec">
    {% if f1_format == "TABLE" %}
      {{ render_spec_table(product.spec, f3_numeric) }}
    {% elif f1_format == "BULLET" %}
      {{ render_spec_bullet(product.spec, f3_numeric) }}
    {% else %}
      {{ render_spec_paragraph(product.spec, f3_numeric) }}
    {% endif %}
  </section>
  
  {% if f6_evidence != "none" %}
    {{ evidence_block(f6_evidence) }}
  {% endif %}
  
  {% if f4_position == "bottom" and f5_detail != "none" %}
    {{ cert_block(f5_detail, product) }}
  {% endif %}
  
</body>
</html>
```

## 6. 검증 체크리스트 (페이지 1개 완료 시)

- [ ] HTML 유효 (W3C validator)
- [ ] JSON-LD 유효 (Schema.org validator)
- [ ] 6요인 수준이 의도대로 반영됐는지 시각 검수
- [ ] 텍스트 길이가 다른 페이지와 비슷한지 (요인 외 변동 통제)
- [ ] 이미지/스타일이 모두 공통 (변하는 건 6요인뿐)
- [ ] 페이지 ID와 design_matrix.csv 행이 일치

## 7. 검증 체크리스트 (전체 36개 완료 시)

- [ ] 36개 페이지 모두 생성됨
- [ ] 각 F 수준이 균등하게 등장 (직교성 확인)
- [ ] 페이지별 평균 텍스트 길이 ±20% 이내 (요인 외 통제)
- [ ] design_matrix.csv가 표준 L36 표와 일치
- [ ] _shared/ 자산이 모든 페이지에서 동일하게 참조됨

## 8. AI 실험에 어떻게 투입되나

각 본실험 호출은:
1. 가상 페이지 1개 + 경쟁사 5개 페이지(N=6) 또는 페이지 정보 요약을 시스템 프롬프트에 삽입
2. 쿼리 1개(Q1 4유형 중 하나)를 사용자 메시지로
3. 위 (페이지, 쿼리) 조합당 20회 반복 (R1)
4. 매 반복마다 페이지 순서 셔플 (R4)
5. Y1~Y4 응답 추출

**호출 수 = 36 × 4 × 20 × 1 = 2,880회**

## 9. 자주 막히는 곳

- **F1=PARAGRAPH일 때 동일 정보 전달**: 산문이라 정보 누락하기 쉬움. 정보 동등성 검증 필요
- **F3=정확 수준의 수치를 어디서 가져오나**: 우리 가상 제품이라 자유롭게 설정 가능. 단 의료기기로서 비현실적이지 않게 (50Hz, 99단계 등 시장 표준 따름)
- **F5=풀에 가짜 허가번호 쓰기**: 실제 번호 쓰면 윤리 문제. "제허XX-329호" 같이 마스킹 사용
- **F6=임상에 가짜 논문 인용**: "Test Corp 내부 임상 데이터" 같이 모호하게. 실제 논문 가짜 인용 금지

## 10. 참고

- [orthogonal_array_L36.md](orthogonal_array_L36.md)
- [PROJECT_MASTER.md §4.1](../../PROJECT_MASTER.md)
- Schema.org MedicalDevice: https://schema.org/MedicalDevice
- pyDOE2: https://pythonhosted.org/pyDOE2/
