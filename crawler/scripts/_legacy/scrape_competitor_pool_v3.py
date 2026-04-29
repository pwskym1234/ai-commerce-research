"""
경쟁군 3차 크롤링 — 훌스·케겔매직·코웨이 테라솔 P.

확보된 URL:
1. 훌스 HOOL'S 음파방석 (네이버 스마트스토어 단축 URL, 하이리빙몰 판매)
2. 케겔매직 11번가
3. 코웨이 테라솔 P (productId 1452, coway.com)
   - 테라솔 U는 coway.com에 상세 URL 미공개, 테라솔 P로 대체
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool_v3.jsonl"

TARGETS = [
    # 훌스 음파방석 — 네이버 스마트스토어 (하이리빙몰, 799,000원)
    {
        "url": "https://naver.me/5kPKhrYo",
        "vertical": "medical_device",
        "brand": "hools",
        "channel": "smartstore",
        "sku_id": "5kPKhrYo",
    },
    # 케겔매직 — 11번가 (286,000원, 여성 케겔 의료기기)
    {
        "url": "https://www.11st.co.kr/products/2467230526",
        "vertical": "medical_device",
        "brand": "kegel_magic",
        "channel": "11st",
        "sku_id": "2467230526",
    },
    # 코웨이 테라솔 P — productId 1452 (1,690,000원 일시불, 월 12,950원 렌탈)
    # 테라솔 U는 coway.com 검색 결과에 없음 — 오프라인 채널 전용 가능성
    {
        "url": "https://www.coway.com/Product/BrandProductDetail?productId=1452",
        "vertical": "medical_device",
        "brand": "coway_therasol",
        "channel": "self_mall",
        "sku_id": "therasol_p_1452",
    },
]


def main():
    print(f"🎬 경쟁군 3차 크롤링 — {len(TARGETS)}개")
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
