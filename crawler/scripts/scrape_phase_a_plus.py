"""
Phase A+ 추가 크롤 — 진짜 경쟁군만 검증된 SKU 6개.

Wayne 지시(2026-04-25): "대충 연관된 거 긁지 말고 진짜 카테고리 제품만"

검증 통과:
1. 바디닥터 GN코스몰 product_no 187 (요실금치료기 단품, 의료기기)
2. 바디닥터 GN코스몰 product_no 210 (요실금치료기+좌훈기+허리벨트 3종 세트)
3. 어썸쿨 가글 600ml — awesomecool.co.kr 자사몰
4. 유시몰 가글 500ml — LG생활건강 가족몰
5. 테라브레스 오랄린스 마일드 민트 — 11번가 (한국 공식몰 DNS 실패 → retail 대체)
6. 엠비랩 ReTens (Retens2 R2) — mblab.kr 자사몰

검증 실패로 스킵 (진짜 경쟁군 아님):
- 썬텍메디칼 / 비엠씨 / 유진플러스 / 리모트솔루션 / 펠비케어 (B2B 또는 한국 미진출)
- 쉬엔비 (자사몰 있지만 요실금 제품 미공개, 다른 의료 카테고리)
- 콜게이트 / 오랄비 / 센소다인 가글 (한국 가글 SKU 명확 부재)
- 광동 인후엔 (약국 일반의약품, 온라인 채널 미확인)
- 청우메디칼 베리얀30 (자사몰 미공개)
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
JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "phase_a_plus.jsonl"


TARGETS = [
    {"url": "https://gncosshop.com/product/detail.html?product_no=187&cate_no=26",
     "vertical": "medical_device", "brand": "bodydoctor", "channel": "gncosshop",
     "sku_id": "bodydoctor_gn_187"},
    {"url": "https://gncosshop.com/product/detail.html?product_no=210&cate_no=26",
     "vertical": "medical_device", "brand": "bodydoctor", "channel": "gncosshop",
     "sku_id": "bodydoctor_gn_210_set"},
    {"url": "https://awesomecool.co.kr/product/%EC%96%B4%EC%8D%B8%EC%BF%A8-%EA%B0%80%EA%B8%80-600ml-%EB%8C%80%EC%9A%A9%EB%9F%89/21/category/1/display/2/",
     "vertical": "gargle", "brand": "awesomecool", "channel": "self_mall",
     "sku_id": "awesomecool_600ml"},
    {"url": "https://www.lgcaremall.com/product/detail/S10003279",
     "vertical": "gargle", "brand": "usimol", "channel": "lgcaremall",
     "sku_id": "usimol_500ml"},
    {"url": "https://www.11st.co.kr/products/2817933676",
     "vertical": "gargle", "brand": "therabreath", "channel": "11st",
     "sku_id": "therabreath_473_2pk"},
    {"url": "http://mblab.kr/",
     "vertical": "medical_device", "brand": "mblab", "channel": "self_mall",
     "sku_id": "mblab_retens"},
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
        # 11번가는 Akamai 가능성 → 첫 시도 후 실패 시 mobile UA 시도 안 함 (그냥 기록)
        r = cr.get(tgt["url"], impersonate="chrome124", timeout=25, allow_redirects=True)
        body = r.text
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
        filename = f"{tgt['sku_id']}_{sha}.html"
        raw_path = raw_dir / filename
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
    print(f"🎬 Phase A+ 추가 크롤 — {len(TARGETS)}개 (진짜 경쟁군만)")
    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        for tgt in TARGETS:
            r = crawl_one(tgt)
            marker = "✅" if r.status == 200 and r.content_length > 5000 else "⚠️"
            status = f"{r.content_length:,} bytes / HTTP {r.status}" if r.content_length else f"error: {r.error}"
            print(f"{marker} {r.brand}/{r.channel} sku={r.sku_id}: {status}")
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
