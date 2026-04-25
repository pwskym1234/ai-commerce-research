"""
BRD per-brand 응답 정밀 파싱 — Claude haiku.

각 브랜드의 BRD 응답을 분석해서 brand-level X 변수 추출:
  · brand_sentiment: positive/neutral/negative
  · mentioned_attributes: 효능·기능 키워드 리스트
  · co_mentioned_brands: 같이 거론되는 다른 브랜드들
  · safety_avoidance: 의료진 상담 회피 발언 여부
  · confidence: AI가 그 브랜드를 얼마나 확신 있게 평가하는가

산출:
  ml/data/b1_runs/<run_id>/parsed_brd_claude.jsonl  (호출 단위)
  data/processed/brand_brd_features.jsonl  (brand-level 집계)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from collections import Counter

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CONCURRENCY = 10


PARSE_INSTRUCTION = """다음은 사용자가 특정 브랜드/제품에 대해 물었을 때 AI 어시스턴트의 응답입니다.

**대상 브랜드**: {brand_name} (vertical: {vertical})
**사용자 질문**: {query}

**AI 응답**:
{response}

이 응답을 분석해서 JSON으로 추출해주세요.

1. `sentiment`: 대상 브랜드에 대한 전체 톤 (positive/neutral/negative/unknown)
   - positive: 긍정·추천·장점 강조
   - negative: 부정·단점·회피 권고
   - neutral: 양면·중립 평가
   - unknown: 그 브랜드 자체를 모른다·정보 없다고 답함

2. `mentioned_attributes`: 응답에서 그 브랜드의 특성·기능·효능으로 언급된 키워드 리스트 (5개 이내)
   예) ["저주파 EMS", "골반저근 강화", "렌탈 가능", "케겔 운동"]

3. `co_mentioned_brands`: 응답에서 비교·대안·언급된 다른 브랜드명 (한국어/영어 모두) — 대상 브랜드 자체 제외
   예) ["이지케이", "코웨이 테라솔", "Elvie"]

4. `safety_avoidance`: true/false — "의사·약사·전문가와 상담" 같은 회피 발언이 있는가

5. `confidence`: 0.0~1.0 — AI가 그 브랜드에 대한 평가에 얼마나 확신을 보이는가
   - 높음 (0.8+): 구체 정보·수치 인용
   - 중간 (0.5~0.8): 일반 정보 정도
   - 낮음 (~0.4): "모르겠다", "정보 부족", 두루뭉술

JSON만 출력. 설명 없이 다음 형식으로:

{{
  "sentiment": "positive",
  "mentioned_attributes": ["...", "..."],
  "co_mentioned_brands": ["...", "..."],
  "safety_avoidance": false,
  "confidence": 0.7
}}"""


@dataclass
class ParsedBrdRow:
    run_id: str
    brand_id: str
    brand_name: str
    vertical: str
    repeat_idx: int
    sentiment: str
    mentioned_attributes: list[str]
    co_mentioned_brands: list[str]
    safety_avoidance: bool
    confidence: float
    claude_tokens_in: int
    claude_tokens_out: int
    claude_cost_usd: float
    parse_error: Optional[str] = None


async def parse_one(client: AsyncAnthropic, semaphore: asyncio.Semaphore,
                    budget_state: dict, row: dict) -> ParsedBrdRow:
    if budget_state.get("exceeded"):
        return ParsedBrdRow(
            run_id=row["run_id"], brand_id=row["brand_id"], brand_name=row["brand_name"],
            vertical=row["vertical"], repeat_idx=row["repeat_idx"],
            sentiment="unknown", mentioned_attributes=[], co_mentioned_brands=[],
            safety_avoidance=False, confidence=0.0,
            claude_tokens_in=0, claude_tokens_out=0, claude_cost_usd=0.0,
            parse_error="SKIPPED: budget",
        )

    prompt = PARSE_INSTRUCTION.format(
        brand_name=row["brand_name"], vertical=row["vertical"],
        query=row["query_text"], response=row["raw_response"][:3000],
    )

    parse_error = None
    parsed = {}
    tokens_in = tokens_out = 0

    async with semaphore:
        try:
            r = await client.messages.create(
                model=CLAUDE_MODEL, max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = r.content[0].text if r.content else ""
            tokens_in = r.usage.input_tokens if r.usage else 0
            tokens_out = r.usage.output_tokens if r.usage else 0

            tc = text.strip()
            if tc.startswith("```"):
                tc = tc.split("```")[1]
                if tc.startswith("json"): tc = tc[4:].strip()
                tc = tc.rstrip("`").strip()
            parsed = json.loads(tc)
        except Exception as e:
            parse_error = f"{type(e).__name__}: {str(e)[:120]}"

    cost = tokens_in * 0.25 / 1_000_000 + tokens_out * 1.25 / 1_000_000

    return ParsedBrdRow(
        run_id=row["run_id"], brand_id=row["brand_id"], brand_name=row["brand_name"],
        vertical=row["vertical"], repeat_idx=row["repeat_idx"],
        sentiment=parsed.get("sentiment", "unknown"),
        mentioned_attributes=parsed.get("mentioned_attributes", []),
        co_mentioned_brands=parsed.get("co_mentioned_brands", []),
        safety_avoidance=parsed.get("safety_avoidance", False),
        confidence=parsed.get("confidence", 0.0),
        claude_tokens_in=tokens_in, claude_tokens_out=tokens_out, claude_cost_usd=cost,
        parse_error=parse_error,
    )


def aggregate_brand_x(parsed_rows: list[ParsedBrdRow]) -> dict:
    """brand-level X 변수 집계."""
    by_brand: dict = {}
    for r in parsed_rows:
        if r.parse_error: continue
        b = r.brand_id
        if b not in by_brand:
            by_brand[b] = {
                "brand_id": b, "brand_name": r.brand_name, "vertical": r.vertical,
                "n_obs": 0, "sentiments": [], "attributes": Counter(),
                "co_brands": Counter(), "safety_count": 0, "confidence_sum": 0.0,
            }
        d = by_brand[b]
        d["n_obs"] += 1
        d["sentiments"].append(r.sentiment)
        for a in r.mentioned_attributes: d["attributes"][a] += 1
        for cb in r.co_mentioned_brands: d["co_brands"][cb] += 1
        if r.safety_avoidance: d["safety_count"] += 1
        d["confidence_sum"] += r.confidence

    agg = []
    for b, d in by_brand.items():
        n = d["n_obs"]
        sent_counts = Counter(d["sentiments"])
        agg.append({
            "brand_id": d["brand_id"], "brand_name": d["brand_name"],
            "vertical": d["vertical"], "n_obs": n,
            "sentiment_positive_rate": sent_counts.get("positive", 0) / n,
            "sentiment_neutral_rate": sent_counts.get("neutral", 0) / n,
            "sentiment_negative_rate": sent_counts.get("negative", 0) / n,
            "sentiment_unknown_rate": sent_counts.get("unknown", 0) / n,
            "safety_avoidance_rate": d["safety_count"] / n,
            "confidence_mean": d["confidence_sum"] / n,
            "top_attributes": [a for a, _ in d["attributes"].most_common(10)],
            "top_co_brands": [b for b, _ in d["co_brands"].most_common(10)],
            "n_unique_attributes": len(d["attributes"]),
            "n_unique_co_brands": len(d["co_brands"]),
        })
    return agg


async def run_async(run_dir: Path, budget: Optional[float]):
    if not ANTHROPIC_KEY: sys.exit("❌ ANTHROPIC_API_KEY 미설정")
    jsonl = run_dir / "brd_per_brand.jsonl"
    if not jsonl.exists(): sys.exit(f"❌ {jsonl} 없음")

    rows = [json.loads(l) for l in jsonl.open()]
    print(f"🎬 BRD Claude 파싱 — {len(rows)} 응답, {CLAUDE_MODEL}")
    if budget: print(f"   Budget: ${budget:.2f}")

    client = AsyncAnthropic(api_key=ANTHROPIC_KEY)
    sem = asyncio.Semaphore(CONCURRENCY)
    bs: dict = {"exceeded": False}

    tasks = [parse_one(client, sem, bs, r) for r in rows]
    parsed = []
    t0 = time.time()
    for i, fut in enumerate(asyncio.as_completed(tasks), start=1):
        p = await fut
        parsed.append(p)
        cost = sum(x.claude_cost_usd for x in parsed)
        if budget and not bs["exceeded"] and cost >= budget:
            bs["exceeded"] = True
            print(f"\n⛔ Budget ${budget:.2f} 도달")
        if i % 50 == 0 or i == len(rows):
            err = sum(1 for x in parsed if x.parse_error and "SKIPPED" not in (x.parse_error or ""))
            print(f"  [{i}/{len(rows)}] ${cost:.3f} 오류={err}")

    parsed.sort(key=lambda r: (r.brand_id, r.repeat_idx))
    out = run_dir / "parsed_brd_claude.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in parsed:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    # brand-level 집계
    brand_x = aggregate_brand_x(parsed)
    bx_path = REPO_ROOT / "data" / "processed" / "brand_brd_features.jsonl"
    with bx_path.open("w", encoding="utf-8") as f:
        for d in brand_x:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"\n✅ {out}")
    print(f"✅ {bx_path} ({len(brand_x)} 브랜드)")
    print(f"   비용 ${sum(p.claude_cost_usd for p in parsed):.3f}, 소요 {time.time() - t0:.0f}s")

    # 빠른 요약
    print(f"\n📊 brand-level 요약 (정렬 = sentiment_positive_rate):")
    for d in sorted(brand_x, key=lambda x: -x["sentiment_positive_rate"]):
        print(f"  {d['brand_id']:20} pos={d['sentiment_positive_rate']:.0%} "
              f"unknown={d['sentiment_unknown_rate']:.0%} conf={d['confidence_mean']:.2f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", help="ml/data/b1_runs/<run_id>")
    p.add_argument("--budget", type=float, default=1.0)
    args = p.parse_args()
    asyncio.run(run_async(Path(args.run_dir), args.budget))


if __name__ == "__main__":
    main()
