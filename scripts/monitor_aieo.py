#!/usr/bin/env python3
"""주간 AiEO 가시성 모니터링 — 본실험 별개 트랙.

목표: 바디닥터(의료기기) + 프로폴린스(가글) anchor 브랜드의 AI 추천률 시계열 추적.
참고: Profound/Otterly가 매일 자동화하는 기능을 가벼게(주간 1회) 자체 구현.

설계 결정 (2026-04-30):
- 빈도: 매주 월요일 03:00 (KST)
- LLM: gpt-5.4-mini 단일 (메인 비용 효율). 추가는 LLMS 리스트 확장만 하면 됨
- 쿼리: 4 유형(BRD/CAT/CMP/USE) × 1개씩 = 8 쿼리 (본실험 queries_*.yaml 차용)
- 반복: 7회/쿼리 (Wilson CI 적당)
- 비용: ~$0.05/주 (gpt-5.4-mini, 56 호출)
- 저장: experiments/monitoring/<run_id>/responses.jsonl + history.csv 시계열

본실험과 의도적으로 다른 점:
- R1 적용 안 함 — 이건 본실험 룰. 모니터링은 별도 트랙임을 명시
- 쿼리 수 적음 — trend 추적 목적이지 통계 power 목적 아님
- 단일 모델 — our brand 시계열 추적이지 모델 비교 아님
- 결과 통계 분석 X — history.csv를 보고 변화량만 확인

실행 (수동): python scripts/monitor_aieo.py
실행 (자동): launchd plist (scripts/com.aieo.monitor.plist) 설치 — 아직 미실행
멱등성: 같은 ISO 주(YYYY-Www)에 두 번 실행 시 skip (--force로 우회)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# .env 로드
for line in (ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

OUT_DIR = ROOT / "experiments" / "monitoring"
OUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_CSV = OUT_DIR / "history.csv"

MODEL = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4-mini")
N_REPS = 7
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))
SYSTEM_PROMPT = "한국어로 답변해주세요."

# 쿼리 (본실험 queries_*.yaml에서 4 유형 1개씩 차용 — 모니터링 가벼움 목적)
QUERIES = {
    "bodydoctor": {
        "BRD": "바디닥터 요실금치료기 어때요?",
        "CAT": "요실금치료기 추천해줘",
        "CMP": "바디닥터 vs 이지케이 비교해줘",
        "USE": "출산 후 골반저근 회복하려면 어떻게 해야 해?",
    },
    "propolinse": {
        "BRD": "프로폴린스 가글 어때요?",
        "CAT": "구강청결제 추천해줘",
        "CMP": "프로폴린스 vs 리스테린 비교해줘",
        "USE": "잇몸 관리하려면 어떤 가글 쓰는 게 좋아?",
    },
}

# 매칭 패턴 (anchor brand mention 감지)
MENTION_PATTERNS = {
    "bodydoctor": [r"바디닥터", r"BodyDoctor", r"Body Doctor"],
    "propolinse": [r"프로폴린스", r"Propolinse"],
}


def iso_week_id() -> str:
    today = datetime.now(timezone.utc).date()
    iso = today.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def already_run_this_week(week: str) -> bool:
    if not HISTORY_CSV.exists():
        return False
    with HISTORY_CSV.open("r") as f:
        return any(row.get("week") == week for row in csv.DictReader(f))


def call_openai(query: str, seed: int) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            seed=seed,
        )
        return {
            "ok": True,
            "text": resp.choices[0].message.content or "",
            "usage": resp.usage.model_dump() if resp.usage else {},
            "latency_s": round(time.time() - t0, 3),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "latency_s": round(time.time() - t0, 3)}


def detect_mention(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def run_brand(brand_id: str) -> dict:
    queries = QUERIES[brand_id]
    patterns = MENTION_PATTERNS[brand_id]
    week = iso_week_id()
    run_id = f"{week}_{brand_id}_{datetime.now().strftime('%H%M%S')}"
    run_dir = OUT_DIR / run_id
    run_dir.mkdir(exist_ok=True)
    jsonl_path = run_dir / "responses.jsonl"

    summary: dict = {qtype: {"hits": 0, "total": 0} for qtype in queries}

    with jsonl_path.open("w") as f:
        for qtype, qtext in queries.items():
            for i in range(N_REPS):
                seed = SEED_BASE + i + (hash(qtype) & 0xFFFF)
                resp = call_openai(qtext, seed)
                hit = resp.get("ok", False) and detect_mention(resp.get("text", ""), patterns)
                summary[qtype]["total"] += 1
                if hit:
                    summary[qtype]["hits"] += 1
                line = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "week": week,
                    "brand": brand_id,
                    "qtype": qtype,
                    "qtext": qtext,
                    "rep": i,
                    "seed": seed,
                    "model": MODEL,
                    "hit": hit,
                    **resp,
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    return {"week": week, "brand": brand_id, "run_id": run_id, "summary": summary}


def append_history(rows: list[dict]) -> None:
    cols = ["week", "brand", "qtype", "hits", "total", "rate", "run_id", "model"]
    write_header = not HISTORY_CSV.exists()
    with HISTORY_CSV.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if write_header:
            w.writeheader()
        for r in rows:
            for qtype, c in r["summary"].items():
                rate = c["hits"] / c["total"] if c["total"] else 0.0
                w.writerow({
                    "week": r["week"], "brand": r["brand"], "qtype": qtype,
                    "hits": c["hits"], "total": c["total"],
                    "rate": f"{rate:.3f}",
                    "run_id": r["run_id"], "model": MODEL,
                })


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="이번 주 이미 돌렸어도 다시 실행")
    p.add_argument("--brand", choices=["bodydoctor", "propolinse", "all"], default="all")
    args = p.parse_args()

    week = iso_week_id()
    if not args.force and already_run_this_week(week):
        print(f"[monitor] {week} 이미 실행됨 — skip (--force로 재실행)", file=sys.stderr)
        return 0

    if not os.environ.get("OPENAI_API_KEY"):
        print("[monitor] OPENAI_API_KEY 없음 — abort", file=sys.stderr)
        return 1

    print(f"[monitor] week={week}, model={MODEL}, reps={N_REPS}/query")

    brands = ["bodydoctor", "propolinse"] if args.brand == "all" else [args.brand]
    rows = [run_brand(b) for b in brands]
    append_history(rows)

    print(f"\n[monitor] 완료 → {HISTORY_CSV}")
    for r in rows:
        print(f"  {r['brand']}:")
        for qtype, c in r["summary"].items():
            rate = c["hits"] / c["total"] if c["total"] else 0
            print(f"    {qtype}: {c['hits']}/{c['total']} = {rate:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
