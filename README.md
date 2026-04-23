# AiEO 프로젝트

> AI 에이전트가 상품을 추천할 때, 상품 페이지의 어떤 요소가 추천에 영향을 미치는가?

산업공학통계 + 데이터마이닝 두 과목의 팀 프로젝트를 AiEO(AI Engine Optimization) 연구 파이프라인으로 통합 진행하는 레포.
실제 고객사: GN그룹/바디닥터.

---

## 빠른 시작

1. **무엇을 하는 프로젝트인지** → [docs/PROJECT_MASTER.md](docs/PROJECT_MASTER.md) 먼저 읽기 (필독)
2. **어떻게 작업해야 하는지** → [CLAUDE.md](CLAUDE.md) (Claude/팀원 공통 작업 가이드)
3. **AI 도구 활용** → [docs/AGENTS_AND_SKILLS.md](docs/AGENTS_AND_SKILLS.md)

---

## 디렉토리 구조

```
docs/         프로젝트 마스터 문서, 의사결정 기록, 회의록
data/         크롤링 원본(raw) + 정제본(processed)
experiments/  가상 페이지(synthetic_pages), 프롬프트, API 실험 결과
crawler/      사이트별 크롤러
stats/        산업공학통계 영역 (가설검정, 로지스틱 회귀)
ml/           데이터마이닝 영역 (XGBoost, SHAP)
consulting/   바디닥터K 진단/컨설팅 산출물
presentations/  수업별 발표자료
```

자세한 규칙은 [CLAUDE.md §2](CLAUDE.md)와 [§8 데이터/시크릿 관리](CLAUDE.md) 참조.

---

## 팀

- **Wayne (방우식)**: 양쪽 조율 + 실험 설계 + 컨설팅 연결
- **산공통 팀 3명**: 통제 실험 → 인과 추론
- **데마 팀 3명**: 실제 크롤링 → 예측 모델링

---

## 환경 설정

```bash
# Python 3.11+
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# .env 생성 (API 키)
cp .env.example .env
# OPENAI_API_KEY, GOOGLE_API_KEY 등 입력
```

---

## 7주 로드맵 (요약)

| 주차 | 산공통 | 데마 |
|------|--------|------|
| 1 | 경쟁사 조사 + 요인 확정 | 크롤링 시작 |
| 2 | 가상 페이지 18~36개 제작 | 크롤링 완료 + EDA |
| 3 | 파일럿 실험 | 가설 탐색 |
| 4 | 본실험 (15~20회 반복) | API 실험 + Y변수 생성 |
| 5 | 가설검정 + 로지스틱 회귀 | XGBoost + SHAP |
| 6 | 바디닥터K 실제 검증 | 바디닥터K 진단 리포트 |
| 7 | 발표 준비 | 발표 + 컨설팅 산출물 |

---

## 기여

PR 단위는 한 가지 일만. 영역 prefix 사용 (`[stats]`, `[ml]`, `[crawler]`, `[consulting]`, `[docs]`).
자세한 규칙은 [CLAUDE.md §11 팀 협업 규칙](CLAUDE.md) 참조.
