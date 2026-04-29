"""
데마 관찰형 쿼리 실행 — 산공통 본실험과 별도.

산공통 본실험 = 가상 페이지(54) × 쿼리(24) × 반복(20) 통제 실험
이 스크립트 = 가상 페이지 없이 **실제 브랜드 이름만** 프롬프트에 넣고 AI 응답 수집
           → 데마 모델 학습용 Y (브랜드별 언급률·감성·순위) 생성

친구 대시보드와 호환 구조 (4유형 + 우리 8유형 병행 수집).

사용법:
  python ml/scripts/run_observational_queries.py --mode pilot  # 소량
  python ml/scripts/run_observational_queries.py --mode main   # 전체
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

# runner.py와 동일한 파싱 로직 재사용
sys.path.insert(0, str(REPO_ROOT / "experiments"))
from runner import (
    COMPETITOR_KEYWORDS, COMPETITORS, KNOWN_OTHER_BRANDS,
    parse_mentioned_predefined, parse_other_brands,
    parse_y2a_by_type, parse_y4,
    cache_key, load_cache, save_cache,
)

MODEL_VERSION = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4-nano")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))
QUERIES_YAML = REPO_ROOT / "experiments" / "prompts" / "queries.yaml"
OUT_DIR = REPO_ROOT / "ml" / "data" / "observational_runs"


SYSTEM_PROMPT_OBS = (
    "당신은 제품 비교·추천을 도와주는 쇼핑 어시스턴트입니다. "
    "한국 시장에서 가정용 의료기기·요실금 치료기 관련 질문에 답해 주세요. "
    "추천 근거를 1~2문장으로 간결히 설명하세요."
)


@dataclass
class ObsResult:
    run_id: str
    query_id: str
    query_type: str
    query_text: str
    repeat_idx: int
    seed: int
    model_version: str
    temperature: Optional[float]
    raw_response: str
    mentioned_predefined: list[str]
    other_brands_detected: list[str]
    y2a_mention: bool
    y2a_positive: Optional[str]
    y2a_alternative: Optional[bool]
    y2a_wintieloss: Optional[str]
    y2a_singleselect: Optional[bool]
    y4_safety_avoidance: bool
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: str
    from_cache: bool


def load_queries():
    with QUERIES_YAML.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = []
    for qtype, qlist in data.items():
        for i, text in enumerate(qlist, start=1):
            items.append((f"{qtype}-{i}", qtype, text))
    return items


def call_one(client, cfg, qid, qtype, qtext, repeat_idx, run_id):
    seed = SEED_BASE + repeat_idx
    # 관찰형은 페이지 없고 쿼리만 — 하지만 Position bias 위해 경쟁사 명시적 리스트 유무 선택 필요
    # 친구 대시보드 방식: 경쟁사 리스트 없이 쿼리만 (AI의 prior 측정)
    # → 우리도 동일: "X 추천해줘" 만 던지고 AI가 자유롭게 브랜드 언급
    user_prompt = qtext

    key = cache_key(cfg["model_version"], SYSTEM_PROMPT_OBS, user_prompt, seed, cfg["temperature"])
    cached = load_cache(key) if cfg["use_cache"] else None
    from_cache = cached is not None

    if cached:
        raw = cached["raw_response"]
        tokens_in = cached.get("tokens_in", 0)
        tokens_out = cached.get("tokens_out", 0)
    else:
        params = {
            "model": cfg["model_version"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_OBS},
                {"role": "user", "content": user_prompt},
            ],
        }
        if cfg["temperature"] is not None:
            params["temperature"] = cfg["temperature"]
        r = client.chat.completions.create(**params)
        raw = r.choices[0].message.content or ""
        tokens_in = r.usage.prompt_tokens if r.usage else 0
        tokens_out = r.usage.completion_tokens if r.usage else 0
        save_cache(key, {"raw_response": raw, "tokens_in": tokens_in, "tokens_out": tokens_out})

    mentioned = parse_mentioned_predefined(raw)
    y2a_sub = parse_y2a_by_type(raw, qid, "bodydoctor", mentioned)
    other = parse_other_brands(raw, exclude_ids=mentioned)
    y4 = parse_y4(raw)

    prices = {"gpt-5.4": (2.5, 15.0), "gpt-5.4-mini": (0.75, 4.5), "gpt-5.4-nano": (0.2, 1.25)}
    in_rate, out_rate = prices.get(cfg["model_version"], (2.5, 15.0))
    cost = tokens_in * in_rate / 1_000_000 + tokens_out * out_rate / 1_000_000

    return ObsResult(
        run_id=run_id, query_id=qid, query_type=qtype, query_text=qtext,
        repeat_idx=repeat_idx, seed=seed, model_version=cfg["model_version"],
        temperature=cfg["temperature"], raw_response=raw,
        mentioned_predefined=mentioned, other_brands_detected=other,
        y2a_mention=y2a_sub["y2a_mention"],
        y2a_positive=y2a_sub["y2a_positive"],
        y2a_alternative=y2a_sub["y2a_alternative"],
        y2a_wintieloss=y2a_sub["y2a_wintieloss"],
        y2a_singleselect=y2a_sub["y2a_singleselect"],
        y4_safety_avoidance=y4,
        tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost,
        timestamp=datetime.now(timezone.utc).isoformat(), from_cache=from_cache,
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pilot", "main"], default="pilot")
    p.add_argument("--n-repeat", type=int, default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    n_repeat = args.n_repeat or (5 if args.mode == "pilot" else 20)
    queries = load_queries()
    if args.mode == "pilot":
        queries = [q for q in queries if q[0].endswith("-1")][:3]  # 샘플 3개

    total = len(queries) * n_repeat
    cfg = {"model_version": MODEL_VERSION, "temperature": None, "use_cache": True}

    if args.dry_run:
        prices = {"gpt-5.4": 0.0125, "gpt-5.4-mini": 0.00375, "gpt-5.4-nano": 0.001025}
        per = prices.get(cfg["model_version"], 0.0125)
        print(f"쿼리: {len(queries)}, 반복: {n_repeat}")
        print(f"예상 호출: {total} / 비용: ${total * per:.2f}")
        return

    if not API_KEY:
        sys.exit("OPENAI_API_KEY 미설정")

    client = OpenAI(api_key=API_KEY)
    run_id = f"obs_{args.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = OUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = out_dir / "observational.jsonl"
    print(f"🎬 관찰형 쿼리 실행 — {total} 호출")

    done = 0
    total_cost = 0.0
    cache_hits = 0
    with jsonl_path.open("w", encoding="utf-8") as f:
        for qid, qtype, qtext in queries:
            for rep in range(n_repeat):
                result = call_one(client, cfg, qid, qtype, qtext, rep, run_id)
                f.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
                f.flush()
                done += 1
                total_cost += result.cost_usd
                if result.from_cache:
                    cache_hits += 1
                if done % 20 == 0:
                    print(f"  [{done}/{total}] ${total_cost:.3f} 캐시 {cache_hits}")

    summary = {"run_id": run_id, "total": total, "cost_usd": round(total_cost, 4),
               "cache_hits": cache_hits, "model": cfg["model_version"]}
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {jsonl_path}")


if __name__ == "__main__":
    main()
