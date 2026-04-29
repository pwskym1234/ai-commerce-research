"""
가글 버티컬 경쟁사 JS 렌더링 크롤링.

대상 (본실험 N=6 권고):
1. 프로폴린스 (우리) — propolinse.co.kr (이미 정적 fetch 완료, 재확인)
2. 리스테린 — listerine.kr
3. 가그린 — dmall.co.kr/brands/garglin + dapharm.com
4. 페리오 — lghnh.com
5. 2080 — 자사몰 약함, SSG/쿠팡 대표 SKU
+ 해외: 콜게이트 / 테라브레스 (선택)

⚠️ 의료기기 버티컬은 별도: scrape_medical_device_rendered.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "gargle_rendered.jsonl"

TARGETS = [
    # === 프로폴린스 (우리 anchor) ===
    {
        "url": "https://propolinse.co.kr",
        "vertical": "gargle",
        "brand": "propolinse",
        "channel": "self_mall",
        "sku_id": "main",
    },
    # === 리스테린 한국 ===
    {
        "url": "https://www.listerine.kr/",
        "vertical": "gargle",
        "brand": "listerine",
        "channel": "self_mall",
        "sku_id": "main",
    },
    {
        "url": "https://www.listerine.kr/products/gum-care-mild",
        "vertical": "gargle",
        "brand": "listerine",
        "channel": "self_mall",
        "sku_id": "gum-care-mild",
    },
    # === 가그린 ===
    {
        "url": "https://www.dapharm.com/ko/brand/contents/OCG",
        "vertical": "gargle",
        "brand": "garglin",
        "channel": "manufacturer_site",
        "sku_id": "brand",
    },
    {
        "url": "https://dmall.co.kr/product/가그린-오리지널-100ml/41/",
        "vertical": "gargle",
        "brand": "garglin",
        "channel": "dmall",
        "sku_id": "41",
    },
    # === 페리오 ===
    {
        "url": "https://www.lghnh.com/brand/detail.jsp?gbn=2&bid1=H021",
        "vertical": "gargle",
        "brand": "perio",
        "channel": "manufacturer_site",
        "sku_id": "brand",
    },
    # === 2080 — 자사몰 약해서 SSG 대표 상품 ===
    {
        "url": "https://www.ssg.com/item/itemView.ssg?itemId=1000064922816",
        "vertical": "gargle",
        "brand": "2080",
        "channel": "ssg",
        "sku_id": "1000064922816",
    },
]


def main():
    print(f"🎬 Playwright 렌더링 시작 — {len(TARGETS)} URL (가글 버티컬)")
    results = render_pages(TARGETS, wait_for="domcontentloaded", timeout_ms=30000, screenshot=False)
    for r in results:
        marker = "✅" if r.html_length > 5000 else "⚠️"
        status = f"{r.html_length:,} bytes" if r.html_length else f"error: {r.error}"
        print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
        append_jsonl(JSONL_PATH, r)


if __name__ == "__main__":
    main()
