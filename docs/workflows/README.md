# Workflows — 재사용 가능한 작업 템플릿

> 같은 작업을 두 번 이상 할 거라면 여기 템플릿화. 매번 처음부터 설명할 필요 X.
> Claude는 "워크플로우 X 실행해줘"만 받으면 됨.

---

## 사용법

```
사용자: "워크플로우 new_competitor.md대로 이지케이 추가해줘"
Claude: [템플릿 읽고 단계별 실행, 검증 체크리스트까지]
```

---

## 인덱스

| 워크플로우 | 언제 쓰나 | 예상 시간 |
|----------|----------|---------|
| [new_competitor.md](new_competitor.md) | 새 경쟁사 추가 | 30~60분 |
| [new_hypothesis.md](new_hypothesis.md) | 새 가설 추가/검정 | 60~90분 |
| [pilot_run.md](pilot_run.md) | 파일럿 실험 실행 | 2~3시간 + API 비용 |
| [weekly_digest_update.md](weekly_digest_update.md) | 매주 금요일 갱신 의식 | 30분 |

> 위 4개는 첫 번째 우선순위. 나머지(full_experiment, consulting_report, presentation_prep)는 해당 시점에 신설.

---

## 새 워크플로우 추가 규칙

각 워크플로우 파일은 다음 구조:

```markdown
# Workflow: <name>

**목적**: 한 줄
**언제 쓰나**: 트리거 조건
**예상 시간**: ~분/시간
**전제조건**: 이미 되어 있어야 할 것

## 단계
1. ...
2. ...

## 호출할 스킬/에이전트
- /investigate, Explore agent 등

## 검증 체크리스트
- [ ] ...
- [ ] ...

## 산출물 위치
- ...

## 갱신해야 할 다른 파일
- DIGEST.md, MEMORY.md 등
```

**원칙**: 워크플로우는 *복붙* 가능해야 한다. 모호한 단계 ("적절히 분석") 금지.
