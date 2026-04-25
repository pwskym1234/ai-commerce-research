"""
Phase B1 풀 실행 — 4개 명령(open/closed × 의료기기/가글) + Claude 파싱 통합.

전체 통합 budget 추적: 한 번의 명령으로 모든 단계 실행하면서 누적 비용 모니터링.
한도 도달 시 다음 단계 시작 안 함.

사용법:
  python ml/scripts/run_phase_b1_full.py --budget 10.0
  python ml/scripts/run_phase_b1_full.py --budget 10.0 --skip-claude
  python ml/scripts/run_phase_b1_full.py --pilot --budget 1.0
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))

# import as modules
import run_b1_async
import parse_responses_claude


COMBOS = [
    ("open", "medical_device"),
    ("closed", "medical_device"),
    ("open", "gargle"),
    ("closed", "gargle"),
]


async def run_b1(mode: str, vertical: str, n_repeat: int, budget_remaining: float):
    run_id = f"b1_{mode}_{vertical}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    summary = await run_b1_async.run_async(
        mode=mode, vertical=vertical, n_repeat=n_repeat,
        concurrency=20, use_cache=True, run_id=run_id,
        budget=budget_remaining,
    )
    return summary, run_id


async def run_claude_parse(run_id: str, budget_remaining: float):
    run_dir = REPO_ROOT / "ml" / "data" / "b1_runs" / run_id
    await parse_responses_claude.run_async(run_dir, budget=budget_remaining)


async def main_async(args):
    n_repeat = 5 if args.pilot else args.n_repeat
    total_budget = args.budget
    spent = 0.0
    run_ids = []

    print(f"🎯 Phase B1 풀 실행")
    print(f"   Total budget: ${total_budget:.2f}")
    print(f"   n_repeat: {n_repeat}, mode/vertical 4개")
    print(f"   Claude parsing: {'skip' if args.skip_claude else 'enabled'}")
    print()

    t0 = time.time()

    # Step 1~4: B1 4개 실행
    for i, (mode, vertical) in enumerate(COMBOS, start=1):
        remaining = max(total_budget - spent, 0.0)
        if remaining < 0.05:
            print(f"\n⛔ 잔여 예산 ${remaining:.4f} — Step {i} ({mode}/{vertical}) 스킵")
            break

        print(f"\n━━━ Step {i}/4: {mode} × {vertical} (잔여 ${remaining:.2f}) ━━━")
        summary, run_id = await run_b1(mode, vertical, n_repeat, remaining)
        spent += summary["total_cost_usd"]
        run_ids.append(run_id)
        print(f"   누적 ${spent:.4f} / ${total_budget:.2f}")

    # Step 5: Claude 파싱 (4개 run_dir에 대해)
    if not args.skip_claude:
        for i, run_id in enumerate(run_ids, start=1):
            remaining = max(total_budget - spent, 0.0)
            if remaining < 0.05:
                print(f"\n⛔ 잔여 ${remaining:.4f} — Claude parse {i}/{len(run_ids)} 스킵")
                break
            print(f"\n━━━ Claude parse {i}/{len(run_ids)}: {run_id} (잔여 ${remaining:.2f}) ━━━")
            await run_claude_parse(run_id, remaining)
            # parse_responses_claude 는 summary 파일에 비용 기록 — 거기서 합산
            summary_path = REPO_ROOT / "ml" / "data" / "b1_runs" / run_id / "parsed_claude_summary.json"
            if summary_path.exists():
                import json
                claude_summary = json.loads(summary_path.read_text())
                spent += claude_summary.get("total_cost_usd", 0.0)
                print(f"   누적 ${spent:.4f} / ${total_budget:.2f}")

    elapsed = time.time() - t0
    print(f"\n✅ Phase B1 완료")
    print(f"   총 소요: {elapsed:.0f}s ({elapsed/60:.1f}분)")
    print(f"   총 비용: ${spent:.4f} / 예산 ${total_budget:.2f}")
    print(f"   run_ids: {run_ids}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=float, default=10.0,
                   help="총 USD 예산 (모든 단계 합산, 도달 시 다음 단계 스킵)")
    p.add_argument("--n-repeat", type=int, default=20)
    p.add_argument("--pilot", action="store_true", help="5 반복 (검증용)")
    p.add_argument("--skip-claude", action="store_true", help="Claude 파싱 단계 스킵")
    args = p.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
