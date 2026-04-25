"""
B1 응답 정밀 파싱 — Claude 4.5 haiku.

룰 기반(키워드 매칭) 파싱의 한계:
- 브랜드 변형·오타 ("바디닥터스", "Body Doctor") 못 잡음
- 감성 분류 부정확 (단순 키워드 트리거)
- 비교 응답의 win/tie/loss 정밀도 낮음
- "추천하지 않는다"의 맥락 파악 못함

해결: 룰 1차 → 모든 응답에 대해 Claude haiku로 정밀 재파싱 → 비교·통합.

비용 (haiku $0.25/$1.25 per MTok):
- 호출당 input ~600 + output ~150 = $0.000338
- 1,920 응답 = $0.65

사용법:
  python ml/scripts/parse_responses_claude.py <run_dir>
  # 예: python ml/scripts/parse_responses_claude.py ml/data/b1_runs/b1_open_medical_device_20260425_095830
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

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

CONCURRENCY = 10  # Anthropic Tier 1 제한 고려


# ========== 파싱 프롬프트 ==========
PARSE_INSTRUCTION = """다음은 AI 어시스턴트가 사용자 질문에 답한 응답입니다.
응답을 분석해서 다음 항목을 JSON으로 추출해주세요.

**사용자 질문**: {query}
**쿼리 유형**: {query_type} (BRD=브랜드지명/CAT=카테고리/SYM=증상/CMP=비교/COM=경쟁사후대안/PRC=가격/USE=유스케이스/DEC=단일선택)
**우리 브랜드**: {anchor_label}

**AI 응답**:
{response}

**추출 항목**:

1. `mentioned_brands`: 응답에서 명시적으로 언급된 모든 브랜드명 (한국어/영어/오타·변형 포함). 카테고리·기능명("케겔 트레이너")은 제외, 실제 상표만.
2. `our_mention`: true/false — 우리 브랜드가 명시적으로 언급됐는가
3. `our_sentiment`: 우리 브랜드에 대한 감성 (positive/neutral/negative/not_mentioned)
   - positive: 추천·긍정적 묘사
   - negative: 회피·단점 강조·"추천하지 않음"
   - neutral: 단순 언급, 평가 없음
   - not_mentioned: 우리 브랜드 미언급
4. `our_rank`: 응답에서 우리 브랜드가 추천 순위 몇 번째인지 (1=1순위, 2=2순위, ..., null=언급 안됨 또는 순위 없음)
5. `comparison_result`: (CMP/CMP 쿼리만, 그 외 null)
   - "win": 우리가 더 우수
   - "tie": 비슷·결정 어려움
   - "loss": 경쟁사가 더 우수
   - "solo": 우리만 언급됨 (비교 의미 없음)
6. `single_select`: (DEC 쿼리만, 그 외 null)
   - 응답에서 "단 하나"로 지정한 브랜드명. 우리면 우리 브랜드, 다른 브랜드면 그 브랜드명, 결정 안 함이면 null
7. `safety_avoidance`: true/false — "의사·약사·전문가와 상담" 같은 안전 회피 발언이 있는가
8. `confidence`: 0.0~1.0 — 위 추출의 확신도 (응답이 명확하면 0.9+, 모호하면 0.5~0.7)

**JSON만 출력**. 설명 없이 다음 형식으로:

{{
  "mentioned_brands": ["...", "..."],
  "our_mention": true,
  "our_sentiment": "positive",
  "our_rank": 1,
  "comparison_result": null,
  "single_select": null,
  "safety_avoidance": false,
  "confidence": 0.9
}}"""


@dataclass
class ParsedRow:
    run_id: str
    query_id: str
    repeat_idx: int
    # Claude 추출
    mentioned_brands: list[str]
    our_mention: bool
    our_sentiment: str
    our_rank: Optional[int]
    comparison_result: Optional[str]
    single_select: Optional[str]
    safety_avoidance: bool
    confidence: float
    # 메타
    claude_tokens_in: int
    claude_tokens_out: int
    claude_cost_usd: float
    parse_error: Optional[str] = None


VERTICAL_ANCHOR = {"medical_device": "바디닥터", "gargle": "프로폴린스"}


async def parse_one(client: AsyncAnthropic, semaphore: asyncio.Semaphore,
                    budget_state: dict, row: dict) -> ParsedRow:
    if budget_state.get("exceeded"):
        return ParsedRow(
            run_id=row["run_id"], query_id=row["query_id"], repeat_idx=row["repeat_idx"],
            mentioned_brands=[], our_mention=False, our_sentiment="not_mentioned",
            our_rank=None, comparison_result=None, single_select=None,
            safety_avoidance=False, confidence=0.0,
            claude_tokens_in=0, claude_tokens_out=0, claude_cost_usd=0.0,
            parse_error="SKIPPED: budget exceeded",
        )
    vertical = row.get("vertical", "medical_device")
    anchor_label = VERTICAL_ANCHOR.get(vertical, "바디닥터")

    prompt = PARSE_INSTRUCTION.format(
        query=row["query_text"],
        query_type=row["query_type"],
        anchor_label=anchor_label,
        response=row["raw_response"][:3000],  # 응답 길면 자름
    )

    parse_error = None
    parsed = {}
    tokens_in, tokens_out = 0, 0

    async with semaphore:
        try:
            r = await client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = r.content[0].text if r.content else ""
            tokens_in = r.usage.input_tokens if r.usage else 0
            tokens_out = r.usage.output_tokens if r.usage else 0

            # JSON 추출 (```json ... ``` 코드블록 가능성 처리)
            text_clean = text.strip()
            if text_clean.startswith("```"):
                text_clean = text_clean.split("```")[1]
                if text_clean.startswith("json"):
                    text_clean = text_clean[4:].strip()
                text_clean = text_clean.rstrip("`").strip()
            parsed = json.loads(text_clean)
        except Exception as e:
            parse_error = f"{type(e).__name__}: {str(e)[:200]}"

    cost = tokens_in * 0.25 / 1_000_000 + tokens_out * 1.25 / 1_000_000

    return ParsedRow(
        run_id=row["run_id"], query_id=row["query_id"], repeat_idx=row["repeat_idx"],
        mentioned_brands=parsed.get("mentioned_brands", []),
        our_mention=parsed.get("our_mention", False),
        our_sentiment=parsed.get("our_sentiment", "not_mentioned"),
        our_rank=parsed.get("our_rank"),
        comparison_result=parsed.get("comparison_result"),
        single_select=parsed.get("single_select"),
        safety_avoidance=parsed.get("safety_avoidance", False),
        confidence=parsed.get("confidence", 0.0),
        claude_tokens_in=tokens_in, claude_tokens_out=tokens_out, claude_cost_usd=cost,
        parse_error=parse_error,
    )


async def run_async(run_dir: Path, budget: Optional[float] = None):
    if not ANTHROPIC_KEY:
        sys.exit("❌ ANTHROPIC_API_KEY 미설정")

    b1_jsonl = run_dir / "b1.jsonl"
    if not b1_jsonl.exists():
        sys.exit(f"❌ {b1_jsonl} 없음")

    rows = []
    with b1_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    print(f"🎬 Claude 정밀 파싱 — {len(rows)} 응답, model={CLAUDE_MODEL}")
    print(f"   concurrency={CONCURRENCY}")
    if budget is not None:
        print(f"   ⚠️  Budget: ${budget:.2f}")

    client = AsyncAnthropic(api_key=ANTHROPIC_KEY)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    budget_state: dict = {"exceeded": False}

    tasks = [parse_one(client, semaphore, budget_state, row) for row in rows]
    results = []
    t0 = time.time()
    for i, future in enumerate(asyncio.as_completed(tasks), start=1):
        parsed = await future
        results.append(parsed)
        cost = sum(r.claude_cost_usd for r in results)
        if budget is not None and not budget_state["exceeded"] and cost >= budget:
            budget_state["exceeded"] = True
            print(f"\n⛔ Budget ${budget:.2f} 도달 (현재 ${cost:.4f}). 새 호출 중단...")
        if i % 30 == 0 or i == len(rows):
            elapsed = time.time() - t0
            err = sum(1 for r in results if r.parse_error and "SKIPPED" not in (r.parse_error or ""))
            skipped = sum(1 for r in results if r.parse_error and "SKIPPED" in (r.parse_error or ""))
            tag = " ⛔" if budget_state["exceeded"] else ""
            print(f"  [{i}/{len(rows)}] ${cost:.3f} 오류={err} skip={skipped}{tag} | {i/elapsed:.1f}/s")

    out_path = run_dir / "parsed_claude.jsonl"
    results.sort(key=lambda r: (r.query_id, r.repeat_idx))
    with out_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    summary = {
        "run_dir": str(run_dir.resolve().relative_to(REPO_ROOT.resolve())),
        "total": len(rows),
        "model": CLAUDE_MODEL,
        "total_cost_usd": round(sum(r.claude_cost_usd for r in results), 4),
        "parse_errors": sum(1 for r in results if r.parse_error),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (run_dir / "parsed_claude_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ {out_path}")
    print(f"   비용: ${summary['total_cost_usd']}, 오류: {summary['parse_errors']}/{len(rows)}")
    print(f"   소요: {summary['elapsed_sec']}s")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", help="ml/data/b1_runs/<run_id>")
    p.add_argument("--budget", type=float, default=None, help="USD 한도")
    args = p.parse_args()
    asyncio.run(run_async(Path(args.run_dir), budget=args.budget))


if __name__ == "__main__":
    main()
