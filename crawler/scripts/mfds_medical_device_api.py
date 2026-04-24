"""
식약처 공공데이터 OpenAPI — 의료기기 품목허가 정보 조회

데이터셋: data.go.kr/data/15057456
Endpoint (확정):
  https://apis.data.go.kr/1471000/MdlpPrdlstPrmisnInfoService05/getMdlpPrdlstPrmisnList04

파라미터 (소문자):
  - serviceKey: API 키
  - pageNo, numOfRows, type=json
  - prduct: 품목명 (정확 일치, 공백 없음. 예: "비이식형요실금신경근전기자극장치")
  - entrps: 업체명 (정확 또는 부분 일치 불명확)

응답 필드:
  - ENTRPS: 업체명 (법인명)
  - PRDUCT: 품목명 (카테고리명)
  - PRMISN_STTEMNT: 허가 상태 코드 (1=유효, 2/3/4=다양)
  - PRDUCT_PRMISN_NO: 허가번호 (예: "제허 15-329 호")
  - PRMISN_DT: 허가일자 (YYYYMMDD)
  - MDEQ_PRDLST_SN: 의료기기 품목 일련번호
  - RTRCN_DSCTN_DIVS_CD / RTRCN_DSCTN_DT: 철회/취소 정보
  - MANUF_NM: 제조원명 (수입 제품의 경우)
  - CHG_DT: 마지막 변경일

사용법:
    python crawler/scripts/mfds_medical_device_api.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

API_KEY = os.environ.get("MFDS_OPENAPI_KEY", "").strip()
if not API_KEY:
    sys.exit("MFDS_OPENAPI_KEY 미설정")

ENDPOINT = "https://apis.data.go.kr/1471000/MdlpPrdlstPrmisnInfoService05/getMdlpPrdlstPrmisnList04"

OUT_DIR = REPO_ROOT / "data" / "external" / "mfds_medical_device"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 우리 관심 품목 (공백 제거 형태로 검색)
TARGET_CATEGORIES = [
    "비이식형요실금신경근전기자극장치",  # 주 카테고리 — EASY-K가 여기
    "개인용저주파자극기",               # 인접 — 알파메딕이 또 여기도 등록
    "저주파의료용조합자극기",           # 마스터 §2.2에 바디닥터 등록 카테고리로 언급
    "골반저근자극기",                    # 기타 관련
    "전기근육자극기",                    # 광범위 (주의: 너무 많을 수 있음)
]


def fetch_category(prduct: str, max_pages: int = 3, rows_per_page: int = 100) -> list[dict]:
    """특정 품목명의 모든 등록 제품 수집."""
    all_items = []
    for page in range(1, max_pages + 1):
        params = {
            "serviceKey": API_KEY,
            "pageNo": page,
            "numOfRows": rows_per_page,
            "type": "json",
            "prduct": prduct,
        }
        r = requests.get(ENDPOINT, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = [it.get("item", {}) for it in data.get("body", {}).get("items", [])]
        total = data.get("body", {}).get("totalCount", 0)
        all_items.extend(items)
        if page * rows_per_page >= total:
            break
    return all_items


def save_jsonl(items: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def main():
    summary = []
    for category in TARGET_CATEGORIES:
        print(f"=== {category} ===")
        items = fetch_category(category)
        print(f"  수집: {len(items)}건")
        # 유효 허가(상태=1)만 필터
        active = [it for it in items if it.get("PRMISN_STTEMNT") == "1"]
        print(f"  유효(상태=1): {len(active)}건")

        # 회사별 집계
        by_company: dict[str, list] = {}
        for it in active:
            company = it.get("ENTRPS", "(미상)")
            by_company.setdefault(company, []).append(it)
        for company, its in sorted(by_company.items(), key=lambda kv: -len(kv[1])):
            for it in its:
                print(
                    f"    {company:<25} | {it.get('PRDUCT_PRMISN_NO'):<15} | {it.get('PRMISN_DT')}"
                )

        # 저장
        slug = category.replace(" ", "_")
        save_jsonl(items, OUT_DIR / f"{slug}.jsonl")
        summary.append({"category": category, "total": len(items), "active": len(active), "companies": len(by_company)})
        print()

    # 요약 저장
    summary_path = OUT_DIR / "_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 요약 저장: {summary_path}")


if __name__ == "__main__":
    main()
