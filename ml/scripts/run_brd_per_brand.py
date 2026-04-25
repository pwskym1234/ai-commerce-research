"""
BRD per-brand 호출 — 모든 경쟁군 브랜드 × 1쿼리 × 20반복.

목적 (Wayne 통찰 2026-04-25):
  · 기존 BRD: anchor 1개 × 3변형 = 단순 baseline. 데마 X 변수로 무가치.
  · 신규 BRD per-brand: 25 브랜드 × 1쿼리 × 20반복 = 500 호출
  · 결과 → brand-level "AI prior 인지 강도" X 변수 추출:
    - sentiment (positive/neutral/negative)
    - mentioned_attributes (효능·기능 키워드)
    - co_mentioned_brands (같이 거론되는 브랜드들)
    - confidence (Claude 파싱 확신도)
    - safety_avoidance_rate
  · 이 brand-level X를 페이지 X와 join → AI prior 통제 후 페이지 X 순효과 측정

비용: ~$0.5 (gpt-5.4-mini, 500 호출), 5분.

사용:
  python ml/scripts/run_brd_per_brand.py --budget 1.5
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

sys.path.insert(0, str(REPO_ROOT / "experiments"))
from runner import COMPETITORS, COMPETITORS_GARGLE

MODEL_VERSION = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4-mini").strip()
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))

CACHE_DIR = REPO_ROOT / "experiments" / "api_runs" / "_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = REPO_ROOT / "ml" / "data" / "b1_runs"

SYSTEM_PROMPT = "한국어로 답변해주세요."

# vertical별 BRD 쿼리 템플릿 — 일관성 위해 동일 형식
QUERY_TEMPLATES = {
    "medical_device": "{name} 어떤 제품인가요? 효과 있는지, 써본 후기랑 평가 알려주세요.",
    "gargle": "{name} 어떤가요? 효과 있는지, 써본 후기랑 평가 알려주세요.",
}

PRICES = {"gpt-5.4": (2.5, 15.0), "gpt-5.4-mini": (0.75, 4.5), "gpt-5.4-nano": (0.2, 1.25)}


@dataclass
class BrdRow:
    run_id: str
    brand_id: str
    brand_name: str
    vertical: str
    query_text: str
    repeat_idx: int
    seed: int
    model_version: str
    raw_response: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: str
    from_cache: bool


def cache_key(model: str, system: str, user: str, seed: int) -> str:
    h = hashlib.sha256()
    h.update(f"{model}||{system}||{user}||{seed}||None".encode("utf-8"))
    return h.hexdigest()[:24]


def load_cache(key: str) -> Optional[dict]:
    p = CACHE_DIR / f"{key}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save_cache(key: str, data: dict) -> None:
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def all_brands() -> list[dict]:
    """COMPETITORS + COMPETITORS_GARGLE 통합 (vertical 표기)."""
    out = []
    for c in COMPETITORS:
        out.append({**c, "vertical": "medical_device"})
    for c in COMPETITORS_GARGLE:
        out.append({**c, "vertical": "gargle"})
    return out


async def call_one(client: AsyncOpenAI, semaphore: asyncio.Semaphore, budget_state: dict,
                   *, run_id: str, brand: dict, repeat_idx: int) -> BrdRow:
    seed = SEED_BASE + repeat_idx
    template = QUERY_TEMPLATES[brand["vertical"]]
    user_prompt = template.format(name=brand["name"])

    key = cache_key(MODEL_VERSION, SYSTEM_PROMPT, user_prompt, seed)
    cached = load_cache(key)
    from_cache = cached is not None

    if cached:
        raw = cached["raw_response"]
        tokens_in = cached.get("tokens_in", 0)
        tokens_out = cached.get("tokens_out", 0)
    elif budget_state.get("exceeded"):
        raw = "(SKIPPED: budget)"
        tokens_in = tokens_out = 0
    else:
        async with semaphore:
            if budget_state.get("exceeded"):
                raw = "(SKIPPED: budget)"
                tokens_in = tokens_out = 0
            else:
                try:
                    r = await client.chat.completions.create(
                        model=MODEL_VERSION,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                    )
                    raw = r.choices[0].message.content or ""
                    tokens_in = r.usage.prompt_tokens if r.usage else 0
                    tokens_out = r.usage.completion_tokens if r.usage else 0
                    save_cache(key, {"raw_response": raw, "tokens_in": tokens_in,
                                     "tokens_out": tokens_out})
                except Exception as e:
                    raw = f"(API ERROR: {type(e).__name__})"
                    tokens_in = tokens_out = 0

    in_rate, out_rate = PRICES.get(MODEL_VERSION, (2.5, 15.0))
    cost = tokens_in * in_rate / 1_000_000 + tokens_out * out_rate / 1_000_000

    return BrdRow(
        run_id=run_id, brand_id=brand["id"], brand_name=brand["name"],
        vertical=brand["vertical"], query_text=user_prompt, repeat_idx=repeat_idx,
        seed=seed, model_version=MODEL_VERSION, raw_response=raw,
        tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost,
        timestamp=datetime.now(timezone.utc).isoformat(), from_cache=from_cache,
    )


async def run_async(n_repeat: int, concurrency: int, budget: Optional[float], run_id: str):
    if not API_KEY:
        sys.exit("OPENAI_API_KEY 미설정")

    brands = all_brands()
    out_dir = OUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(brands) * n_repeat
    print(f"🎬 BRD per-brand 실행 — {len(brands)} 브랜드 × {n_repeat}반복 = {total} 호출")
    print(f"   model={MODEL_VERSION}, concurrency={concurrency}")
    if budget is not None:
        print(f"   ⚠️  Budget: ${budget:.2f}")

    client = AsyncOpenAI(api_key=API_KEY)
    semaphore = asyncio.Semaphore(concurrency)
    budget_state: dict = {"exceeded": False}

    tasks = [
        call_one(client, semaphore, budget_state,
                 run_id=run_id, brand=b, repeat_idx=rep)
        for b in brands for rep in range(n_repeat)
    ]

    results = []
    t0 = time.time()
    for i, fut in enumerate(asyncio.as_completed(tasks), start=1):
        row = await fut
        results.append(row)
        cost = sum(r.cost_usd for r in results)
        if budget is not None and not budget_state["exceeded"] and cost >= budget:
            budget_state["exceeded"] = True
            print(f"\n⛔ Budget ${budget:.2f} 도달 (현재 ${cost:.4f})")
        if i % 50 == 0 or i == total:
            cache_n = sum(1 for r in results if r.from_cache)
            print(f"  [{i}/{total}] ${cost:.3f} 캐시={cache_n}")

    results.sort(key=lambda r: (r.brand_id, r.repeat_idx))
    jsonl = out_dir / "brd_per_brand.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")

    summary = {
        "run_id": run_id, "n_brands": len(brands), "n_repeat": n_repeat,
        "total_calls": total, "cache_hits": sum(1 for r in results if r.from_cache),
        "total_cost_usd": round(sum(r.cost_usd for r in results), 4),
        "elapsed_sec": round(time.time() - t0, 1),
        "model_version": MODEL_VERSION,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(f"\n✅ {jsonl}")
    print(f"   비용 ${summary['total_cost_usd']}, 소요 {summary['elapsed_sec']}s")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-repeat", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=20)
    p.add_argument("--budget", type=float, default=1.5)
    args = p.parse_args()
    run_id = f"brd_per_brand_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    asyncio.run(run_async(args.n_repeat, args.concurrency, args.budget, run_id))


if __name__ == "__main__":
    main()
