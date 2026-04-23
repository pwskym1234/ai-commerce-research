# Knowledge Base — 프로젝트 위키

> 카파시 스타일의 "복리로 쌓이는 지식 레이어".
> 매 실험·조사·결정의 결과를 한 곳에 적층해서, 7주 후 한 권의 책처럼 읽힌다.
> 자세한 설계 배경: [docs/trends_2026/APPLICATION.md](../trends_2026/APPLICATION.md)

---

## 0. 어떻게 쓰나

- **항상 먼저 읽을 것**: [DIGEST.md](DIGEST.md) — 현재 상태 한눈에
- **용어 막힐 때**: [glossary.md](glossary.md)
- **특정 발견·경쟁사·방법 찾을 때**: 아래 디렉토리 grep

```
docs/knowledge/
├── README.md         ← 이 파일 (운영 규칙)
├── DIGEST.md         ★ 현재 상태 요약 (항상 최신, Ragless 핵심)
├── glossary.md       ← 도메인 용어 사전
├── findings/         ← 시간순 발견 누적 (F<date>_<title>.md)
├── competitors/      ← 경쟁사 프로필 (한 곳당 한 파일)
└── methods/          ← 통계/ML 방법 노트 + 재사용 템플릿
```

---

## 1. 무엇을 적나

| 레이어 | 들어가는 것 | 안 들어가는 것 |
|--------|-----------|--------------|
| `findings/` | 실험·분석·EDA에서 나온 *결론과 그 근거* | raw 데이터, 중간 코드 |
| `competitors/` | 경쟁 브랜드의 페이지 구조, F1~F6 기준 진단, 가격/리뷰 요약 | 전체 HTML 덤프 |
| `methods/` | "이 분석을 다시 할 때 따라할 절차" 템플릿 | 일회성 스크립트 |
| `DIGEST.md` | 모든 레이어의 *한 줄 요약*들이 모이는 컨트롤 룸 | 상세 본문 |
| `glossary.md` | 팀원/외부인이 모를 만한 용어의 한 줄 정의 | 흔한 통계/ML 용어 |

**❌ Knowledge에 안 넣는 것**:
- raw 크롤링 결과 → `data/raw/`
- API 응답 jsonl → `experiments/api_runs/`
- 코드 → `stats/scripts/`, `ml/scripts/`, `crawler/scripts/`
- 일정·로드맵 → `docs/PROJECT_MASTER.md`
- 의사결정 로그(ADR) → `docs/decisions/`

---

## 2. 파일 명명 규칙

| 디렉토리 | 패턴 | 예시 |
|---------|------|------|
| `findings/` | `F<YYYY-MM-DD>_<snake_title>.md` | `F2026-04-25_pilot_variance.md` |
| `competitors/` | `<brand_slug>.md` | `easyk.md`, `listerine.md` |
| `methods/` | `<topic_slug>.md` | `orthogonal_array_L18.md` |

날짜 prefix는 정렬용. 발견은 시간 순서가 의미 있다 (가설 진화 추적).

---

## 3. Frontmatter (필수)

특히 `findings/` 파일은 frontmatter로 메타데이터를 넣는다. 나중에 가설별·버티컬별 grep 가능.

```yaml
---
date: 2026-04-25
title: 파일럿 실험 변동성 측정 결과
related_findings: [F2026-04-15_query_design]
contradicts: []
supports: [H1, H4]      # 마스터 §4.4 가설 ID
vertical: medical_device  # medical_device | gargle | both | n_a
phase: pilot              # pilot | main | analysis | validation
author: Wayne
---
```

`competitors/` 파일은:
```yaml
---
brand: 이지케이
vertical: medical_device
last_updated: 2026-04-25
data_sources: [bodydoctor.co.kr, naver_smartstore]
f1_html_format: BULLET
f2_jsonld: none
f3_numeric: ambiguous
f4_cert_position: bottom
f5_cert_detail: minimal
f6_evidence: user_reviews
---
```

`methods/` 파일은:
```yaml
---
topic: 직교배열 L18 설계
when_to_use: 6요인 이내, 수준 ≤3
not_to_use: 4수준 이상 요인 多, 교호작용 모두 검정 필요
references: [docs/PROJECT_MASTER.md#4.1]
---
```

---

## 4. 갱신 의식 (매주 금요일 30분)

1. 이번 주 새 발견을 `findings/F<date>_<title>.md` 한 파일씩
2. 새로 알게 된 경쟁사 정보 `competitors/<brand>.md`에 추가/수정
3. 재사용할 만한 분석 절차는 `methods/`에
4. **`DIGEST.md` 갱신** — 새 발견 한 줄 추가, 기존 결론과 모순되면 Conflict 섹션에 표시
5. 메모리 영향 가는 사실(예: "직교배열은 L18로 확정")은 메모리 파일도 함께 갱신

위 5단계를 매주 한다. 한 번에 몰아서 X.

---

## 5. 모순 처리

새 발견이 기존 결론과 모순되면:
1. 새 finding 파일에 `contradicts: [F2026-04-15_xxx]` 명시
2. `DIGEST.md`의 "🔴 Active Conflicts" 섹션에 한 줄 추가
3. 다음 주 의식 때 둘 중 하나 결정 → 폐기된 finding은 `archive: true` frontmatter 추가 (삭제는 X, 추적성 보존)

---

## 6. 누가 책임?

| 영역 | 1차 담당 | 2차 검토 |
|------|---------|---------|
| `findings/` 산공통 | 산공통 팀원 | Wayne |
| `findings/` 데마 | 데마 팀원 | Wayne |
| `competitors/` 의료기기 | 데마 팀원 | Wayne |
| `competitors/` 가글 | 데마 팀원 | Wayne |
| `methods/` | 작성자 누구든 | Wayne |
| `DIGEST.md` 주간 갱신 | Wayne | — |

---

## 7. Claude에게 시킬 때

- "이번 주 발견을 finding 파일로 만들어줘 (frontmatter 포함, 마스터 §4.4의 H? 가설에 매핑)"
- "DIGEST.md 갱신해줘 — 어제 추가된 finding들 반영"
- "이지케이 경쟁사 페이지 진단해서 competitors/easyk.md 만들어줘 (F1~F6 기준)"
- "methods/ 보고 적용 가능한 템플릿 있나 — 새 분석 시작 전에 먼저 확인"
