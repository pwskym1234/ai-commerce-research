"""
크롤러 공통 베이스 모듈.

원칙 (CLAUDE.md §8):
- raw HTML은 data/raw/<vertical>/<brand>/<channel>/<date>/ 에 저장 (불변)
- 정제·피처 추출은 data/processed/ 에서
- robots.txt 준수, User-Agent 명시, 요청 간 sleep
- 결과 메타데이터 jsonl로 함께 저장 (URL, 시각, 응답 코드, hash)
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
USER_AGENT = "AiEO-Research-Crawler/0.1 (academic research; nanonaeofficial@gmail.com)"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}
SLEEP_BETWEEN_REQUESTS = 2.0  # 매 요청 간 2초


@dataclass
class CrawlResult:
    url: str
    vertical: str           # medical_device | gargle
    brand: str              # bodydoctor | easyk | propolinse | listerine | ...
    channel: str            # gncosshop | smartstore | coupang | self_mall | ...
    sku_id: Optional[str]   # product_no 등
    fetched_at: str
    status: int
    content_length: int
    sha256: str
    raw_path: str
    error: Optional[str] = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def fetch(
    url: str,
    *,
    vertical: str,
    brand: str,
    channel: str,
    sku_id: Optional[str] = None,
    extra_headers: Optional[dict] = None,
) -> CrawlResult:
    """단일 URL fetch 후 raw 저장 + CrawlResult 반환."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir = DATA_RAW / vertical / brand / channel / today
    raw_dir.mkdir(parents=True, exist_ok=True)

    headers = {**DEFAULT_HEADERS, **(extra_headers or {})}

    try:
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        body = r.text
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
        filename = f"{sku_id or 'page'}_{sha}.html"
        raw_path = raw_dir / filename
        raw_path.write_text(body, encoding="utf-8")

        return CrawlResult(
            url=url,
            vertical=vertical,
            brand=brand,
            channel=channel,
            sku_id=sku_id,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            status=r.status_code,
            content_length=len(body),
            sha256=sha,
            raw_path=str(raw_path.relative_to(REPO_ROOT)),
        )
    except Exception as e:
        return CrawlResult(
            url=url,
            vertical=vertical,
            brand=brand,
            channel=channel,
            sku_id=sku_id,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            status=0,
            content_length=0,
            sha256="",
            raw_path="",
            error=str(e),
        )


def append_jsonl(jsonl_path: Path, result: CrawlResult) -> None:
    """크롤링 메타데이터를 jsonl에 한 줄 append."""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(result.to_jsonl() + "\n")
