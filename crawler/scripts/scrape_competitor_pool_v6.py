"""
경쟁군 6차 크롤링 — 훌스 대체 채널(하이리빙 공식몰).

배경:
- 훌스 음파방석은 네이버 스마트스토어(hilivingmall) 전용 → 네이버 로그인 벽.
- wowoo.co.kr 리뷰 확인: 11번가/쿠팡/지마켓에 공식 채널 없음.
- 브랜드 "훌스(HOOL'S)"는 네이버 스마트스토어 전용 작명, 제조사는 (주)하이리빙.
- 하이리빙 공식몰(www.hiliving.co.kr)에 동일 제품 "음파방석" 확인 (이벤트 1233, code=300751).
- 하이리빙 공식몰은 로그인 불요 + curl_cffi(Chrome TLS) 없이도 접근 가능.

한계:
- 공식몰 페이지는 "훌스" 브랜드명 노출 안 함 → AI가 "훌스"로 추천할지 vs "하이리빙 음파방석"으로 할지는 응답 단계에서 확인.
- 상세 가격은 회원가 기준으로 일부 가려질 가능성 (페이지 공개 텍스트에서 50,000원 = 사은품 가격만 노출).

대표 SKU: code=300751 (음파방석_HPUP,멀티백증정 본품 이벤트).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import fetch, append_jsonl, REPO_ROOT

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "competitor_pool_v6.jsonl"

CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
BROWSER_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TARGETS = [
    {
        "url": "https://www.hiliving.co.kr/goods/detail?code=300751",
        "vertical": "medical_device",
        "brand": "hools",
        "channel": "hiliving_mall",
        "sku_id": "hools_sonic_300751",
    },
]


def main():
    print(f"🎬 경쟁군 6차 크롤링 (훌스 공식 제조사몰) — {len(TARGETS)}개")
    for tgt in TARGETS:
        r = fetch(
            tgt["url"],
            vertical=tgt["vertical"],
            brand=tgt["brand"],
            channel=tgt["channel"],
            sku_id=tgt["sku_id"],
            extra_headers=BROWSER_HEADERS,
        )
        marker = "✅" if r.content_length > 5000 and r.status == 200 else "⚠️"
        status = f"{r.content_length:,} bytes / HTTP {r.status}" if r.content_length else f"error: {r.error}"
        print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
        append_jsonl(JSONL_PATH, r)


if __name__ == "__main__":
    main()
