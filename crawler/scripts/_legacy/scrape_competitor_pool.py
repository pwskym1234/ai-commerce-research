"""
본실험 경쟁군 N=14 크롤링 — 추가 5~6 브랜드.

기존 완료:
  바디닥터, 이지케이(coreatech), 세라젬, 퓨런, 닥터케이(제거됨 — 별건 브랜드)

이번 추가:
  - 코웨이 테라솔 U (coway.co.kr)
  - 웨이브케어 V8 (regenestyle.com — 리진바이오)
  - 케겔매직 (kegelmagic.co.kr)
  - 휴온센 EMS 레깅스 (11st)
  - 애플힙 (gsshop)

URL 미확보 (Wayne 요청):
  - 페로니언
  - 훌스 음파방석
  - 스탑요 자동 케겔
  - EMS케겔휘트니스 비틀
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool.jsonl"

TARGETS = [
    # 코웨이 테라솔 U
    {
        "url": "https://www.coway.co.kr/search/SearchResult?keyword=%ED%85%8C%EB%9D%BC%EC%86%94",
        "vertical": "medical_device",
        "brand": "coway_therasol",
        "channel": "self_mall",
        "sku_id": "search",
    },
    # 웨이브케어 V8 (리진바이오 공식)
    {
        "url": "https://regenestyle.com",
        "vertical": "medical_device",
        "brand": "wavecare",
        "channel": "self_mall",
        "sku_id": "main",
    },
    # 케겔매직 공식
    {
        "url": "http://www.kegelmagic.co.kr/",
        "vertical": "medical_device",
        "brand": "kegel_magic",
        "channel": "self_mall",
        "sku_id": "main",
    },
    # 휴온센 EMS 레깅스 11번가
    {
        "url": "https://www.11st.co.kr/products/7374687035",
        "vertical": "medical_device",
        "brand": "huonsen",
        "channel": "11st",
        "sku_id": "7374687035",
    },
    # 애플힙 2026 GSshop
    {
        "url": "https://www.gsshop.com/search/searchSect.gs?tq=%EC%95%A0%ED%94%8C%ED%9E%99",
        "vertical": "medical_device",
        "brand": "applehip",
        "channel": "gsshop",
        "sku_id": "search",
    },
]


def main():
    print(f"🎬 경쟁군 추가 크롤링 — {len(TARGETS)}개")
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

    print(f"\n다음: python crawler/scripts/extract_features.py && python crawler/scripts/sixthshop_score.py")


if __name__ == "__main__":
    main()
