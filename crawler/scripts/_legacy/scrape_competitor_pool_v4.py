"""
경쟁군 4차 크롤링 — 훌스 스마트스토어 + 코웨이 테라솔 P 상세 URL 확정.

확정 URL:
1. 훌스 HOOL'S 음파방석 → smartstore.naver.com/hilivingmall/products/12549951735
2. 코웨이 테라솔 P → coway.com/product/detail?prdno=1452&optno=1

(테라솔 U는 coway.com 검색 결과에 없음 — 공개 URL 미제공.
 Wayne 요청대로 끝까지 찾았으나 온라인 공개 접근 불가 확인.)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool_v4.jsonl"

TARGETS = [
    {
        "url": "https://smartstore.naver.com/hilivingmall/products/12549951735",
        "vertical": "medical_device",
        "brand": "hools",
        "channel": "smartstore",
        "sku_id": "12549951735",
    },
    {
        "url": "https://www.coway.com/product/detail?prdno=1452&optno=1",
        "vertical": "medical_device",
        "brand": "coway_therasol",
        "channel": "self_mall",
        "sku_id": "therasol_p_detail",
    },
]


def main():
    print(f"🎬 경쟁군 4차 크롤링 — {len(TARGETS)}개")
    results = render_pages(
        TARGETS,
        wait_for="networkidle",
        timeout_ms=60000,
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
