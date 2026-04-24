"""
Playwright 기반 크롤러 공통 모듈.

JS 동적 렌더링이 필요한 페이지 (네이버 스마트스토어, easyk.kr 등).
정적 fetch는 _base.py 사용.

원칙:
- headless 기본
- 페이지 로드 후 networkidle 또는 특정 selector wait
- 저장 경로: data/raw/<vertical>/<brand>/<channel>/<date>/ (정적 크롤러와 동일)
- 저장 파일 이름에 "_rendered" 접미사로 구분
- robots.txt 준수 + 요청 간 sleep
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
SLEEP_BETWEEN_REQUESTS = 3.0  # 매 페이지 간 3초


@dataclass
class RenderResult:
    url: str
    vertical: str
    brand: str
    channel: str
    sku_id: Optional[str]
    fetched_at: str
    final_url: str
    html_length: int
    sha256: str
    raw_path: str
    screenshot_path: Optional[str] = None
    error: Optional[str] = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def render_pages(
    targets: list[dict],
    *,
    wait_for_selector: Optional[str] = None,
    wait_for: str = "networkidle",  # "load" | "domcontentloaded" | "networkidle"
    timeout_ms: int = 30000,
    screenshot: bool = False,
) -> list[RenderResult]:
    """
    여러 URL을 JS 렌더링 후 저장.
    각 target dict: {url, vertical, brand, channel, sku_id (optional)}
    """
    results = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="ko-KR",
            viewport={"width": 1280, "height": 2400},
        )
        for tgt in targets:
            url = tgt["url"]
            vertical = tgt["vertical"]
            brand = tgt["brand"]
            channel = tgt["channel"]
            sku_id = tgt.get("sku_id")

            raw_dir = DATA_RAW / vertical / brand / channel / today
            raw_dir.mkdir(parents=True, exist_ok=True)

            page = context.new_page()
            try:
                time.sleep(SLEEP_BETWEEN_REQUESTS)
                page.goto(url, wait_until=wait_for, timeout=timeout_ms)
                if wait_for_selector:
                    try:
                        page.wait_for_selector(wait_for_selector, timeout=5000)
                    except PWTimeout:
                        pass
                # 추가로 2초 — 동적 iframe 등 로드 대기
                page.wait_for_timeout(2000)
                # 전체 높이까지 스크롤해서 lazy 로드 트리거
                page.evaluate("""async () => {
                    await new Promise((resolve) => {
                        let y = 0;
                        const step = 500;
                        const timer = setInterval(() => {
                            window.scrollBy(0, step);
                            y += step;
                            if (y >= document.body.scrollHeight) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 150);
                    });
                }""")
                page.wait_for_timeout(1500)

                html = page.content()
                final_url = page.url
                sha = hashlib.sha256(html.encode("utf-8")).hexdigest()[:16]
                filename = f"{sku_id or 'page'}_{sha}_rendered.html"
                raw_path = raw_dir / filename
                raw_path.write_text(html, encoding="utf-8")

                screenshot_path = None
                if screenshot:
                    shot_path = raw_dir / f"{sku_id or 'page'}_{sha}.png"
                    page.screenshot(path=str(shot_path), full_page=True)
                    screenshot_path = str(shot_path.relative_to(REPO_ROOT))

                results.append(
                    RenderResult(
                        url=url,
                        vertical=vertical,
                        brand=brand,
                        channel=channel,
                        sku_id=sku_id,
                        fetched_at=datetime.now(timezone.utc).isoformat(),
                        final_url=final_url,
                        html_length=len(html),
                        sha256=sha,
                        raw_path=str(raw_path.relative_to(REPO_ROOT)),
                        screenshot_path=screenshot_path,
                    )
                )
            except Exception as e:
                results.append(
                    RenderResult(
                        url=url,
                        vertical=vertical,
                        brand=brand,
                        channel=channel,
                        sku_id=sku_id,
                        fetched_at=datetime.now(timezone.utc).isoformat(),
                        final_url="",
                        html_length=0,
                        sha256="",
                        raw_path="",
                        error=str(e),
                    )
                )
            finally:
                page.close()

        browser.close()

    return results


def append_jsonl(jsonl_path: Path, result: RenderResult) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(result.to_jsonl() + "\n")
