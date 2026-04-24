"""퓨런헬스케어 제품 상세 페이지 크롤링."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = REPO_ROOT / "data" / "raw"

TARGETS = [
    ("http://furun.kr/about-us/company/", "about_company"),
    ("http://furun.kr/about-us/certificates/", "about_certificates"),
    ("http://furun.kr/products/", "products_index"),
    ("http://furun.kr/products/pelvic-floor-muscle-training-device/hnj-350/", "hnj-350"),
    ("http://furun.kr/products/pelvic-floor-muscle-training-device/hnj-1000/", "hnj-1000"),
    ("http://furun.kr/products/medical-device/hnj-7000/", "hnj-7000"),
    ("http://furun.kr/cs/purchase-inquiry/", "cs_purchase"),
]


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir = DATA_RAW / "medical_device" / "furun" / "self_mall" / today
    raw_dir.mkdir(parents=True, exist_ok=True)

    for url, sku_id in TARGETS:
        time.sleep(2.5)
        print(f"→ {url}")
        try:
            r = cffi_requests.get(url, impersonate="chrome", timeout=20, allow_redirects=True)
            body = r.text
            sha = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
            filename = f"{sku_id}_cffi_{sha}_cffi.html"
            (raw_dir / filename).write_text(body, encoding="utf-8")
            marker = "✅" if len(body) > 5000 else "⚠️"
            print(f"  {marker} {r.status_code} | {len(body):,} bytes")
        except Exception as e:
            print(f"  ❌ {e}")


if __name__ == "__main__":
    main()
