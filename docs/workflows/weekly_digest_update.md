# Workflow: 주간 갱신 의식 (매주 금요일 30분)

**목적**: 한 주의 발견·결정·진척을 지식베이스에 적층. 카파시 스타일 복리 효과의 핵심.
**언제 쓰나**: 매주 금요일. 안 빼먹기.
**예상 시간**: 30분.
**전제조건**: 그 주 작업 산출물 (커밋, 노트, 미팅 메모)이 어딘가에 있음.

---

## 단계

### 1. 그 주 변경사항 수집 (5분)
```bash
# 그 주 머지된 PR
gh pr list --search "merged:>=<지난주금요일>" --limit 50

# 그 주 커밋
git log --since="last friday" --oneline

# 그 주 추가된 메모/노트
ls -lt docs/meeting_notes/ | head -10
```

### 2. 새 발견을 finding 파일로 (15분)
각 의미 있는 발견에 대해 `docs/knowledge/findings/F<date>_<title>.md`:
- 한 페이지 이내. 짧게.
- frontmatter 필수 (date, supports/contradicts, vertical, phase)
- 근거: 어느 데이터·실험·분석에서 나왔는지 경로 명시

> "발견"의 기준: 다음 작업 의사결정에 영향을 주는 것. 단순 진척 ≠ 발견.

### 3. competitors/ 신규/갱신 (5분)
새 경쟁사 정보가 있으면 `competitors/<brand>.md` 추가/수정. (별도: workflow `new_competitor.md`)

### 4. methods/ 정착 (선택, 5분)
재사용할 분석 절차가 검증됐다면 `methods/`에 템플릿화.

### 5. DIGEST.md 갱신 (5분, 핵심)
- "마지막 갱신" 날짜 변경
- 핵심 수치 갱신 (가상 페이지 수, API 호출 수, SKU 수 등)
- 가설 상태 변경 (🟡 → 🟢/🔴)
- 경쟁사 진단 표 새 행
- "최근 발견" 섹션에 새 finding 한 줄씩 (최신 5개만 유지)
- 모순 발견 시 "Active Conflicts" 섹션 추가
- "다음 액션" 갱신

### 6. 메모리 동기화 (조건부)
세션 간 영구히 알아야 할 사실(예: "직교배열 L18 확정", "파일럿 변동성 σ=0.12")은 메모리 파일도 갱신:
```
~/.claude/.../memory/project_aieo.md
~/.claude/.../memory/feedback_research_design.md (필요 시)
```

---

## 호출할 스킬/에이전트

| 단계 | 도구 |
|------|------|
| 1 | Bash (gh, git) |
| 2 | 메인 (사람이 어떤 게 발견인지 판단) |
| 5 | 메인 + Edit |
| 6 | Memory write (Claude가 직접) |

`/retro` 스킬도 가능 — 자동 회고. 단, 출력이 길어서 컨텍스트 잡아먹으니 짧게 요청.

---

## 검증 체크리스트

- [ ] 새 finding 파일 frontmatter에 `supports`/`contradicts` 채워짐
- [ ] DIGEST.md "마지막 갱신" 날짜 = 오늘
- [ ] 가설 상태 ⚪/🟡/🟢/🔴 일관성
- [ ] 모순 발견 시 Active Conflicts 등록
- [ ] 메모리에 영향 가는 사실은 메모리도 갱신
- [ ] 다음 주 액션이 DIGEST에 명시됨

---

## 산출물

- `docs/knowledge/findings/F<date>_*.md` (이번 주 발견 수만큼)
- `docs/knowledge/DIGEST.md` (갱신본)
- (선택) `docs/knowledge/competitors/*.md`
- (선택) 메모리 갱신

---

## 30분 안 끝나면

- 한 주에 발견이 너무 많음 → 더 자주(주 2회) 의식 시도
- 의식이 자꾸 밀림 → DIGEST만이라도 갱신. findings는 다음 주에.
- 매주 빈 finding → 정말로 발견이 없거나, 발견을 인지하지 못하고 있음. 후자 의심.
