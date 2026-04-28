"""
GEO 감사 실행 — 브랜드별 brand_config.json 기반 동적 경로/키워드 지원

사용법:
  python 03_run_audit.py --brand brands/bodydoctor/brand_config.json
"""

import argparse
import csv
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from openai import OpenAI

from config import (
    MAX_WORKERS,
    MODEL,
    OPENAI_API_KEY,
    REPEAT_COUNT,
    SEED_BASE,
    TEMPERATURE,
)


def load_brand_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompts(filepath: str) -> List[Dict]:
    prompts = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("prompt_id") and row.get("prompt_text"):
                prompts.append(
                    {
                        "prompt_id": row["prompt_id"].strip(),
                        "category_code": (row.get("category_code") or "").strip(),
                        "category": row["category"].strip(),
                        "subcategory": (row.get("subcategory") or row.get("sub_angle") or "").strip(),
                        "prompt_text": row["prompt_text"].strip(),
                        "target_competitor": (row.get("target_competitor") or "").strip(),
                    }
                )
    return prompts


def extract_citations(message) -> List[Dict]:
    """Chat Completions message.annotations 에서 url_citation 추출."""
    citations = []
    seen = set()
    anns = getattr(message, "annotations", None) or []
    for a in anns:
        if getattr(a, "type", None) != "url_citation":
            continue
        uc = getattr(a, "url_citation", None)
        url = getattr(uc, "url", "") if uc else ""
        title = getattr(uc, "title", "") if uc else ""
        if url and url not in seen:
            seen.add(url)
            citations.append({"url": url, "title": title})
    return citations


def call_openai(client: OpenAI, prompt_text: str) -> Dict:
    """gpt-4o-search-preview — Chat Completions + 내장 web_search.

    모델이 자체 판단으로 검색 여부 결정 (실제 사용자 경험과 동일).
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt_text}],
        web_search_options={},
    )
    msg = response.choices[0].message
    usage = response.usage
    prompt_details = getattr(usage, "prompt_tokens_details", None)
    completion_details = getattr(usage, "completion_tokens_details", None)
    return {
        "content": msg.content or "",
        "citations": extract_citations(msg),
        "model": getattr(response, "model", MODEL),
        "usage": {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
            "cached_tokens": getattr(prompt_details, "cached_tokens", 0) if prompt_details else 0,
            "reasoning_tokens": getattr(completion_details, "reasoning_tokens", 0) if completion_details else 0,
        },
    }


def run_with_retry(
    client: OpenAI,
    prompt: Dict,
    run_number: int,
    audit_start: str,
    max_attempts: int = 4,
) -> Tuple[Optional[Dict], Optional[Exception]]:
    """OpenAI 호출 + 지수 백오프 재시도. 성공 시 record, 실패 시 error 반환."""
    backoff = 2.0
    last_err: Optional[Exception] = None
    for _ in range(max_attempts):
        try:
            result = call_openai(client, prompt["prompt_text"])
            return (
                {
                    "prompt_id": prompt["prompt_id"],
                    "category_code": prompt.get("category_code", ""),
                    "category": prompt["category"],
                    "subcategory": prompt.get("subcategory", ""),
                    "target_competitor": prompt.get("target_competitor", ""),
                    "prompt_text": prompt["prompt_text"],
                    "run_number": run_number,
                    "seed": SEED_BASE + run_number - 1,
                    "response": result["content"],
                    "citations": result["citations"],
                    "model": result["model"],
                    "usage": result["usage"],
                    "timestamp": datetime.now().isoformat(),
                    "audit_start": audit_start,
                },
                None,
            )
        except Exception as e:
            last_err = e
            time.sleep(backoff)
            backoff = min(backoff * 2, 60.0)
    return None, last_err


def load_existing_responses(filepath: str) -> List[Dict]:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_responses(responses: List[Dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)


def get_completed_keys(responses: List[Dict]) -> Set[Tuple[str, int]]:
    return {(r["prompt_id"], r["run_number"]) for r in responses}


def main() -> None:
    parser = argparse.ArgumentParser(description="GEO Audit Runner")
    parser.add_argument(
        "--brand",
        required=True,
        help="brand_config.json 경로 (예: brands/bodydoctor/brand_config.json)",
    )
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY 환경변수를 설정해주세요.")
        print('  export OPENAI_API_KEY="sk-..."')
        return

    brand = load_brand_config(args.brand)
    brand_dir = os.path.dirname(args.brand)
    prompts_file = os.path.join(brand_dir, "prompts.csv")
    raw_responses_file = os.path.join(brand_dir, "results", "raw_responses.json")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompts = load_prompts(prompts_file)
    print(f"[{brand['brand_name']}] 프롬프트 {len(prompts)}개 로드 완료")

    responses = load_existing_responses(raw_responses_file)
    completed = get_completed_keys(responses)
    print(f"기존 응답 {len(responses)}건 로드 (중복 건너뜀)")

    tasks: List[Tuple[Dict, int]] = [
        (p, r)
        for p in prompts
        for r in range(1, REPEAT_COUNT + 1)
        if (p["prompt_id"], r) not in completed
    ]

    total = len(prompts) * REPEAT_COUNT
    done = len(completed)
    start_time = datetime.now().isoformat()
    error_count = 0
    save_every = 20
    since_last_save = 0
    lock = threading.Lock()

    if not tasks:
        print(f"모든 작업 완료됨 ({done}/{total}). 추가 실행 없음.")
    else:
        print(f"병렬 실행 시작 · 대기 {len(tasks)}건 · workers={MAX_WORKERS}")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futures = {
                ex.submit(run_with_retry, client, p, r, start_time): (p, r)
                for p, r in tasks
            }
            for fut in as_completed(futures):
                prompt, run = futures[fut]
                try:
                    record, err = fut.result()
                except Exception as e:
                    record, err = None, e

                with lock:
                    done += 1
                    if record is not None:
                        responses.append(record)
                        cit_n = len(record["citations"])
                        print(
                            f"[{done}/{total}] {prompt['prompt_id']} (run {run}) "
                            f"OK ({record['usage']['total_tokens']} tok"
                            + (f", {cit_n} citations" if cit_n else "")
                            + ")"
                        )
                        since_last_save += 1
                        if since_last_save >= save_every:
                            save_responses(responses, raw_responses_file)
                            since_last_save = 0
                    else:
                        error_count += 1
                        msg = str(err)[:150] if err else "unknown"
                        print(
                            f"[{done}/{total}] {prompt['prompt_id']} (run {run}) "
                            f"ERROR: {msg}"
                        )

    save_responses(responses, raw_responses_file)
    print(
        f"\n완료! 총 {len(responses)}건 저장됨 → {raw_responses_file}"
        + (f" (에러 {error_count}건)" if error_count else "")
    )

    # 감사 메타데이터 저장 (재실행/비교용)
    metadata_file = os.path.join(brand_dir, "results", "audit_metadata.json")
    total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in responses)
    metadata = {
        "brand_name": brand.get("brand_name", ""),
        "audit_start": start_time,
        "audit_end": datetime.now().isoformat(),
        "model": MODEL,
        "temperature": TEMPERATURE,
        "seed_base": SEED_BASE,
        "seed_min": SEED_BASE,
        "seed_max": SEED_BASE + REPEAT_COUNT - 1,
        "repeat_count": REPEAT_COUNT,
        "total_prompts": len(prompts),
        "total_calls": len(prompts) * REPEAT_COUNT,
        "total_responses": len(responses),
        "total_tokens": total_tokens,
        "error_count": error_count,
        "max_workers": MAX_WORKERS,
    }
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"메타데이터 저장 → {metadata_file}")


if __name__ == "__main__":
    main()
