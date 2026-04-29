"""
네이버 스마트스토어 크롤러 (smartstore.naver.com).

대상:
- 바디닥터: smartstore.naver.com/gncosshop
- 프로폴린스: smartstore.naver.com/gncosshop (같은 입점)
- 가그린: smartstore.naver.com/dapharm 또는 동아제약 채널
- 페리오: smartstore.naver.com/lghnh 또는 LG생활건강 채널
- 2080: smartstore.naver.com/aekyung 또는 애경 채널

⚠️ 주의:
- 네이버 스마트스토어는 JS 동적 렌더링이 심함 → requests로는 빈 결과 가능
- 본격 수집은 Playwright/Selenium으로 전환 필요
- 이 파일은 1차 정적 fetch로 어디까지 잡히는지 확인하는 용도

대안: 네이버 쇼핑 OpenAPI (developers.naver.com) 사용 — 카테고리/SKU 메타데이터를 정식 API로 수집
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import fetch, append_jsonl, REPO_ROOT  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "naver_smartstore.jsonl"

# 1차 정적 fetch 대상
TARGETS = [
    # (vertical, brand, channel, store_id, sku_path or None)
    ("medical_device", "bodydoctor", "smartstore", "gncosshop", None),  # 스토어 메인
    ("gargle", "propolinse", "smartstore", "gncosshop", None),
]


def main():
    for vertical, brand, channel, store_id, sku_path in TARGETS:
        url = f"https://smartstore.naver.com/{store_id}"
        if sku_path:
            url += f"/{sku_path}"
        result = fetch(
            url=url,
            vertical=vertical,
            brand=brand,
            channel=channel,
            sku_id=store_id,
        )
        marker = "✅" if result.status == 200 else "❌"
        print(f"{marker} [{result.status}] {brand}/{channel}: {url}")
        append_jsonl(JSONL_PATH, result)
        if result.status == 200 and result.content_length < 5000:
            print(f"   ⚠️ 응답 짧음 ({result.content_length} bytes) — JS 렌더링 필요할 가능성")


if __name__ == "__main__":
    main()
