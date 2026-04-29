"""
경쟁군 5차 크롤링 — 훌스 스마트스토어 재시도 (networkidle → domcontentloaded).

v4에서 훌스 smartstore URL이 networkidle 조건으로 timeout (60s).
네이버 스마트스토어는 백그라운드 AJAX 폴링이 계속 돌아서 idle에 절대 도달 안 함.
→ domcontentloaded + 충분한 wait_for_timeout 으로 전환.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool_v5.jsonl"

TARGETS = [
    {
        "url": "https://smartstore.naver.com/hilivingmall/products/12549951735",
        "vertical": "medical_device",
        "brand": "hools",
        "channel": "smartstore",
        "sku_id": "12549951735",
    },
]


def main():
    print(f"🎬 경쟁군 5차 크롤링 (hools 재시도) — {len(TARGETS)}개")
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
