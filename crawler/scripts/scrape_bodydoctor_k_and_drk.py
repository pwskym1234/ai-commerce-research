"""
바디닥터 K (idx=24) + 닥터케이 추가 크롤.

배경 (2026-04-26 GN 피드백):
  · GN 대표 의도: 바디닥터 K = 의료기기 아닌 일반 건강보조 운동기구 (마케팅 제한 X)
  · 바디닥터 K = 케겔 힙머신 (EMS 자동 케겔 + 엉덩이근 강화)
  · 닥터케이 = 별개 브랜드, K anchor 시 직접 경쟁군

K 페이지 URL:
  · 공식: https://www.bodydoctor.co.kr/product/list2?viewMode=view&idx=24

닥터케이 URL:
  · 11번가: https://www.11st.co.kr/products/2444307960
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
JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "bodydoctor_k_drk.jsonl"


TARGETS = [
    {"url": "https://www.bodydoctor.co.kr/product/list2?viewMode=view&idx=24",
     "vertical": "kegel_exerciser", "brand": "bodydoctor_k", "channel": "bodydoctor_official",
     "sku_id": "kegel_hipmachine_idx24"},
    {"url": "https://www.11st.co.kr/products/2444307960",
     "vertical": "kegel_exerciser", "brand": "drk", "channel": "11st",
     "sku_id": "drk_lowfreq_kegel"},
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
    print(f"🎬 바디닥터 K + 닥터케이 크롤 — {len(TARGETS)}개")
    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for tgt in TARGETS:
            r = crawl_one(tgt)
            marker = "✅" if r.status == 200 and r.content_length > 5000 else "⚠️"
            print(f"{marker} {r.brand:18} / {r.channel:20} sku={r.sku_id}: "
                  f"{r.content_length:,} bytes / HTTP {r.status}")
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
