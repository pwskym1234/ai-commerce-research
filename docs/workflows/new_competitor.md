# Workflow: 새 경쟁사 추가

**목적**: 의료기기 또는 가글 버티컬에 새 경쟁 브랜드를 추가하고 F1~F6 기준으로 진단해서 지식베이스에 적층.
**언제 쓰나**: 1주차 경쟁사 조사, 또는 실험 중 새 경쟁사 발견 시.
**예상 시간**: 30~60분 / 브랜드.
**전제조건**:
- 브랜드명, 공식 URL 또는 판매 페이지 URL 1개 이상
- `crawler/scripts/`에 해당 사이트(예: 네이버 스마트스토어, 쿠팡)용 크롤러 존재 (없으면 먼저 작성)

---

## 단계

### 1. 브랜드 메타 수집
- 공식 사이트, 판매 채널 URL 정리
- 버티컬 결정: medical_device | gargle
- 1차 추정: 가격대, 인지도

### 2. 페이지 크롤링
- `crawler/scripts/<site>.py` 실행 → `crawler/output/<brand>_<date>.html`
- 검증 통과 시 `data/raw/<vertical>/<brand>/` 로 이동
- ⚠️ raw는 절대 수정 금지 (CLAUDE.md §8)

### 3. 피처 추출 (F1~F6 진단)
| 요인 | 방법 |
|------|------|
| F1 HTML 포맷 | 스펙 영역 DOM 분석 — TABLE/UL/P 비율 |
| F2 JSON-LD | `<script type="application/ld+json">` 파싱, @type 확인 |
| F3 수치 구체성 | 정규식 + LLM 보조 — 정확 수치 vs 모호 표현 비율 |
| F4 인증 위치 | "식약처/FDA/인증" 키워드 위치 (상단/하단/없음) |
| F5 인증 상세 | 인증번호+기관+등급 모두? "인증완료"만? 없음? |
| F6 임상/근거 | "임상", "연구", "사용자 후기" 패턴 분류 |

### 4. 경쟁사 프로필 작성
- `docs/knowledge/competitors/<brand_slug>.md` 신설
- frontmatter 필수 (`docs/knowledge/README.md §3` 참조):
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
- 본문: 각 요인별 1~2문단 근거 + 스크린샷/링크

### 5. DIGEST.md 갱신
- 경쟁사 진단 표에 행 추가
- "최근 발견" 섹션에 한 줄: "F2026-04-25: 이지케이 추가 — F4=하단, F5=minimal"

---

## 호출할 스킬/에이전트

| 단계 | 도구 |
|------|------|
| 2 (크롤링) | `/browse` 또는 `/gstack` (JS 페이지 시) / `crawler/scripts/` 직접 실행 |
| 3 (피처 추출) | Explore agent로 페이지 구조 분석 위임 가능 (메인 컨텍스트 보호) |
| 1, 4, 5 | 메인 직접 |

---

## 검증 체크리스트

- [ ] raw HTML이 `data/raw/<vertical>/<brand>/` 에 저장됨
- [ ] `competitors/<brand_slug>.md` frontmatter 6개 필드 모두 채워짐
- [ ] 추측인 항목은 본문에 "추정" 명시
- [ ] DIGEST.md의 진단 표 + 최근 발견 섹션 갱신
- [ ] 같은 사이트 추가 크롤링 시 robots.txt 준수 확인
- [ ] 시그니처/단가 등 *영업적으로 민감한 정보*는 평가 후 포함/제외 결정 (Public 레포)

---

## 산출물 위치

- 원본: `data/raw/<vertical>/<brand>/`
- 진단: `docs/knowledge/competitors/<brand_slug>.md`
- DIGEST 갱신: `docs/knowledge/DIGEST.md`

---

## 갱신해야 할 다른 파일

- `DIGEST.md` (경쟁사 진단 표 + 최근 발견)
- 의료기기/가글 경쟁사 리스트가 마스터 §10 미확정 사항이면 `PROJECT_MASTER.md` §10 체크 갱신

---

## 자주 막히는 곳

- **JS 렌더링 페이지**: `requests`로 빈 결과 → `playwright` 사용
- **네이버 스마트스토어**: 로그인/지역 차단 → User-Agent + 세션 쿠키 필요
- **JSON-LD가 동적 삽입**: 정적 HTML에선 안 보임. 헤드리스 브라우저 후 평가
