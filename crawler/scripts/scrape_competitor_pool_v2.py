"""
경쟁군 N=14 2차 크롤링 — 확보된 URL 5개.

1. 페로니언 부부사랑 케겔 운동기 (11번가)
2. EMS케겔휘트니스 비틀 (d'ARLI)
3. 애플힙 2026 (카카오스토어)
4. 케겔매직 (overview.php)
5. 코웨이 테라솔 U (코웨이 검색)

URL 미확보 (마이너 공산품, 일반 검색 안 잡힘):
- 훌스 HOOL'S 음파방석
- 스탑요 자동 케겔
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool_v2.jsonl"

TARGETS = [
    # 페로니언 11번가 (333,000원, 일시품절)
    {
        "url": "https://m.11st.co.kr/products/m/4171005345",
        "vertical": "medical_device",
        "brand": "peronian",
        "channel": "11st",
        "sku_id": "4171005345",
    },
    # EMS케겔휘트니스 비틀 — d'ARLI 브랜드
    {
        "url": "https://www.darli.kr/21/?idx=2",
        "vertical": "medical_device",
        "brand": "ems_vital",
        "channel": "darli",
        "sku_id": "2",
    },
    # 애플힙 2026 카카오스토어
    {
        "url": "https://store.kakao.com/apapa/products/237396165",
        "vertical": "medical_device",
        "brand": "applehip",
        "channel": "kakao_store",
        "sku_id": "237396165",
    },
    # 케겔매직 — overview.php
    {
        "url": "http://www.kegelmagic.co.kr/overview.php",
        "vertical": "medical_device",
        "brand": "kegel_magic",
        "channel": "self_mall",
        "sku_id": "overview",
    },
    # 코웨이 테라솔 U — 공식 검색 (제품 상세 URL 불명)
    {
        "url": "https://www.coway.co.kr/product/bidet/",
        "vertical": "medical_device",
        "brand": "coway_therasol",
        "channel": "self_mall",
        "sku_id": "bidet_cat",
    },
]


def main():
    print(f"🎬 경쟁군 2차 크롤링 — {len(TARGETS)}개")
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
