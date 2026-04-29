"""
5차 시도 — 실제 시스템 Chrome(channel='chrome')로 JS 렌더링.

curl_cffi는 TLS를 뚫었지만 listerine.kr은 SPA라 초기 HTML에
본문/리뷰 위젯이 안 담김. 이번엔 Chrome channel을 써서 Playwright의
내장 Chromium 대신 실제 Chrome의 TLS fingerprint로 시도.

목표:
- 렌더링 후 DOM에서 F1 spec format, Bazaarvoice 리뷰 위젯, 평점/건수
- 실패 시 에러만 기록하고 기존 curl_cffi 결과로 확정
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
JSONL_PATH = DATA_RAW / "_index" / "chrome_channel_rendered.jsonl"

TARGETS = [
    {"url": "https://www.listerine.kr/products/gum-care-mild",
     "vertical": "gargle", "brand": "listerine", "channel": "self_mall",
     "sku_id": "gum-care-mild_chrome"},
    {"url": "https://www.listerine.kr/products/greentea-mild",
     "vertical": "gargle", "brand": "listerine", "channel": "self_mall",
     "sku_id": "greentea-mild_chrome"},
]


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []

    with sync_playwright() as p:
        try:
            # 실제 Chrome 사용 — Cloudflare TLS 우회 효과
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception as e:
            print(f"❌ Chrome channel 실패, chromium으로 폴백: {e}")
            browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/136.0.0.0 Safari/537.36"),
            locale="ko-KR",
            viewport={"width": 1440, "height": 2800},
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        for tgt in TARGETS:
            time.sleep(3)
            url = tgt["url"]
            print(f"→ {url}")
            raw_dir = DATA_RAW / tgt["vertical"] / tgt["brand"] / tgt["channel"] / today
            raw_dir.mkdir(parents=True, exist_ok=True)

            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
                # lazy-load 트리거
                page.evaluate("""async () => {
                    await new Promise((resolve) => {
                        let y = 0;
                        const step = 600;
                        const timer = setInterval(() => {
                            window.scrollBy(0, step);
                            y += step;
                            if (y >= document.body.scrollHeight) {
                                clearInterval(timer); resolve();
                            }
                        }, 200);
                    });
                }""")
                page.wait_for_timeout(3000)

                html = page.content()
                final_url = page.url
                sha = hashlib.sha256(html.encode("utf-8")).hexdigest()[:16]
                filename = f"{tgt['sku_id']}_{sha}_chrome.html"
                raw_path = raw_dir / filename
                raw_path.write_text(html, encoding="utf-8")

                # 리뷰 위젯 영역 별도 스크린샷
                try:
                    bv = page.locator("[data-bv-show], .bv-cv2, .bv-reviews, [class*='bazaarvoice']").first
                    if bv.count() > 0:
                        shot = raw_dir / f"{tgt['sku_id']}_reviews.png"
                        bv.screenshot(path=str(shot))
                        print(f"  📸 리뷰 위젯 스크린샷: {shot.name}")
                except Exception:
                    pass

                marker = "✅" if len(html) > 10000 else "⚠️"
                print(f"  {marker} {len(html):,} bytes | final={final_url}")
                results.append({
                    "url": url, "status": "ok", "html_length": len(html),
                    "final_url": final_url, "raw_path": str(raw_path.relative_to(REPO_ROOT)),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                print(f"  ❌ {e}")
                results.append({"url": url, "status": "error", "error": str(e)})
            finally:
                page.close()

        browser.close()

    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
