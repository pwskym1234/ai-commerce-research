#!/usr/bin/env python3
"""NAVER 검색 API + DataLab Trends로 한국 의료기기/가글 키워드 빈도 매핑.

목표:
- 산공통 쿼리셋 (Q1×Q2) 외부 타당성 보강 (action_roadmap.md §1.6)
- Ahrefs Brand Radar의 "real search behavior 기반 prompt" 메서드 부분 차용

산출:
- data/processed/naver_search_volume.json — 키워드별 4 엔드포인트 카운트 + DataLab 트렌드
- data/processed/naver_search_volume.md — 사람용 요약 표

메서드:
1. 검색 API → 키워드별 blog/cafearticle/news/shop의 'total' 문서 카운트 (절대 mention proxy)
2. DataLab Trends → 키워드 그룹 12개월 상대 트렌드 (가중치)

한계:
- NaverSearchAd (절대 검색량) API는 별도 광고주 자격 필요 — 우리 키로는 불가
- 검색 API total은 "문서 수"이지 "검색량"이 아님. 인기도 proxy로 사용.
- DataLab은 그룹 내 *상대* 비율만 (1.0 정규화)
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]

# .env 로드
for line in (ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

CID = os.environ["NAVER_CLIENT_ID"]
CSEC = os.environ["NAVER_CLIENT_SECRET"]
HEADERS = {"X-Naver-Client-Id": CID, "X-Naver-Client-Secret": CSEC}
DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"

# ========== 키워드 셋 ==========

MEDICAL_KEYWORDS: dict[str, list[str]] = {
    "category_general": ["요실금", "케겔", "골반저근", "케겔운동", "산후 회복", "출산 후 회복"],
    "category_specific": ["요실금치료기", "케겔운동기구", "EMS 골반", "골반저근 강화"],
    "symptom": ["산후 요실금", "갱년기 요실금", "복압성 요실금", "긴장성 요실금"],
    "brand_kr": ["바디닥터 요실금치료기", "바디닥터 케겔", "이지케이", "EASY-K", "코웨이 테라솔", "세라젬"],
    "brand_global": ["Elvie Trainer", "Perifit", "Kegel8", "kGoal"],
    "comparison": ["요실금 추천", "케겔 추천", "산후 회복기 추천", "골반저근 운동기구 비교"],
}

GARGLE_KEYWORDS: dict[str, list[str]] = {
    "category": ["가글", "구강청결제", "마우스워시", "입냄새 제거"],
    "ingredient": ["프로폴리스 가글", "치주염 가글", "잇몸 가글", "충치예방 가글"],
    "brand": ["프로폴린스", "리스테린", "가그린", "2080", "페리오"],
    "comparison": ["가글 추천", "프로폴리스 가글 추천", "구강청결제 비교"],
}

# ========== 검색 API ==========

def search_total(query: str, endpoint: str) -> int:
    url = f"https://openapi.naver.com/v1/search/{endpoint}.json"
    try:
        r = requests.get(
            url, headers=HEADERS, params={"query": query, "display": 1}, timeout=15
        )
    except requests.RequestException:
        return -1
    if r.status_code != 200:
        return -1
    return r.json().get("total", 0)


def get_endpoint_counts(query: str) -> dict:
    counts: dict = {}
    for ep in ["blog", "cafearticle", "news", "shop"]:
        counts[ep] = search_total(query, ep)
        time.sleep(0.1)  # rate limit 보호
    counts["total"] = sum(c for c in counts.values() if c >= 0)
    return counts


# ========== DataLab Trends ==========

def datalab_trends(group_name: str, keywords: list[str]) -> dict:
    today = date.today()
    start = today - timedelta(days=365)
    body = {
        "startDate": start.isoformat(),
        "endDate": today.isoformat(),
        "timeUnit": "month",
        "keywordGroups": [{"groupName": group_name, "keywords": keywords[:5]}],
    }
    try:
        r = requests.post(
            DATALAB_URL,
            headers={**HEADERS, "Content-Type": "application/json"},
            json=body,
            timeout=15,
        )
    except requests.RequestException as e:
        return {"error": str(e)}
    if r.status_code != 200:
        return {"error": r.status_code, "msg": r.text[:300]}
    return r.json()


# ========== Main ==========

def main() -> int:
    print("=== NAVER 검색량 매핑 (의료기기 + 가글) ===\n")

    out: dict = {
        "collected_at": date.today().isoformat(),
        "method": "naver-search-api-4-endpoints + datalab-trends",
        "limitations": "절대 검색량 아님 — 문서 수 proxy. NaverSearchAd 별도 자격 필요.",
        "medical_device": {},
        "gargle": {},
        "datalab_trends": {},
    }

    for vert_name, vert_dict, target in [
        ("medical_device", MEDICAL_KEYWORDS, out["medical_device"]),
        ("gargle", GARGLE_KEYWORDS, out["gargle"]),
    ]:
        print(f"\n[{vert_name}]")
        for cat, keywords in vert_dict.items():
            target[cat] = {}
            for kw in keywords:
                c = get_endpoint_counts(kw)
                target[cat][kw] = c
                tot = c.get("total", "?")
                print(f"  [{cat}] {kw:<30} → total {tot:>11,}")

    print("\n[DataLab Trends — 12개월 월별 상대 비율]")
    out["datalab_trends"]["medical_brand"] = datalab_trends(
        "의료기기 브랜드",
        ["바디닥터 요실금치료기", "이지케이", "코웨이 테라솔", "세라젬"],
    )
    out["datalab_trends"]["medical_category"] = datalab_trends(
        "요실금 카테고리",
        ["요실금치료기", "케겔운동기구", "골반저근 강화", "EMS 골반"],
    )
    out["datalab_trends"]["gargle_brand"] = datalab_trends(
        "가글 브랜드",
        ["프로폴린스", "리스테린", "가그린", "2080", "페리오"],
    )
    print("  trends 저장됨 (json 안에)")

    out_dir = ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "naver_search_volume.json"
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ JSON: {json_path}")

    # Markdown 요약
    md = [
        "# NAVER 검색량 매핑 — 의료기기 + 가글",
        "",
        f"**수집일**: {out['collected_at']}",
        "",
        "**메서드**: 검색 API 4개 엔드포인트(blog/cafearticle/news/shop) total document count + DataLab Trends 12개월 상대 비율",
        "",
        "**한계**: 절대 검색량이 아닌 문서 수 proxy. NaverSearchAd API(절대 검색량)는 별도 광고주 자격 필요.",
        "",
    ]

    for label, vert_dict in [("의료기기", out["medical_device"]), ("가글", out["gargle"])]:
        md += ["", f"## {label}", ""]
        md += ["| 카테고리 | 키워드 | blog | cafe | news | shop | **total** |"]
        md += ["|---|---|---:|---:|---:|---:|---:|"]
        for cat, items in vert_dict.items():
            for kw, c in items.items():
                fmt = lambda x: f"{x:,}" if isinstance(x, int) and x >= 0 else "-"
                md.append(
                    f"| {cat} | {kw} | {fmt(c.get('blog'))} | {fmt(c.get('cafearticle'))} "
                    f"| {fmt(c.get('news'))} | {fmt(c.get('shop'))} | **{fmt(c.get('total'))}** |"
                )

    md += [
        "",
        "## DataLab Trends",
        "",
        "각 그룹 내 *상대* 검색 비율 (1.0 정규화). 절대값 아님. 자세한 12개월 시계열은 JSON 파일 참조.",
    ]

    md_path = out_dir / "naver_search_volume.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ MD : {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
