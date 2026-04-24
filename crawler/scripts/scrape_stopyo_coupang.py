"""
스탑요 쿠팡 크롤 — Playwright stealth (쿠팡 Akamai Bot Manager 우회).

Wayne 제공 URL: https://www.coupang.com/vp/products/8637377284

curl_cffi Chrome124는 쿠팡에서 403 — Akamai는 헤더·TLS 외에 브라우저 JS 실행·
canvas 핑거프린트 검사. Playwright full browser + stealth 필요.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "stopyo.jsonl"

TARGETS = [
    {
        "url": "https://www.coupang.com/vp/products/8637377284",
        "vertical": "medical_device",
        "brand": "stopyo",
        "channel": "coupang",
        "sku_id": "8637377284",
    },
]


def main():
    print(f"🎬 스탑요 쿠팡 크롤 — Playwright stealth")
    results = render_pages(
        TARGETS,
        wait_for="domcontentloaded",
        timeout_ms=40000,
        screenshot=False,
        stealth=True,
    )
    for r in results:
        marker = "✅" if r.html_length > 5000 else "⚠️"
        status = f"{r.html_length:,} bytes" if r.html_length else f"error: {r.error}"
        print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
        append_jsonl(JSONL_PATH, r)


if __name__ == "__main__":
    main()
