"""
가글 신규 4 브랜드 추가 크롤 (2026-04-25 Wayne 지시).

대상:
  · therabreath — 올리브영 (oliveyoung.co.kr)
  · colgate — 11번가 페록실 (마우스워시)
  · oralb — 올리브영 검색 (한국 가글 SKU 한정)
  · usimol — 이마트몰 (emart.ssg.com)

스킵 (한국 시장 미진출):
  · sensodyne (가글 라인업 부재, 치약만)
  · kwangdong 인후엔 (약국 일반의약품, 온라인 retail 부재)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from curl_cffi import requests as cr

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"
JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "gargle_extra.jsonl"


TARGETS = [
    {"url": "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000136360",
     "vertical": "gargle", "brand": "therabreath", "channel": "oliveyoung",
     "sku_id": "therabreath_473ml"},
    {"url": "https://www.11st.co.kr/products/7396749495",
     "vertical": "gargle", "brand": "colgate", "channel": "11st",
     "sku_id": "colgate_peroxyl_500ml"},
    {"url": "https://www.oliveyoung.co.kr/store/search/getSearchMain.do?query=%EC%98%A4%EB%9E%84%EB%B9%84+%EA%B0%80%EA%B8%80",
     "vertical": "gargle", "brand": "oralb", "channel": "oliveyoung",
     "sku_id": "oralb_search"},
    {"url": "https://emart.ssg.com/item/itemView.ssg?itemId=1000341419223",
     "vertical": "gargle", "brand": "usimol", "channel": "emart_mall",
     "sku_id": "usimol_500ml"},
]


@dataclass
class Result:
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


def crawl_one(tgt: dict) -> Result:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir = DATA_RAW / tgt["vertical"] / tgt["brand"] / tgt["channel"] / today
    raw_dir.mkdir(parents=True, exist_ok=True)
    try:
        r = cr.get(tgt["url"], impersonate="chrome124", timeout=25, allow_redirects=True)
        body = r.text
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
        raw_path = raw_dir / f"{tgt['sku_id']}_{sha}.html"
        raw_path.write_text(body, encoding="utf-8")
        return Result(
            url=tgt["url"], vertical=tgt["vertical"], brand=tgt["brand"],
            channel=tgt["channel"], sku_id=tgt["sku_id"],
            fetched_at=datetime.now(timezone.utc).isoformat(),
            status=r.status_code, content_length=len(body), sha256=sha,
            raw_path=str(raw_path.relative_to(REPO_ROOT)),
        )
    except Exception as e:
        return Result(
            url=tgt["url"], vertical=tgt["vertical"], brand=tgt["brand"],
            channel=tgt["channel"], sku_id=tgt["sku_id"],
            fetched_at=datetime.now(timezone.utc).isoformat(),
            status=0, content_length=0, sha256="", raw_path="",
            error=f"{type(e).__name__}: {str(e)[:100]}",
        )


def main():
    print(f"🎬 가글 추가 크롤 — {len(TARGETS)}개 (therabreath/colgate/oralb/usimol)")
    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for tgt in TARGETS:
            r = crawl_one(tgt)
            marker = "✅" if r.status == 200 and r.content_length > 5000 else "⚠️"
            print(f"{marker} {r.brand:12} / {r.channel:14} sku={r.sku_id}: "
                  f"{r.content_length:,} bytes / HTTP {r.status}")
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
