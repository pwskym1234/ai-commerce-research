"""
stealth 재시도 — 이전 bot 차단된 URL들.

차단된 대상 (2026-04-24 1차 시도):
- listerine.kr / listerine.kr/products/gum-care-mild (가글)
- furenhealth.com (의료기기)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT, STEALTH_AVAILABLE  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "stealth_retry.jsonl"

TARGETS = [
    {
        "url": "https://www.listerine.kr/",
        "vertical": "gargle",
        "brand": "listerine",
        "channel": "self_mall",
        "sku_id": "main_stealth",
    },
    {
        "url": "https://www.listerine.kr/products/gum-care-mild",
        "vertical": "gargle",
        "brand": "listerine",
        "channel": "self_mall",
        "sku_id": "gum-care-mild_stealth",
    },
    {
        "url": "https://www.furenhealth.com",
        "vertical": "medical_device",
        "brand": "furenhealth",
        "channel": "self_mall",
        "sku_id": "main_stealth",
    },
]


def main():
    print(f"playwright-stealth 사용 가능: {STEALTH_AVAILABLE}")
    print(f"🎬 stealth 재시도 — {len(TARGETS)} URL")
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
