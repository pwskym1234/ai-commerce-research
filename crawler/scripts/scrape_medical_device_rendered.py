"""
의료기기 버티컬 경쟁사 JS 렌더링 크롤링.

대상 (본실험 N=6 권고):
1. 바디닥터 (재크롤링) — 제품 상세 JS 동적 로드 확인
2. 알파메딕 EASY-K (이지케이) — easyk.kr + coreatech-rental.com
3. 세라젬 — 자사몰
4. 퓨런헬스케어 — 자사몰
+ 노이즈: 애플힙 (선택)
+ 해외: Elvie 한국 (선택)

⚠️ 가글 버티컬은 별도 스크립트: scrape_gargle_rendered.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _playwright_base import render_pages, append_jsonl, REPO_ROOT  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "medical_device_rendered.jsonl"

TARGETS = [
    # === 세라젬 ===
    {
        "url": "https://www.ceragem.com",
        "vertical": "medical_device",
        "brand": "ceragem",
        "channel": "self_mall",
        "sku_id": "main",
    },
    # === 퓨런헬스케어 ===
    {
        "url": "https://www.furenhealth.com",
        "vertical": "medical_device",
        "brand": "furenhealth",
        "channel": "self_mall",
        "sku_id": "main",
    },
]

# 이미 크롤링 완료 (이전 실행):
# - bodydoctor gncosshop product_no=187 (✅ 2026-04-24)
# - easyk coreatech product 415 (✅ 2026-04-24)
# - easyk self_mall (❌ DNS 실패 — 별도 확인 필요)


def main():
    print(f"🎬 Playwright 렌더링 시작 — {len(TARGETS)} URL")
    results = render_pages(TARGETS, wait_for="domcontentloaded", timeout_ms=30000, screenshot=False)
    for r in results:
        marker = "✅" if r.html_length > 5000 else "⚠️"
        status = f"{r.html_length:,} bytes" if r.html_length else f"error: {r.error}"
        print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
        append_jsonl(JSONL_PATH, r)


if __name__ == "__main__":
    main()
