"""
응답 검수 CLI — responses.jsonl을 사람이 읽기 좋게 출력.

사용 예:
    # 무작위 5개
    python experiments/inspect_responses.py <run_dir> --random 5

    # 특정 쿼리만
    python experiments/inspect_responses.py <run_dir> --query BRD-1

    # 특정 페이지만
    python experiments/inspect_responses.py <run_dir> --page page_001

    # 자동 플래그된 것만 (짧은 응답·회피만 등)
    python experiments/inspect_responses.py <run_dir> --flagged

    # 키워드 grep
    python experiments/inspect_responses.py <run_dir> --grep "바디닥터"

    # 우리 안 언급된 응답만 (왜 안 잡혔는지 확인)
    python experiments/inspect_responses.py <run_dir> --no-our

    # 특정 response_id (CSV에서 본 셀의 jsonl 역참조)
    python experiments/inspect_responses.py <run_dir> --id <uuid>
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path


def load_jsonl(p: Path) -> list[dict]:
    out = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def fmt_one(r: dict, full: bool = False) -> str:
    sep = "─" * 70
    head = (
        f"\n{sep}\n"
        f"[{r.get('query_id')}] {r.get('query_text','')}\n"
        f"page={r.get('page_id')}  rep={r.get('repeat_idx')}  "
        f"seed={r.get('seed')}  model={r.get('model_version')}  "
        f"persona={r.get('persona_id')}\n"
        f"response_id={r.get('response_id','')[:8]}…  "
        f"length={r.get('response_length',0)}자  "
        f"cache_hit={r.get('from_cache')}\n"
    )

    flags = []
    if r.get("y2a_our_selected"):
        flags.append("✅우리언급")
    else:
        flags.append("❌우리없음")
    if r.get("y4_safety_avoidance"):
        flags.append("⚠️회피있음")
    if r.get("y2a_wintieloss"):
        flags.append(f"CMP={r['y2a_wintieloss']}")
    mentioned = r.get("y2a_mentioned_brand_ids") or []
    if mentioned:
        flags.append(f"언급={'/'.join(mentioned)}")
    other = r.get("other_brands_detected") or []
    if other:
        flags.append(f"외부={'/'.join(other[:3])}")

    head += "  ".join(flags)

    raw = r.get("raw_response", "")
    if not full and len(raw) > 600:
        raw = raw[:600] + f"…\n  [+{len(raw)-600}자 — --full 로 전체 보기]"

    return head + "\n\n" + raw + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", help="experiments/api_runs/<run_id>/")
    p.add_argument("--random", type=int, metavar="N", help="무작위 N개")
    p.add_argument("--query", help="특정 query_id (예: BRD-1)")
    p.add_argument("--qtype", help="특정 query_type (예: BRD)")
    p.add_argument("--page", help="특정 page_id")
    p.add_argument("--id", dest="response_id", help="특정 response_id")
    p.add_argument("--grep", help="raw_response 키워드 검색")
    p.add_argument("--flagged", action="store_true",
                   help="자동 플래그된 것 (짧은 응답·회피만 등)")
    p.add_argument("--no-our", action="store_true",
                   help="우리(바디닥터/프로폴린스) 언급 안 된 응답만")
    p.add_argument("--full", action="store_true", help="응답 전체 출력 (기본 600자 truncate)")
    p.add_argument("--limit", type=int, default=20, help="최대 출력 개수 (기본 20)")
    p.add_argument("--count-only", action="store_true", help="개수만 출력")
    args = p.parse_args()

    run_dir = Path(args.run_dir)
    jsonl = run_dir / "responses.jsonl"
    if not jsonl.exists():
        sys.exit(f"❌ {jsonl} 없음")

    rows = load_jsonl(jsonl)
    print(f"📂 {jsonl} — 총 {len(rows):,}건 로드", file=sys.stderr)

    # 필터 체인
    if args.query:
        rows = [r for r in rows if r.get("query_id") == args.query]
    if args.qtype:
        rows = [r for r in rows if r.get("query_type") == args.qtype]
    if args.page:
        rows = [r for r in rows if r.get("page_id") == args.page]
    if args.response_id:
        rows = [r for r in rows if r.get("response_id", "").startswith(args.response_id)]
    if args.grep:
        pat = re.compile(args.grep, re.IGNORECASE)
        rows = [r for r in rows if pat.search(r.get("raw_response", ""))]
    if args.flagged:
        rows = [
            r for r in rows
            if r.get("response_length", 0) < 100
            or (r.get("y4_safety_avoidance") and not (r.get("y2a_mentioned_brand_ids") or []))
            or len(r.get("y2a_mentioned_brand_ids") or []) == 0
        ]
    if args.no_our:
        rows = [r for r in rows if not r.get("y2a_our_selected")]

    print(f"🔍 필터 후 {len(rows):,}건", file=sys.stderr)
    if args.count_only:
        return

    # 샘플링
    if args.random and args.random < len(rows):
        rows = random.sample(rows, args.random)

    rows = rows[: args.limit]
    for r in rows:
        print(fmt_one(r, full=args.full))


if __name__ == "__main__":
    main()
