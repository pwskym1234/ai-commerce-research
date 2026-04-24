"""
Elvie Trainer 공식 페이지 크롤.

배경:
- 경쟁군 N=14 중 해외 1종 = Elvie (영국 브랜드, 글로벌 대표 Kegel 트레이너).
- 글로벌 편향 측정용 — 한국 AI가 Elvie를 추천하는 빈도가 F/H10 검정에 의미 있음.

URL: https://elvie.com/products/elvie-trainer (Shopify 상점, 정적 HTML 응답 가능)
접근: curl_cffi Chrome124 임퍼소네이트 (일반 Cloudflare 없음, Shopify 기본 보호만)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import append_jsonl, REPO_ROOT

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from curl_cffi import requests as cr

DATA_RAW = REPO_ROOT / "data" / "raw"
JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "elvie.jsonl"

TARGETS = [
    {
        "url": "https://elvie.com/products/elvie-trainer",
        "vertical": "medical_device",
        "brand": "elvie",
        "channel": "official_global",
        "sku_id": "elvie_trainer",
    },
]


@dataclass
class SimpleResult:
    url: str
    vertical: str
    brand: str
    channel: str
    sku_id: Optional[str]
    fetched_at: str
    status: int
    content_length: int
    sha256: str
    raw_path: str
    error: Optional[str] = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🎬 Elvie Trainer 크롤 — {len(TARGETS)}개")
    for tgt in TARGETS:
        raw_dir = DATA_RAW / tgt["vertical"] / tgt["brand"] / tgt["channel"] / today
        raw_dir.mkdir(parents=True, exist_ok=True)
        try:
            r = cr.get(tgt["url"], impersonate="chrome124", timeout=30, allow_redirects=True)
            body = r.text
            sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
            filename = f"{tgt['sku_id']}_{sha}.html"
            raw_path = raw_dir / filename
            raw_path.write_text(body, encoding="utf-8")
            res = SimpleResult(
                url=tgt["url"],
                vertical=tgt["vertical"],
                brand=tgt["brand"],
                channel=tgt["channel"],
                sku_id=tgt["sku_id"],
                fetched_at=datetime.now(timezone.utc).isoformat(),
                status=r.status_code,
                content_length=len(body),
                sha256=sha,
                raw_path=str(raw_path.relative_to(REPO_ROOT)),
            )
            marker = "✅" if res.status == 200 and res.content_length > 5000 else "⚠️"
            print(f"{marker} {res.brand}/{res.channel} sku={res.sku_id}: {res.content_length:,} bytes / HTTP {res.status}")
        except Exception as e:
            res = SimpleResult(
                url=tgt["url"],
                vertical=tgt["vertical"],
                brand=tgt["brand"],
                channel=tgt["channel"],
                sku_id=tgt["sku_id"],
                fetched_at=datetime.now(timezone.utc).isoformat(),
                status=0,
                content_length=0,
                sha256="",
                raw_path="",
                error=str(e),
            )
            print(f"❌ {res.brand}/{res.channel}: {e}")
        # append_jsonl expects CrawlResult-like — our SimpleResult has same to_jsonl
        JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with JSONL_PATH.open("a", encoding="utf-8") as f:
            f.write(res.to_jsonl() + "\n")


if __name__ == "__main__":
    main()
