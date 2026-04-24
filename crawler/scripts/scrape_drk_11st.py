"""
닥터케이 11번가 제품 페이지 크롤링.

URL: https://www.11st.co.kr/products/2444307960
제품: "닥터케이 저주파 EMS 케겔 요실금 질수축 질탄력 여성기구 괄약근 골반근육 골반저근"
가격: 198,000원 (Wayne 진단 리포트 경쟁군)
카테고리: 공산품 저주파자극기 (의료기기 아님 추정 — H10 검정 대상)

11번가 특성:
- JS 동적 렌더링 심함
- 봇 차단 약함 (대체로 Playwright 기본으로 통과)
- 리뷰·Q&A는 별도 AJAX 로드 — 상품 상세는 본 페이지에 있음

사용법:
  python crawler/scripts/scrape_drk_11st.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "drk_11st.jsonl"

TARGETS = [
    {
        "url": "https://www.11st.co.kr/products/2444307960",
        "vertical": "medical_device",
        "brand": "drk",
        "channel": "11st",
        "sku_id": "2444307960",
    },
]


def main():
    print(f"🎬 닥터케이 11번가 크롤링")
    results = render_pages(
        TARGETS,
        wait_for="domcontentloaded",
        timeout_ms=40000,
        screenshot=True,          # Wayne 시각 확인용
        stealth=True,
    )
    for r in results:
        marker = "✅" if r.html_length > 5000 else "⚠️"
        status = f"{r.html_length:,} bytes" if r.html_length else f"error: {r.error}"
        print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
        append_jsonl(JSONL_PATH, r)

    # feature + sixthshop 바로 재계산 권고
    print(f"\n다음 단계:")
    print(f"  python crawler/scripts/extract_features.py   # 피처 재추출")
    print(f"  python crawler/scripts/sixthshop_score.py    # Sixthshop 점수 재계산")


if __name__ == "__main__":
    main()
