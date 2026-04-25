"""
Phase B1 통합 비동기 러너 — 오픈셋(B1-A) + 클로즈드셋(B1-B).

설계 결정 (2026-04-25 Wayne):
- 시스템 프롬프트: 미니멀 (옵션 B) — "한국어로 답변" 만
- 파싱: 룰 기반 1차 (Claude API는 ANTHROPIC_API_KEY 받으면 추가)
- B1-B: 페이지 풀 텍스트 + URL 메타 (옵션 C)
- 병렬: asyncio + Semaphore(20), 동시 20 호출

사용법:
  # 의료기기 오픈셋 (B1-A)
  python ml/scripts/run_b1_async.py --mode open --vertical medical_device

  # 의료기기 클로즈드셋 (B1-B)
  python ml/scripts/run_b1_async.py --mode closed --vertical medical_device

  # 가글 둘 다
  python ml/scripts/run_b1_async.py --mode open --vertical gargle
  python ml/scripts/run_b1_async.py --mode closed --vertical gargle

  # 파일럿 (5 반복만)
  python ml/scripts/run_b1_async.py --mode open --vertical medical_device --pilot
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import AsyncOpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

sys.path.insert(0, str(REPO_ROOT / "experiments"))
from runner import (
    COMPETITORS, COMPETITORS_GARGLE, COMPETITOR_KEYWORDS, KNOWN_OTHER_BRANDS,
    parse_mentioned_predefined, parse_other_brands, parse_y2a_by_type, parse_y4,
)

MODEL_VERSION = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4-nano").strip()
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))

EXP_DIR = REPO_ROOT / "experiments"
CACHE_DIR = EXP_DIR / "api_runs" / "_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = REPO_ROOT / "ml" / "data" / "b1_runs"

# 미니멀 시스템 프롬프트 (옵션 B) — 영어 응답 방지만
SYSTEM_PROMPT = "한국어로 답변해주세요."

# B1-B 클로즈드셋 instruction
CLOSED_INSTRUCTION = (
    "다음 제품들의 상세 페이지 정보를 참고하여 사용자 질문에 답변해주세요. "
    "위 제품들 중에서만 추천하고, 추천 이유를 1~2문장으로 설명해주세요."
)


# ========== 데이터 로드 ==========
def load_queries(vertical: str) -> list[tuple[str, str, str]]:
    """8유형 × 3 = 24개 (qid, qtype, text)."""
    yaml_path = EXP_DIR / "prompts" / (
        "queries.yaml" if vertical == "medical_device" else "queries_gargle.yaml"
    )
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = []
    for qtype, qlist in data.items():
        for i, text in enumerate(qlist, start=1):
            items.append((f"{qtype}-{i}", qtype, text))
    return items


def load_pages_with_meta(vertical: str) -> list[dict]:
    """B1-B용: 경쟁군 brand만 + 의미 있는 텍스트(>500자) 페이지만 컨텍스트에 포함.

    원시 URL은 data/raw/_index/*.jsonl 에서 raw_path → url 매핑.
    Elvie 등 경쟁군 제외 브랜드는 vertical=medical_device 라도 자동 제외.
    """
    # 0) 경쟁군 brand_id 화이트리스트 + features brand 별칭 매핑
    if vertical == "medical_device":
        allowed_brands = {c["id"] for c in COMPETITORS}
    else:
        allowed_brands = {c["id"] for c in COMPETITORS_GARGLE}

    # features.jsonl 의 brand 값 ↔ COMPETITORS id 별칭
    # (회사 등록명 vs 자사몰 도메인 차이, "gargle_" 접두사 차이 등)
    FEATURE_BRAND_ALIAS = {
        "furun": "furenhealth",      # furun.kr 자사몰 도메인 = (주)퓨런헬스케어
        "2080": "gargle_2080",       # COMPETITORS_GARGLE id 가독성 위해 접두사 추가
    }

    # 1) raw_path → url 매핑 dict 작성
    raw_index_dir = REPO_ROOT / "data" / "raw" / "_index"
    raw_to_url = {}
    for jsonl in raw_index_dir.glob("*.jsonl"):
        with jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    rp = d.get("raw_path", "")
                    url = d.get("url", "")
                    if rp and url:
                        raw_to_url[rp] = url
                except Exception:
                    pass

    # 2) features.jsonl 에서 vertical + 경쟁군 필터 → brand 단위로 "가장 긴 텍스트" 1개 선택
    feat_path = REPO_ROOT / "data" / "processed" / "features.jsonl"
    candidates_by_brand: dict[str, dict] = {}  # brand_canonical → 최선 후보

    with feat_path.open("r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("vertical") != vertical:
                continue
            brand_canonical = FEATURE_BRAND_ALIAS.get(d["brand"], d["brand"])
            if brand_canonical not in allowed_brands:
                continue

            rp = d.get("raw_path") or d.get("raw_relpath")
            if not rp:
                continue
            full_path = REPO_ROOT / rp
            if not full_path.exists():
                continue

            try:
                html = full_path.read_text(encoding="utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                for t in soup(["script", "style", "nav", "footer", "header"]):
                    t.decompose()
                full_text = soup.get_text(separator=" ", strip=True)
                text = full_text[:2500]
            except Exception:
                full_text, text = "", ""

            # ★ 명백한 차단 페이지(텍스트 < 100자)만 제외 — Wayne 결정 (2026-04-25):
            # brand 단위로 다 포함하기 위해 필터 완화. 짧아도 brand명은 컨텍스트에 노출.
            if len(full_text) < 100:
                continue

            # brand 단위 best 후보 (가장 긴 full_text)
            existing = candidates_by_brand.get(brand_canonical)
            if existing is None or len(full_text) > existing["_full_len"]:
                url = raw_to_url.get(rp, f"(url not indexed: {d['brand']}/{d['channel']})")
                candidates_by_brand[brand_canonical] = {
                    "brand": brand_canonical,
                    "channel": d["channel"],
                    "sku_id": d["sku_id"],
                    "url": url,
                    "text": text,
                    "_full_len": len(full_text),
                }

    pages = []
    for brand_id, p in candidates_by_brand.items():
        del p["_full_len"]
        pages.append(p)
    return pages


# ========== 캐시 ==========
def cache_key(model: str, system: str, user: str, seed: int, temp: Optional[float]) -> str:
    h = hashlib.sha256()
    h.update(f"{model}||{system}||{user}||{seed}||{temp!r}".encode("utf-8"))
    return h.hexdigest()[:24]


def load_cache(key: str) -> Optional[dict]:
    p = CACHE_DIR / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_cache(key: str, data: dict) -> None:
    p = CACHE_DIR / f"{key}.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# ========== 프롬프트 조립 ==========
def build_user_prompt_open(query: str) -> str:
    """B1-A: 쿼리만."""
    return query


def build_user_prompt_closed(query: str, pages: list[dict]) -> str:
    """B1-B: 페이지 본문 + URL + 쿼리."""
    blocks = []
    for i, p in enumerate(pages, start=1):
        block = (
            f"[제품 {i}] {p['brand']} ({p['channel']})\n"
            f"URL: {p['url']}\n"
            f"본문 발췌: {p['text']}\n"
        )
        blocks.append(block)
    pages_text = "\n".join(blocks)
    return (
        f"{pages_text}\n"
        f"---\n"
        f"{CLOSED_INSTRUCTION}\n\n"
        f"사용자 질문: {query}"
    )


# ========== 결과 dataclass ==========
@dataclass
class B1Row:
    run_id: str
    mode: str                 # open | closed
    vertical: str
    query_id: str
    query_type: str
    query_text: str
    repeat_idx: int
    seed: int
    model_version: str
    temperature: Optional[float]
    products_order: list[str]   # B1-B 셔플 결과
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


# ========== 단일 호출 (async) ==========
PRICES = {
    "gpt-5.4": (2.5, 15.0),
    "gpt-5.4-mini": (0.75, 4.5),
    "gpt-5.4-nano": (0.2, 1.25),
}


async def call_one(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    budget_state: dict,
    *,
    run_id: str,
    mode: str,
    vertical: str,
    qid: str,
    qtype: str,
    qtext: str,
    repeat_idx: int,
    pages_for_closed: list[dict] | None,
    anchor_id: str,
    use_cache: bool = True,
) -> B1Row:
    seed = SEED_BASE + repeat_idx

    # B1-B는 매 반복마다 페이지 셔플 (R4)
    if mode == "closed" and pages_for_closed:
        rng = random.Random(seed)
        pages_shuffled = rng.sample(pages_for_closed, k=len(pages_for_closed))
        user_prompt = build_user_prompt_closed(qtext, pages_shuffled)
        products_order = [p["sku_id"] for p in pages_shuffled]
    else:
        user_prompt = build_user_prompt_open(qtext)
        products_order = []

    key = cache_key(MODEL_VERSION, SYSTEM_PROMPT, user_prompt, seed, None)
    cached = load_cache(key) if use_cache else None
    from_cache = cached is not None

    if cached:
        raw = cached["raw_response"]
        tokens_in = cached.get("tokens_in", 0)
        tokens_out = cached.get("tokens_out", 0)
    elif budget_state.get("exceeded"):
        # 예산 초과 → API 호출 안 함, skip row 반환
        raw = "(SKIPPED: budget exceeded)"
        tokens_in, tokens_out = 0, 0
    else:
        async with semaphore:
            # double check: semaphore 대기 중 다른 task 가 한도 초과 발생시켰을 수도
            if budget_state.get("exceeded"):
                raw = "(SKIPPED: budget exceeded)"
                tokens_in, tokens_out = 0, 0
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
                    save_cache(key, {"raw_response": raw, "tokens_in": tokens_in, "tokens_out": tokens_out})
                except Exception as e:
                    raw = f"(API ERROR: {type(e).__name__}: {str(e)[:200]})"
                    tokens_in, tokens_out = 0, 0

    # 룰 파싱
    mentioned = parse_mentioned_predefined(raw)
    y2a = parse_y2a_by_type(raw, qid, anchor_id, mentioned)
    other = parse_other_brands(raw, exclude_ids=mentioned)
    y4 = parse_y4(raw)

    in_rate, out_rate = PRICES.get(MODEL_VERSION, (2.5, 15.0))
    cost = tokens_in * in_rate / 1_000_000 + tokens_out * out_rate / 1_000_000

    return B1Row(
        run_id=run_id, mode=mode, vertical=vertical,
        query_id=qid, query_type=qtype, query_text=qtext,
        repeat_idx=repeat_idx, seed=seed, model_version=MODEL_VERSION, temperature=None,
        products_order=products_order, raw_response=raw,
        mentioned_predefined=mentioned, other_brands_detected=other,
        y2a_mention=y2a["y2a_mention"], y2a_positive=y2a["y2a_positive"],
        y2a_alternative=y2a["y2a_alternative"],
        y2a_wintieloss=y2a["y2a_wintieloss"], y2a_singleselect=y2a["y2a_singleselect"],
        y4_safety_avoidance=y4,
        tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost,
        timestamp=datetime.now(timezone.utc).isoformat(), from_cache=from_cache,
    )


# ========== 본 실행 (async) ==========
async def run_async(
    *, mode: str, vertical: str, n_repeat: int, concurrency: int,
    use_cache: bool, run_id: str, budget: Optional[float] = None,
) -> dict:
    if not API_KEY:
        sys.exit("OPENAI_API_KEY 미설정")

    queries = load_queries(vertical)
    pages = load_pages_with_meta(vertical) if mode == "closed" else None
    if mode == "closed" and not pages:
        sys.exit(f"❌ {vertical} 페이지 0개 — features.jsonl 확인 필요")
    anchor = "bodydoctor" if vertical == "medical_device" else "propolinse"

    out_dir = OUT_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "b1.jsonl"

    total = len(queries) * n_repeat
    print(f"🎬 run_id={run_id}")
    print(f"   mode={mode}, vertical={vertical}, queries={len(queries)}, repeat={n_repeat}")
    print(f"   total={total}, concurrency={concurrency}, model={MODEL_VERSION}")
    if mode == "closed":
        print(f"   pages={len(pages)} (페이지 텍스트 + URL 컨텍스트)")
    if budget is not None:
        print(f"   ⚠️  Budget: ${budget:.2f} (초과 시 새 호출 중단)")

    client = AsyncOpenAI(api_key=API_KEY)
    semaphore = asyncio.Semaphore(concurrency)
    budget_state: dict = {"exceeded": False}

    # 모든 호출 task 만들기
    tasks = []
    for qid, qtype, qtext in queries:
        for rep in range(n_repeat):
            tasks.append(call_one(
                client, semaphore, budget_state,
                run_id=run_id, mode=mode, vertical=vertical,
                qid=qid, qtype=qtype, qtext=qtext, repeat_idx=rep,
                pages_for_closed=pages, anchor_id=anchor, use_cache=use_cache,
            ))

    # 진행 모니터링용
    results = []
    t0 = time.time()
    for i, future in enumerate(asyncio.as_completed(tasks), start=1):
        row = await future
        results.append(row)
        cost = sum(r.cost_usd for r in results)
        # budget 체크 (이미 초과면 skip)
        if budget is not None and not budget_state["exceeded"] and cost >= budget:
            budget_state["exceeded"] = True
            skipped_remaining = total - i
            print(f"\n⛔ Budget ${budget:.2f} 도달 (현재 ${cost:.4f}). "
                  f"새 호출 중단, 진행 중 task 마저 완료... (남은 ~{skipped_remaining})")
        if i % 50 == 0 or i == total:
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            eta = (total - i) / rate if rate > 0 else 0
            cache_n = sum(1 for r in results if r.from_cache)
            skipped = sum(1 for r in results if r.raw_response.startswith("(SKIPPED"))
            tag = " ⛔" if budget_state["exceeded"] else ""
            print(f"  [{i}/{total}] ${cost:.3f} 캐시={cache_n} skip={skipped}{tag} | {rate:.1f}/s ETA={eta:.0f}s")

    # 정렬: query_id, repeat_idx 순으로
    results.sort(key=lambda r: (r.query_id, r.repeat_idx))
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")

    summary = {
        "run_id": run_id, "mode": mode, "vertical": vertical,
        "model_version": MODEL_VERSION, "n_queries": len(queries), "n_repeat": n_repeat,
        "total_calls": total,
        "cache_hits": sum(1 for r in results if r.from_cache),
        "skipped_budget": sum(1 for r in results if r.raw_response.startswith("(SKIPPED")),
        "budget_usd": budget,
        "budget_exceeded": budget_state["exceeded"],
        "total_cost_usd": round(sum(r.cost_usd for r in results), 4),
        "elapsed_sec": round(time.time() - t0, 1),
        "concurrency": concurrency,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 저장: {jsonl_path}")
    print(f"   비용: ${summary['total_cost_usd']}, 캐시 히트: {summary['cache_hits']}/{total}")
    print(f"   소요: {summary['elapsed_sec']}s")
    return summary


# ========== CLI ==========
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["open", "closed"], required=True)
    p.add_argument("--vertical", choices=["medical_device", "gargle"], required=True)
    p.add_argument("--n-repeat", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=20)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--pilot", action="store_true", help="5 반복으로 빠른 검증")
    p.add_argument("--budget", type=float, default=None,
                   help="USD 한도. 누적 비용이 한도 도달 시 새 호출 중단 (진행 중 task 는 완료)")
    args = p.parse_args()

    n_repeat = 5 if args.pilot else args.n_repeat
    run_id = f"b1_{args.mode}_{args.vertical}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    asyncio.run(run_async(
        mode=args.mode, vertical=args.vertical, n_repeat=n_repeat,
        concurrency=args.concurrency, use_cache=not args.no_cache, run_id=run_id,
        budget=args.budget,
    ))


if __name__ == "__main__":
    main()
