"""
퓨런헬스케어 올바른 자사몰 URL — furun.kr.
이전에 잘못 써온 furenhealth.com은 DNS 죽음 + 도메인 탈취. Wayne 확인으로 furun.kr 확정.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from curl_cffi import requests as cffi_requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
JSONL_PATH = DATA_RAW / "_index" / "cffi_selfmall.jsonl"

TARGETS = [
    {"url": "http://furun.kr/", "vertical": "medical_device", "brand": "furun",
     "channel": "self_mall", "sku_id": "main_cffi"},
    {"url": "https://furun.kr/", "vertical": "medical_device", "brand": "furun",
     "channel": "self_mall", "sku_id": "main_https_cffi"},
]

IMPERSONATE = "chrome"
SLEEP = 3.0


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []
    for tgt in TARGETS:
        time.sleep(SLEEP)
        url = tgt["url"]
        print(f"→ {url}")
        raw_dir = DATA_RAW / tgt["vertical"] / tgt["brand"] / tgt["channel"] / today
        raw_dir.mkdir(parents=True, exist_ok=True)
        try:
            r = cffi_requests.get(
                url, impersonate=IMPERSONATE, timeout=25, allow_redirects=True,
                headers={
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none", "Upgrade-Insecure-Requests": "1",
                },
            )
            body = r.text
            sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
            filename = f"{tgt['sku_id']}_{sha}_cffi.html"
            raw_path = raw_dir / filename
            raw_path.write_text(body, encoding="utf-8")
            marker = "✅" if len(body) > 5000 else "⚠️"
            print(f"  {marker} HTTP {r.status_code} | {len(body):,} bytes | final={r.url}")
            results.append({
                "url": url, "status": r.status_code, "final_url": r.url,
                "html_length": len(body), "raw_path": str(raw_path.relative_to(REPO_ROOT)),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            print(f"  ❌ error: {e}")
            results.append({"url": url, "error": str(e)})

    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
