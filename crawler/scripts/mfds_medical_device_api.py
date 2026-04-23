"""
식약처 공공데이터 OpenAPI — 의료기기 품목허가 정보 조회

데이터셋: data.go.kr/data/15057456
목적: "비이식형 요실금 신경근 전기자극장치" 등 우리 카테고리에 등록된 의료기기 OEM 풀 추출

명세서가 공공데이터포털에 직접 노출되지 않으므로, 식약처 OpenAPI의 표준 패턴으로 endpoint를 시도하고
응답 구조를 보면서 작동하는 endpoint를 찾는다.
"""
import os
import sys
import json
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.environ.get("MFDS_OPENAPI_KEY", "").strip()
if not API_KEY:
    sys.exit("환경변수 MFDS_OPENAPI_KEY가 비어 있습니다. .env 확인.")

# 식약처 OpenAPI 표준 호스트
HOST = "https://apis.data.go.kr/1471000"

# 시도할 endpoint 후보 (15057456 = 의료기기 품목허가 정보)
# 식약처 OpenAPI는 보통 {Service}/{operation} 구조
ENDPOINT_CANDIDATES = [
    "MdcInQrySrvc/getItem",
    "MedDevPrmsnInfoService/getMedDevPrmsnInfo",
    "MdeqPrmsnInfoService01/getMdeqPrmsnInfoInq01",
    "MdeqInfoService01/getMdeqInfoInq01",
    "MdeqMnftPrmsnDtlInfoService02/getMdeqMnftPrmsnDtlInfoInq02",
    "MdeqStdCdPrdtInfoService03/getMdeqStdCdPrdtInfoInq03",  # 표준코드별 — 다른 데이터셋이지만 작동 확인용
]

QUERY_KEYWORDS = [
    "비이식형 요실금 신경근 전기자극장치",
    "저주파 의료용 조합 자극기",
    "골반저근",
]


def try_endpoint(endpoint: str, **params) -> dict:
    """endpoint 1개 시도. 응답 미리보기 반환."""
    url = f"{HOST}/{endpoint}"
    base_params = {
        "serviceKey": API_KEY,
        "type": "json",
        "pageNo": 1,
        "numOfRows": 5,
    }
    base_params.update(params)
    try:
        r = requests.get(url, params=base_params, timeout=30)
        return {
            "endpoint": endpoint,
            "status": r.status_code,
            "url": r.url[:200],
            "preview": r.text[:600],
        }
    except Exception as e:
        return {"endpoint": endpoint, "status": "error", "error": str(e)}


def main():
    print(f"API 키 끝 4자리: ...{API_KEY[-4:]}\n")
    print("=" * 80)
    print("Step 1: endpoint 후보 탐색")
    print("=" * 80)
    for ep in ENDPOINT_CANDIDATES:
        result = try_endpoint(ep)
        status = result.get("status")
        marker = "✅" if status == 200 else "❌"
        print(f"\n{marker} [{status}] {ep}")
        print(f"   URL: {result.get('url')}")
        preview = result.get("preview", "")
        if preview:
            print(f"   응답: {preview[:300]}")


if __name__ == "__main__":
    main()
