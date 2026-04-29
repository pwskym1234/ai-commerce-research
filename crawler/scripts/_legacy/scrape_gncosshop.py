"""
GN코스몰(gncosshop.com) 크롤러.

대상:
- 바디닥터 카테고리 (cate_no=26): 12개 제품
- 프로폴린스 단독 페이지 (해당 카테고리 검색 필요)
- 굿닥터/메르셀 등 부가 라인 (선택)

사용법:
    python crawler/scripts/scrape_gncosshop.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import fetch, append_jsonl, REPO_ROOT  # noqa: E402

JSONL_PATH = REPO_ROOT / "data" / "raw" / "_index" / "gncosshop.jsonl"

# 1차 진단에서 추출한 product_no 매핑 (gncosshop cate_no=26)
BODYDOCTOR_PRODUCTS = {
    187: "바디닥터 요실금 치료기 의료기 자동 케겔운동기",
    210: "바디닥터 3종 세트 요실금치료기 좌훈기 허리벨트",
    190: "바디닥터 EMS 트레이닝 무선 허리벨트",
    204: "바디닥터 고주파 리페어",
    207: "바디닥터 고주파 리페어 전용 캐리어 가방",
    200: "바디닥터 3종 전용 캐링백 백팩",
    172: "바디닥터 기능성 내의 2벌 세트",
    203: "바디닥터 고주파 리페어 컨덕티브 바디크림 500ml",
    202: "바디닥터 고주파 리페어 더블케어 크림 8ml*20ea",
    212: "바디닥터 더블케어크림 150ml 페이스용",
    211: "바디닥터 컨덕티브 크림 150ml 바디용",
    196: "바디닥터 요실금치료기 전용 프리미엄 물티슈",
}

CATE_NO = 26

# 핵심 SKU만 우선 수집 (의료기기 본실험에 직결)
CORE_PRODUCT_NOS = [187, 210, 190, 204]


def main(only_core: bool = True):
    targets = CORE_PRODUCT_NOS if only_core else list(BODYDOCTOR_PRODUCTS.keys())
    for pn in targets:
        url = f"https://gncosshop.com/product/detail.html?product_no={pn}&cate_no={CATE_NO}"
        result = fetch(
            url=url,
            vertical="medical_device",
            brand="bodydoctor",
            channel="gncosshop",
            sku_id=str(pn),
        )
        marker = "✅" if result.status == 200 else "❌"
        print(f"{marker} [{result.status}] product_no={pn}: {BODYDOCTOR_PRODUCTS[pn][:30]}")
        append_jsonl(JSONL_PATH, result)


if __name__ == "__main__":
    main(only_core=True)
