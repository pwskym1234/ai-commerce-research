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
SERVICE = "MdlpPrdlstPrmisnInfoService05"  # Wayne 제공: 의료기기 품목허가 정보

# 일반 식약처 패턴: getXxxInfo / getXxxInfoInq05 등
OPERATION_CANDIDATES = [
    "getMdlpPrdlstPrmisnDtlInq05",   # Dtl (Detail) 패턴
    "getMdlpPrdlstPrmisnDtlInq",
    "getMdlpPrdlstPrmisnInq",
    "getMdlpPrdlstPrmisnDtl",
    "getMdlpPrdlstInq05",
    "getMdlpPrdlstInq",
    "getMdlpPrdlst05",
    "getMdlp05",
    "list",
    "search",
    "",  # operation 없이 service URL만 (메뉴 출력 가능성)
]

QUERY_KEYWORDS = [
    "비이식형 요실금 신경근 전기자극장치",
    "저주파 의료용 조합 자극기",
    "골반저근",
]


def try_operation(operation: str, **params) -> dict:
    """operation 1개 시도. 응답 미리보기 반환."""
    url = f"{HOST}/{SERVICE}/{operation}"
    base_params = {
        "serviceKey": API_KEY,
        "type": "json",
        "pageNo": 1,
        "numOfRows": 3,
    }
    base_params.update(params)
    try:
        r = requests.get(url, params=base_params, timeout=30)
        return {
            "operation": operation,
            "status": r.status_code,
            "url": r.url[:250],
            "preview": r.text[:1000],
        }
    except Exception as e:
        return {"operation": operation, "status": "error", "error": str(e)}


def main():
    print(f"API 키 끝 4자리: ...{API_KEY[-4:]}")
    print(f"Service: {SERVICE}\n")
    print("=" * 80)
    print("Step 1: operation 이름 탐색")
    print("=" * 80)
    working_op = None
    for op in OPERATION_CANDIDATES:
        result = try_operation(op)
        status = result.get("status")
        marker = "✅" if status == 200 else "❌"
        print(f"\n{marker} [{status}] {op}")
        preview = result.get("preview", "")
        if preview:
            print(f"   응답: {preview[:400]}")
        # 성공 또는 작동하는 응답 패턴 발견 시 저장
        if status == 200 and preview and "INFO-" not in preview[:200]:
            working_op = op
            break
        if status == 200 and "INFO-" in preview[:200]:
            # INFO-200 = success but no data, INFO-NO-DATA 등도 성공
            working_op = op


if __name__ == "__main__":
    main()
