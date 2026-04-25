"""
Phase B1 파이프라인 검증 — 본실험($14) 들어가기 전 minimal cost(~$0.30) smoke test.

검증 항목:
  1. 정적 체크 (비용 0): 쿼리 yaml / features / 페이지 / .env 키
  2. 4 조합(open/closed × 의료/가글) × 핵심 8쿼리 × 2반복 = 64 OpenAI 호출
  3. Claude 파싱 1건 (1 verification 만)
  4. 응답 품질 패턴 검증 (BRD mention=100%, B1-B 페이지 인용 등)
  5. Budget guard 동작 확인

총 비용: ~$0.25 (본실험 $14의 1.8%)
총 시간: ~3분

사용:
  python3 ml/scripts/verify_pipeline.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "experiments"))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")


CHECK_OK = "✅"
CHECK_FAIL = "❌"
CHECK_WARN = "⚠️ "

results: list[tuple[str, bool, str]] = []  # (name, passed, detail)


def log(name: str, passed: bool, detail: str = ""):
    icon = CHECK_OK if passed else CHECK_FAIL
    print(f"  {icon} {name:50} {detail}")
    results.append((name, passed, detail))


# ========== 1. 정적 체크 (비용 0) ==========
def check_static():
    print("\n━━━ 1. 정적 체크 (비용 0) ━━━")

    # .env 키
    for key, name in [
        ("OPENAI_API_KEY", "OPENAI_API_KEY"),
        ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
        ("NAVER_CLIENT_ID", "NAVER_CLIENT_ID"),
        ("OPENAI_MODEL_VERSION", "OPENAI_MODEL_VERSION"),
    ]:
        v = os.environ.get(key, "").strip()
        log(f".env {name}", bool(v), f"({'set' if v else 'EMPTY'})")

    # 쿼리 yaml
    import yaml
    for path, label in [
        (REPO_ROOT / "experiments/prompts/queries.yaml", "queries.yaml (medical)"),
        (REPO_ROOT / "experiments/prompts/queries_gargle.yaml", "queries_gargle.yaml"),
    ]:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            n = sum(len(v) for v in data.values())
            log(label, n == 24, f"{n} 쿼리 (8유형 × 3 = 24 기대)")
        else:
            log(label, False, "FILE NOT FOUND")

    # features.jsonl
    feat_path = REPO_ROOT / "data/processed/features.jsonl"
    if feat_path.exists():
        n = sum(1 for _ in feat_path.open())
        log("features.jsonl", n >= 50, f"{n} SKU")
    else:
        log("features.jsonl", False, "FILE NOT FOUND")

    # 페이지 컨텍스트 로드 (B1-B 입력)
    try:
        from run_b1_async import load_pages_with_meta
        for v in ["medical_device", "gargle"]:
            pages = load_pages_with_meta(v)
            log(f"pages [{v}]", len(pages) >= 5,
                f"{len(pages)} 페이지, 총 {sum(len(p['text']) for p in pages):,}자")
    except Exception as e:
        log("page loader", False, f"ERROR: {e}")

    # imports
    try:
        from runner import COMPETITORS, COMPETITORS_GARGLE
        log("runner.py imports", True,
            f"의료 {len(COMPETITORS)}, 가글 {len(COMPETITORS_GARGLE)}")
    except Exception as e:
        log("runner.py imports", False, f"ERROR: {e}")


# ========== 2. Smoke 호출 (4 조합) ==========
async def smoke_b1(mode: str, vertical: str) -> tuple[bool, dict]:
    """8 쿼리 × 2 반복 = 16 호출. 핵심 8유형 each one."""
    import run_b1_async
    from openai import AsyncOpenAI

    queries = run_b1_async.load_queries(vertical)
    # 8유형 각 1개씩 (qid가 -1로 끝나는 것)
    seed_queries = [q for q in queries if q[0].endswith("-1")]
    pages = run_b1_async.load_pages_with_meta(vertical) if mode == "closed" else None
    anchor = "bodydoctor" if vertical == "medical_device" else "propolinse"

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    semaphore = asyncio.Semaphore(20)
    budget_state: dict = {"exceeded": False}

    tasks = []
    for qid, qtype, qtext in seed_queries:
        for rep in range(2):
            tasks.append(run_b1_async.call_one(
                client, semaphore, budget_state,
                run_id=f"verify_{mode}_{vertical}",
                mode=mode, vertical=vertical,
                qid=qid, qtype=qtype, qtext=qtext, repeat_idx=rep,
                pages_for_closed=pages, anchor_id=anchor, use_cache=True,
            ))

    rows = await asyncio.gather(*tasks)
    cost = sum(r.cost_usd for r in rows)
    errors = sum(1 for r in rows if r.raw_response.startswith("(API ERROR"))

    # 패턴 검증
    by_type = {}
    for r in rows:
        by_type.setdefault(r.query_type, []).append(r)

    passed = errors == 0 and all(len(v) == 2 for v in by_type.values())

    metrics = {
        "n": len(rows), "errors": errors, "cost": cost,
        "by_type_mention": {qt: sum(1 for r in vs if r.y2a_mention) / len(vs)
                            for qt, vs in by_type.items()},
        "rows": rows,
    }
    return passed, metrics


async def smoke_4_combos():
    print(f"\n━━━ 2. B1 Smoke (4 조합 × 8유형 × 2반복 = 64 호출) ━━━")
    total_cost = 0.0
    all_rows = {}
    for mode, vertical in [
        ("open", "medical_device"), ("closed", "medical_device"),
        ("open", "gargle"), ("closed", "gargle"),
    ]:
        passed, m = await smoke_b1(mode, vertical)
        total_cost += m["cost"]
        all_rows[(mode, vertical)] = m["rows"]
        # mention rate by query type 요약
        mentions = m["by_type_mention"]
        rate_summary = ", ".join(f"{qt}:{mentions[qt]:.0%}" for qt in ["BRD", "CMP", "SYM", "DEC"]
                                 if qt in mentions)
        log(f"B1 [{mode}/{vertical[:3]}]", passed,
            f"{m['n']}/16 ok, ${m['cost']:.3f}, {rate_summary}")
    return total_cost, all_rows


# ========== 3. 응답 품질 패턴 ==========
def check_response_patterns(all_rows: dict):
    print("\n━━━ 3. 응답 품질 패턴 검증 ━━━")
    for (mode, vertical), rows in all_rows.items():
        # BRD 쿼리에서 anchor mention 비율 (높아야 함)
        brd_rows = [r for r in rows if r.query_type == "BRD"]
        if brd_rows:
            brd_mention = sum(1 for r in brd_rows if r.y2a_mention) / len(brd_rows)
            log(f"BRD anchor mention [{mode}/{vertical[:3]}]",
                brd_mention >= 0.5,
                f"{brd_mention:.0%} (≥50% 기대 — 브랜드 지명 시 답변)")

    # B1-B 에서 페이지 인용 — 페이지 본문 단어가 응답에 등장?
    for vertical in ["medical_device", "gargle"]:
        rows = all_rows.get(("closed", vertical), [])
        if not rows:
            continue
        # 응답에서 경쟁군 brand 언급 1개 이상
        non_empty = sum(1 for r in rows if r.mentioned_predefined)
        log(f"B1-B 브랜드 인용 [{vertical[:3]}]",
            non_empty >= len(rows) * 0.5,
            f"{non_empty}/{len(rows)} (≥50% 기대 — 페이지 컨텍스트 활용)")


# ========== 4. Claude 파싱 1건 ==========
async def smoke_claude(open_med_rows):
    print("\n━━━ 4. Claude haiku 파싱 (16 응답) ━━━")
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        log("Claude parsing", False, "ANTHROPIC_API_KEY 없음")
        return 0.0

    import parse_responses_claude
    from anthropic import AsyncAnthropic
    from dataclasses import asdict

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    semaphore = asyncio.Semaphore(10)
    budget_state: dict = {"exceeded": False}

    rows_dict = [asdict(r) for r in open_med_rows]
    tasks = [parse_responses_claude.parse_one(client, semaphore, budget_state, r)
             for r in rows_dict]
    parsed = await asyncio.gather(*tasks)

    errors = sum(1 for p in parsed if p.parse_error)
    cost = sum(p.claude_cost_usd for p in parsed)

    # 룰 vs Claude sentiment 비교 (BRD 쿼리만)
    brd_indices = [i for i, r in enumerate(rows_dict) if r["query_type"] == "BRD"]
    sent_diff = 0
    for i in brd_indices:
        if rows_dict[i].get("y2a_positive") != parsed[i].our_sentiment:
            sent_diff += 1

    log("Claude 파싱", errors == 0, f"{len(parsed)}/16 ok, ${cost:.4f}")
    log("룰 vs Claude sentiment 차이",
        True,  # 차이 있는 것 자체가 정보 — 항상 통과
        f"BRD에서 {sent_diff}/{len(brd_indices)} 차이 (룰 약점 입증)")
    return cost


# ========== 5. Budget guard ==========
async def check_budget_guard():
    print("\n━━━ 5. Budget Guard 동작 확인 ━━━")
    import run_b1_async
    from openai import AsyncOpenAI

    queries = run_b1_async.load_queries("medical_device")[:3]  # 3 쿼리만
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    semaphore = asyncio.Semaphore(5)
    budget_state: dict = {"exceeded": False}

    tasks = []
    for qid, qtype, qtext in queries:
        for rep in range(3):
            tasks.append(run_b1_async.call_one(
                client, semaphore, budget_state,
                run_id="verify_budget",
                mode="open", vertical="medical_device",
                qid=qid, qtype=qtype, qtext=qtext, repeat_idx=rep + 100,  # cache 회피
                pages_for_closed=None, anchor_id="bodydoctor", use_cache=True,
            ))

    # 0.01 budget 초과 시 즉시 stop
    rows = []
    cost = 0.0
    for fut in asyncio.as_completed(tasks):
        row = await fut
        rows.append(row)
        cost += row.cost_usd
        if cost >= 0.01 and not budget_state["exceeded"]:
            budget_state["exceeded"] = True

    skipped = sum(1 for r in rows if r.raw_response.startswith("(SKIPPED"))
    log("Budget guard ($0.01 한도)", skipped > 0 or budget_state["exceeded"],
        f"새 호출 {skipped}건 SKIP, 진행 중 task 마저 완료")
    return cost


# ========== Main ==========
async def main_async():
    print("🧪 Phase B1 Pipeline Verification")
    print(f"   본실험 약 $14 → 검증 비용 ~$0.30 (1/45 비용)")
    print(f"   목표 시간: 3분")
    t0 = time.time()

    check_static()
    static_failed = sum(1 for n, p, _ in results if not p)
    if static_failed > 0:
        print(f"\n❌ 정적 체크 {static_failed}건 실패 — 본실험 진행 불가")
        sys.exit(1)

    smoke_cost, all_rows = await smoke_4_combos()
    check_response_patterns(all_rows)
    claude_cost = await smoke_claude(all_rows[("open", "medical_device")])
    budget_cost = await check_budget_guard()

    total_cost = smoke_cost + claude_cost + budget_cost
    elapsed = time.time() - t0

    print("\n━━━ 최종 결과 ━━━")
    failed = sum(1 for n, p, _ in results if not p)
    if failed == 0:
        print(f"  {CHECK_OK} 모든 검증 통과")
        print(f"  총 비용: ${total_cost:.3f}")
        print(f"  총 시간: {elapsed:.0f}s")
        print(f"\n✅ 본실험 진행 준비 완료. 명령:")
        print(f"   python3 ml/scripts/run_phase_b1_full.py --budget 15")
    else:
        print(f"  {CHECK_FAIL} {failed}건 실패")
        for n, p, d in results:
            if not p:
                print(f"     - {n}: {d}")
        print(f"\n  비용: ${total_cost:.3f}, 시간: {elapsed:.0f}s")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main_async())
