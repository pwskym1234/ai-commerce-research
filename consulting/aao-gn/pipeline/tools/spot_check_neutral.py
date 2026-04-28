"""
NEUTRAL 추천 0% 원인 진단용 일회성 스팟체크.

브랜드당 NEUTRAL 5개 프롬프트를 4개 세팅으로 2회씩 호출 → 브랜드 등장률 비교.

세팅:
  A. 현재 기준선      gpt-4o-search-preview + medium, KR
  B. 검색 강도↑       gpt-4o-search-preview + high,   KR
  C. 구체 추천 유도    A + 프롬프트 끝에 "구체 제품명/브랜드 2~3개 추천해줘"
  D. Responses API    gpt-4o + tools=[{"type":"web_search"}]
"""

import argparse
import csv
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OPENAI_API_KEY

from openai import OpenAI


def load_brand(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_neutral_prompts(brand_dir: str, n: int = 5) -> List[Dict]:
    path = os.path.join(brand_dir, "prompts.csv")
    with open(path, "r", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("category_code") == "NEUTRAL"]
    return rows[:n]


def _brand_variants(brand: Dict) -> List[str]:
    raw = list(brand.get("brand_keywords") or [])
    if brand.get("brand_name"):
        raw.insert(0, brand["brand_name"])
    if brand.get("brand_name_en"):
        raw.insert(1, brand["brand_name_en"])
    out = []
    seen = set()
    for v in raw:
        v = (v or "").strip()
        if not v or v.lower() in seen:
            continue
        seen.add(v.lower())
        out.append(v)
    return out


def _strict_variants(brand: Dict) -> List[str]:
    """
    false positive 방지: 바디닥터K는 'K' 없는 '바디닥터'만 매칭하면 다른 회사
    '바디닥터 요실금치료기'까지 잡힘. 2글자 이하 토큰이나 브랜드 구분자 없는 variant는 제외.
    """
    name = (brand.get("brand_name") or "").strip()
    variants = _brand_variants(brand)
    if "바디닥터" in name and name.endswith("K") is False and "K" in name:
        # name 안에 K 있지만 끝이 K가 아닐 때는 특수. 현재 로직은 단순화.
        pass
    # 바디닥터K 케이스: '바디닥터'만 있는 variant 제거
    if name.replace(" ", "").lower() == "바디닥터k":
        variants = [v for v in variants if v.strip() != "바디닥터"]
    return variants


def brand_hit(text: str, variants: List[str]) -> bool:
    if not text:
        return False
    t = text.lower()
    return any(v.lower() in t for v in variants)


def extract_chat_citations(message) -> List[str]:
    out = []
    for ann in getattr(message, "annotations", None) or []:
        if getattr(ann, "type", None) != "url_citation":
            continue
        cit = getattr(ann, "url_citation", None)
        url = getattr(cit, "url", "") if cit else ""
        if url:
            out.append(url)
    return out


def run_setting(client: OpenAI, setting: str, prompt_text: str) -> Tuple[str, List[str], str]:
    """
    returns: (response_text, citation_urls, model_used)
    """
    if setting in ("A", "B", "C"):
        search_size = "high" if setting == "B" else "medium"
        text = prompt_text
        if setting == "C":
            text = prompt_text + "\n\n구체 제품명이나 브랜드명 2~3개를 추천해줘."
        resp = client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={
                "search_context_size": search_size,
                "user_location": {"type": "approximate", "approximate": {"country": "KR"}},
            },
            messages=[{"role": "user", "content": text}],
        )
        msg = resp.choices[0].message
        return msg.content or "", extract_chat_citations(msg), resp.model
    elif setting == "D":
        resp = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search"}],
            input=prompt_text,
        )
        text = getattr(resp, "output_text", "") or ""
        return text, [], resp.model
    raise ValueError(f"unknown setting: {setting}")


def run_brand(brand_config_path: str, runs_per_setting: int = 2, n_prompts: int = 5) -> Dict:
    brand = load_brand(brand_config_path)
    brand_dir = os.path.dirname(brand_config_path)
    variants = _strict_variants(brand)
    print(f"\n=== {brand['brand_name']} spot check ===")
    print(f"  brand variants for matching: {variants}")

    prompts = load_neutral_prompts(brand_dir, n_prompts)
    print(f"  neutral prompts loaded: {len(prompts)}")

    client = OpenAI(api_key=OPENAI_API_KEY)

    results_by_setting: Dict[str, List[Dict]] = defaultdict(list)

    settings = ["A", "B", "C", "D"]
    total_calls = len(settings) * runs_per_setting * len(prompts)
    done = 0
    for setting in settings:
        for p in prompts:
            for run in range(1, runs_per_setting + 1):
                done += 1
                prefix = f"  [{done}/{total_calls}] setting={setting} {p['prompt_id']} run{run}"
                try:
                    text, cits, model = run_setting(client, setting, p["prompt_text"])
                    hit = brand_hit(text, variants)
                    results_by_setting[setting].append({
                        "prompt_id": p["prompt_id"],
                        "run": run,
                        "model": model,
                        "hit": hit,
                        "citations_count": len(cits),
                        "response_length": len(text or ""),
                        "response_preview": (text or "")[:400],
                    })
                    print(f"{prefix}  hit={hit}  len={len(text or '')}  cits={len(cits)}")
                except Exception as e:
                    print(f"{prefix}  ERROR: {type(e).__name__}: {e}")
                    results_by_setting[setting].append({
                        "prompt_id": p["prompt_id"],
                        "run": run,
                        "error": f"{type(e).__name__}: {e}",
                    })
                time.sleep(0.6)

    # summary
    setting_labels = {
        "A": "현재 기준선 (medium)",
        "B": "검색 강도 high",
        "C": "구체 추천 유도",
        "D": "gpt-4o + Responses",
    }
    summary_rows = []
    print(f"\n=== {brand['brand_name']} 결과 요약 ===")
    print(f"  {'setting':28} {'brand_hits':>12} {'avg_cits':>10} {'avg_len':>10}")
    for setting in settings:
        rows = results_by_setting[setting]
        ok = [r for r in rows if "error" not in r]
        hits = sum(1 for r in ok if r["hit"])
        avg_c = sum(r["citations_count"] for r in ok) / max(len(ok), 1)
        avg_l = sum(r["response_length"] for r in ok) / max(len(ok), 1)
        denom = len(rows)
        print(f"  {setting_labels[setting]:28} {f'{hits}/{denom}':>12} {avg_c:>10.2f} {avg_l:>10.0f}")
        summary_rows.append({
            "setting": setting,
            "label": setting_labels[setting],
            "hits": hits,
            "total": denom,
            "avg_citations": round(avg_c, 2),
            "avg_response_length": round(avg_l, 0),
        })

    report = {
        "brand_name": brand["brand_name"],
        "brand_variants": variants,
        "prompt_ids_sampled": [p["prompt_id"] for p in prompts],
        "runs_per_setting": runs_per_setting,
        "summary": summary_rows,
        "details_by_setting": dict(results_by_setting),
    }

    out_path = os.path.join(brand_dir, "spot_check_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  saved: {out_path}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", action="append", required=True, help="brand_config.json 경로 (여러번 지정 가능)")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--n-prompts", type=int, default=5)
    args = ap.parse_args()

    for bp in args.brand:
        run_brand(bp, runs_per_setting=args.runs, n_prompts=args.n_prompts)


if __name__ == "__main__":
    main()
