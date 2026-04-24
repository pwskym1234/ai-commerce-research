"""
본실험 API 러너 — gpt-5.4 (OpenAI).

재현성 룰 (CLAUDE.md §4 R1~R10) 강제 적용:
- R1: 반복 20회 (조합 × 쿼리당)
- R2: temperature default (None 전달 → API 기본값)
- R3: 모델 버전 .env에서 핀 (OPENAI_MODEL_VERSION)
- R4: 매 반복마다 상품 제시 순서 랜덤 셔플 (seed = seed_base + repeat_idx)
- R5: seed 모든 jsonl 라인에 기록
- R6: Y 변수 중 Y2a는 binary + continuous 이중 산출 (분석 단계에서)
- R7: Wilson 95% CI — 분석 단계
- R8: raw 응답 원문 jsonl 저장 (캐시와 별도)
- R9: 파일럿 우선 권장 (이 스크립트의 --mode pilot)
- R10: 버티컬 분리 — 이 스크립트는 medical_device만 (gargle은 별도 호출)

응답 캐싱:
  key = sha256(model_version + system + user + seed + temperature_repr)
  hit → API 호출 안 함. 재실행 무료.

사용법:
    # 파일럿 (L27 × 8쿼리 × 5회 = 1,080 호출, ~$14)
    python experiments/runner.py --mode pilot

    # 본실험 (L54 × 8쿼리 × 20회 = 8,640 호출, ~$108)
    python experiments/runner.py --mode main
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")


# ========== 설정 ==========
MODEL_VERSION = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))

EXP_DIR = REPO_ROOT / "experiments"
PAGES_DIR = EXP_DIR / "synthetic_pages"
CACHE_DIR = EXP_DIR / "api_runs" / "_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ========== 쿼리 로드 (YAML, 8유형 × 3개) ==========
QUERIES_YAML = EXP_DIR / "prompts" / "queries.yaml" if False else Path(__file__).resolve().parent / "prompts" / "queries.yaml"

def load_queries() -> list[tuple[str, str, str]]:
    """Returns list of (query_id, query_type, query_text).
       query_id 예: BRD-1, BRD-2, BRD-3, CAT-1, ...
    """
    with QUERIES_YAML.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = []
    for qtype, qlist in data.items():
        for i, text in enumerate(qlist, start=1):
            items.append((f"{qtype}-{i}", qtype, text))
    return items


# ========== 경쟁군 N=6 (의료기기) ==========
COMPETITORS = [
    {"id": "bodydoctor", "name": "바디닥터 요실금치료기", "brand": "GN그룹"},
    {"id": "easyk", "name": "이지케이 EASY-K", "brand": "알파메딕"},
    {"id": "ceragem", "name": "세라젬 요실금치료기", "brand": "세라젬"},
    {"id": "furenhealth", "name": "퓨런헬스케어 요실금치료기", "brand": "퓨런헬스케어"},
    {"id": "drk", "name": "닥터케이 저주파 EMS 케겔운동기", "brand": "닥터케이 (공산품)"},
    {"id": "elvie", "name": "Elvie Trainer", "brand": "Elvie (해외)"},
]


SYSTEM_PROMPT = (
    "당신은 제품 비교·추천을 도와주는 쇼핑 어시스턴트입니다. "
    "사용자 질문에 성실하게 답하되, 경쟁 제품 중에서만 비교하고 그 외 제품은 언급하지 마세요. "
    "추천 이유는 간결하게 1~2문장으로 설명하세요."
)


# ========== 자료구조 ==========
@dataclass
class RunConfig:
    mode: str                              # pilot | main
    model_version: str
    n_repeat: int
    temperature: Optional[float] = None    # None → API 기본
    seed_base: int = SEED_BASE
    use_cache: bool = True
    vertical: str = "medical_device"


@dataclass
class CallResult:
    run_id: str
    page_id: str
    query_id: str
    repeat_idx: int
    seed: int
    model_version: str
    temperature: Optional[float]
    system_hash: str
    user_prompt_hash: str
    products_order: list[str]
    raw_response: str
    y2a_mentioned_brand_ids: list[str]
    y2a_our_selected: bool
    y4_safety_avoidance: bool
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: str
    from_cache: bool

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


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


# ========== 재현성 가드 ==========
def assert_reproducibility(cfg: RunConfig) -> None:
    assert cfg.model_version, "R3: 모델 버전 명시 필수"
    if cfg.mode == "main":
        assert cfg.n_repeat >= 15, f"R1: 본실험 반복 ≥15 필수 (pilot 제외), got {cfg.n_repeat}"
    if cfg.temperature is not None:
        assert 0.5 <= cfg.temperature <= 1.0, "R2: temperature 0 고정 금지 ([0.5, 1.0] 또는 None)"


# ========== 응답 파싱 ==========
def parse_y2a(response_text: str, our_brand_id: str) -> tuple[list[str], bool]:
    """응답에서 멘션된 경쟁사 brand id 목록 + 우리가 선택됐는지."""
    mentioned = []
    for c in COMPETITORS:
        # brand name 키워드 기반 단순 매칭 (본실험에서는 정교한 NER 필요)
        if c["id"] == "bodydoctor" and "바디닥터" in response_text:
            mentioned.append("bodydoctor")
        elif c["id"] == "easyk" and ("이지케이" in response_text or "EASY-K" in response_text or "EASY K" in response_text):
            mentioned.append("easyk")
        elif c["id"] == "ceragem" and "세라젬" in response_text:
            mentioned.append("ceragem")
        elif c["id"] == "furenhealth" and ("퓨런" in response_text or "furen" in response_text.lower()):
            mentioned.append("furenhealth")
        elif c["id"] == "drk" and "닥터케이" in response_text:
            mentioned.append("drk")
        elif c["id"] == "elvie" and "elvie" in response_text.lower():
            mentioned.append("elvie")
    return mentioned, our_brand_id in mentioned


SAFETY_AVOID_PATTERNS = ["전문가와 상담", "의사와 상담", "의료진 상담", "병원 방문", "진료를 받으"]


def parse_y4(response_text: str) -> bool:
    return any(p in response_text for p in SAFETY_AVOID_PATTERNS)


# ========== 단일 호출 ==========
def make_user_prompt(page_html: str, query: str, products_order: list[str]) -> str:
    product_list = "\n".join(
        f"{i+1}. {next(c['name'] for c in COMPETITORS if c['id'] == pid)}"
        for i, pid in enumerate(products_order)
    )
    # 가상 페이지 HTML을 압축해서 prompt에 주입 (텍스트만)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    page_text = soup.get_text(separator=" ", strip=True)[:3000]

    return (
        f"다음 제품들을 비교해 주세요:\n{product_list}\n\n"
        f"첫 번째 제품(바디닥터)의 상세 페이지 내용:\n{page_text}\n\n"
        f"사용자 질문: {query}\n\n"
        f"위 제품들만 고려해서 답변해 주세요. 추천 이유도 같이."
    )


def call_one(cfg: RunConfig, client: OpenAI, page_html: str, page_id: str,
             query_id: str, query: str, repeat_idx: int, run_id: str) -> CallResult:
    # R4: 매 반복 상품 순서 셔플
    seed = cfg.seed_base + repeat_idx
    rng = random.Random(seed)
    order = [c["id"] for c in COMPETITORS]
    rng.shuffle(order)

    user_prompt = make_user_prompt(page_html, query, order)

    sys_hash = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:12]
    usr_hash = hashlib.sha256(user_prompt.encode("utf-8")).hexdigest()[:12]
    key = cache_key(cfg.model_version, SYSTEM_PROMPT, user_prompt, seed, cfg.temperature)

    cached = load_cache(key) if cfg.use_cache else None
    from_cache = cached is not None

    if cached:
        raw = cached["raw_response"]
        tokens_in = cached.get("tokens_in", 0)
        tokens_out = cached.get("tokens_out", 0)
    else:
        # OpenAI 호출
        params = {
            "model": cfg.model_version,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }
        if cfg.temperature is not None:
            params["temperature"] = cfg.temperature

        r = client.chat.completions.create(**params)
        raw = r.choices[0].message.content or ""
        tokens_in = r.usage.prompt_tokens if r.usage else 0
        tokens_out = r.usage.completion_tokens if r.usage else 0
        save_cache(key, {"raw_response": raw, "tokens_in": tokens_in, "tokens_out": tokens_out})

    # Y 변수 추출
    mentioned, our_selected = parse_y2a(raw, "bodydoctor")
    y4 = parse_y4(raw)

    # 모델별 단가 (per 1M tokens)
    # gpt-5.4: $2.50 / $15
    # gpt-5.4-mini: $0.75 / $4.50
    # gpt-5.4-nano: $0.20 / $1.25
    model_prices = {
        "gpt-5.4": (2.5, 15.0),
        "gpt-5.4-mini": (0.75, 4.5),
        "gpt-5.4-nano": (0.2, 1.25),
    }
    in_rate, out_rate = model_prices.get(cfg.model_version, (2.5, 15.0))
    cost = tokens_in * in_rate / 1_000_000 + tokens_out * out_rate / 1_000_000

    return CallResult(
        run_id=run_id,
        page_id=page_id,
        query_id=query_id,
        repeat_idx=repeat_idx,
        seed=seed,
        model_version=cfg.model_version,
        temperature=cfg.temperature,
        system_hash=sys_hash,
        user_prompt_hash=usr_hash,
        products_order=order,
        raw_response=raw,
        y2a_mentioned_brand_ids=mentioned,
        y2a_our_selected=our_selected,
        y4_safety_avoidance=y4,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost,
        timestamp=datetime.now(timezone.utc).isoformat(),
        from_cache=from_cache,
    )


# ========== 실험 본체 ==========
def run_experiment(cfg: RunConfig) -> dict:
    assert_reproducibility(cfg)
    if not API_KEY:
        sys.exit("OPENAI_API_KEY 미설정")

    client = OpenAI(api_key=API_KEY)
    run_id = f"{cfg.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = EXP_DIR / "api_runs" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # config snapshot
    (out_dir / "config.json").write_text(
        json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 설계 매트릭스 로드
    matrix_path = PAGES_DIR / "design_matrix.csv"
    with matrix_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 쿼리 8유형 × 3개 = 24개 (YAML 로드)
    all_queries = load_queries()  # [(qid, qtype, text), ...]
    if cfg.mode == "pilot":
        rows = rows[:27]
        # 파일럿: BRD-1, CAT-1, SYM-1 (유형당 1개만)
        query_items = [q for q in all_queries if q[0].endswith("-1")][:3]
    else:
        query_items = all_queries  # 전체 24개

    jsonl_path = out_dir / "responses.jsonl"
    total = len(rows) * len(query_items) * cfg.n_repeat
    print(f"🎬 run_id={run_id}, 총 호출: {total}")
    print(f"   페이지={len(rows)}, 쿼리={len(query_items)}, 반복={cfg.n_repeat}, 모델={cfg.model_version}")

    done = 0
    total_cost = 0.0
    cache_hits = 0
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            page_id = row["page_id"]
            page_html = (PAGES_DIR / f"{page_id}.html").read_text(encoding="utf-8")
            for qid, qtype, query in query_items:
                for rep in range(cfg.n_repeat):
                    result = call_one(cfg, client, page_html, page_id, qid, query, rep, run_id)
                    f.write(result.to_jsonl() + "\n")
                    f.flush()
                    done += 1
                    total_cost += result.cost_usd
                    if result.from_cache:
                        cache_hits += 1
                    if done % 50 == 0:
                        print(f"  [{done}/{total}] 누적 비용 ${total_cost:.2f}, 캐시 히트 {cache_hits}")

    summary = {
        "run_id": run_id,
        "total_calls": total,
        "cache_hits": cache_hits,
        "total_cost_usd": round(total_cost, 4),
        "n_pages": len(rows),
        "n_queries": len(query_items),
        "n_repeat": cfg.n_repeat,
        "model_version": cfg.model_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n✅ 실험 완료")
    print(f"   responses.jsonl: {jsonl_path}")
    print(f"   총 비용: ${total_cost:.2f}")
    print(f"   캐시 히트: {cache_hits} / {total}")
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pilot", "main"], default="pilot")
    p.add_argument("--n-repeat", type=int, default=None)
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="설정만 출력")
    args = p.parse_args()

    n_repeat = args.n_repeat if args.n_repeat is not None else (5 if args.mode == "pilot" else 20)
    cfg = RunConfig(
        mode=args.mode,
        model_version=MODEL_VERSION,
        n_repeat=n_repeat,
        temperature=args.temperature,
        use_cache=not args.no_cache,
    )

    if args.dry_run:
        print(json.dumps(asdict(cfg), ensure_ascii=False, indent=2))
        n_queries = 3 if args.mode == "pilot" else 24  # pilot: 3개, main: 8유형×3=24개
        n_pages = 27 if args.mode == "pilot" else 54
        est_calls = n_pages * n_queries * n_repeat
        # 평균 토큰 2,000 input + 500 output 기준 호출당 비용
        prices = {"gpt-5.4": 0.0125, "gpt-5.4-mini": 0.00375, "gpt-5.4-nano": 0.001025}
        per_call = prices.get(cfg.model_version, 0.0125)
        print(f"예상 호출: {est_calls}")
        print(f"예상 비용 ({cfg.model_version}): ${est_calls * per_call:.2f}")
        return

    run_experiment(cfg)


if __name__ == "__main__":
    main()
