"""
4차 시도 — curl_cffi Chrome TLS fingerprint impersonation.

이전 3차 시도 모두 Cloudflare/WAF 차단으로 실패:
- 1차 requests.get: JS 미실행
- 2차 Playwright (headless + networkidle): 292~795 bytes
- 3차 Playwright + stealth v2: 동일 차단

이번 4차는 TLS ClientHello fingerprint까지 Chrome으로 위조 (JA3 우회).
curl_cffi는 BoringSSL + Chrome의 TLS extension 순서를 그대로 재현.
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
    # 리스테린 자사몰
    {"url": "https://www.listerine.kr/", "vertical": "gargle", "brand": "listerine",
     "channel": "self_mall", "sku_id": "main_cffi"},
    {"url": "https://www.listerine.kr/products/gum-care-mild", "vertical": "gargle",
     "brand": "listerine", "channel": "self_mall", "sku_id": "gum-care-mild_cffi"},
    {"url": "https://www.listerine.kr/products/greentea-mild", "vertical": "gargle",
     "brand": "listerine", "channel": "self_mall", "sku_id": "greentea-mild_cffi"},
    {"url": "https://www.listerine.kr/about", "vertical": "gargle",
     "brand": "listerine", "channel": "self_mall", "sku_id": "about_cffi"},
    # 대체 도메인 (301 리다이렉트 대상)
    {"url": "https://listerine.co.kr/", "vertical": "gargle", "brand": "listerine",
     "channel": "self_mall", "sku_id": "co_kr_cffi"},
    # 퓨런헬스케어
    {"url": "https://furenhealth.com/", "vertical": "medical_device", "brand": "furenhealth",
     "channel": "self_mall", "sku_id": "main_cffi"},
    {"url": "https://www.furenhealth.com/", "vertical": "medical_device", "brand": "furenhealth",
     "channel": "self_mall", "sku_id": "www_cffi"},
]

# Chrome 136 (가장 최신 프로필)
IMPERSONATE = "chrome"
SLEEP = 3.0


@dataclass
class Result:
    url: str
    vertical: str
    brand: str
    channel: str
    sku_id: str
    fetched_at: str
    status: int
    final_url: str
    html_length: int
    sha256: str
    raw_path: str
    error: Optional[str] = None


def main():
    results = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for tgt in TARGETS:
        time.sleep(SLEEP)
        url = tgt["url"]
        print(f"→ {url}")
        raw_dir = DATA_RAW / tgt["vertical"] / tgt["brand"] / tgt["channel"] / today
        raw_dir.mkdir(parents=True, exist_ok=True)

        try:
            r = cffi_requests.get(
                url,
                impersonate=IMPERSONATE,
                timeout=25,
                allow_redirects=True,
                headers={
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                },
            )
            body = r.text
            sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
            filename = f"{tgt['sku_id']}_{sha}_cffi.html"
            raw_path = raw_dir / filename
            raw_path.write_text(body, encoding="utf-8")

            marker = "✅" if len(body) > 5000 else "⚠️"
            print(f"  {marker} HTTP {r.status_code} | {len(body):,} bytes | final={r.url}")

            results.append(Result(
                url=url, vertical=tgt["vertical"], brand=tgt["brand"],
                channel=tgt["channel"], sku_id=tgt["sku_id"],
                fetched_at=datetime.now(timezone.utc).isoformat(),
                status=r.status_code, final_url=r.url,
                html_length=len(body), sha256=sha,
                raw_path=str(raw_path.relative_to(REPO_ROOT)),
            ))
        except Exception as e:
            print(f"  ❌ error: {e}")
            results.append(Result(
                url=url, vertical=tgt["vertical"], brand=tgt["brand"],
                channel=tgt["channel"], sku_id=tgt["sku_id"],
                fetched_at=datetime.now(timezone.utc).isoformat(),
                status=0, final_url="", html_length=0, sha256="",
                raw_path="", error=str(e),
            ))

    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    # 요약
    ok = sum(1 for r in results if r.html_length > 5000)
    print(f"\n{'='*50}\n성공 {ok}/{len(results)} (html > 5KB 기준)")


if __name__ == "__main__":
    main()
