"""
H14 외부 증거 수집기 — NAVER 검색 API.

수집 항목 (브랜드당):
- 블로그 언급 수 (총 검색 결과)
- 카페 언급 수
- 뉴스 언급 수
- 쇼핑 상품 수 (= 한국 유통 채널 다양성 proxy)

환경변수:
- NAVER_CLIENT_ID, NAVER_CLIENT_SECRET (Wayne이 developers.naver.com에서 발급)

사용법:
    python crawler/scripts/collect_external_evidence.py

출력: data/processed/external_evidence.jsonl (브랜드당 1 row)

키 없으면: "NAVER API 키 없음" 안내 후 종료. 수동 대체 가능.
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "").strip()
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "").strip()

OUT_PATH = REPO_ROOT / "data" / "processed" / "external_evidence.jsonl"

# 경쟁군 의료기기 N=13 + 가글 N=12 (2026-04-24 v5 — 가글 풀 확장)
BRANDS = [
    # 의료기기 anchor + 경쟁 12 (elvie/stopyo 제외: elvie는 경쟁군에서 제외, stopyo는 쿠팡 Akamai 차단)
    {"id": "bodydoctor", "query": "바디닥터 요실금치료기", "vertical": "medical_device"},
    {"id": "easyk", "query": "이지케이 EASY-K", "vertical": "medical_device"},
    {"id": "coway_therasol", "query": "코웨이 테라솔", "vertical": "medical_device"},
    {"id": "ceragem", "query": "세라젬 요실금치료기", "vertical": "medical_device"},
    {"id": "furenhealth", "query": "퓨런헬스케어 요실금", "vertical": "medical_device"},
    {"id": "peronian", "query": "페로니언 케겔", "vertical": "medical_device"},
    {"id": "hools", "query": "훌스 음파방석", "vertical": "medical_device"},
    {"id": "wavecare", "query": "웨이브케어 V8", "vertical": "medical_device"},
    {"id": "stopyo", "query": "스탑요 자동 케겔", "vertical": "medical_device"},
    {"id": "ems_vital", "query": "EMS케겔휘트니스 비틀", "vertical": "medical_device"},
    {"id": "kegel_magic", "query": "케겔매직", "vertical": "medical_device"},
    {"id": "huonsen", "query": "휴온센 EMS 레깅스", "vertical": "medical_device"},
    {"id": "applehip", "query": "애플힙 케겔자동운동기구", "vertical": "medical_device"},
    # 가글 anchor + 경쟁 11 (풀 확장 2026-04-24)
    {"id": "propolinse", "query": "프로폴린스 가글", "vertical": "gargle"},
    {"id": "listerine", "query": "리스테린 가글", "vertical": "gargle"},
    {"id": "garglin", "query": "가그린", "vertical": "gargle"},
    {"id": "perio", "query": "페리오 가글", "vertical": "gargle"},
    {"id": "gargle_2080", "query": "2080 구강청결제", "vertical": "gargle"},
    {"id": "awesomecool", "query": "어썸쿨 프로폴리스 가글", "vertical": "gargle"},
    {"id": "therabreath", "query": "테라브레스 오랄린스", "vertical": "gargle"},
    {"id": "usimol", "query": "유시몰 가글", "vertical": "gargle"},
    {"id": "colgate", "query": "콜게이트 플락스 가글", "vertical": "gargle"},
    {"id": "oralb", "query": "오랄비 가글", "vertical": "gargle"},
    {"id": "sensodyne", "query": "센소다인 가글", "vertical": "gargle"},
    {"id": "kwangdong", "query": "광동 인후엔 가글", "vertical": "gargle"},
]

ENDPOINTS = {
    "blog": "https://openapi.naver.com/v1/search/blog.json",
    "cafearticle": "https://openapi.naver.com/v1/search/cafearticle.json",
    "news": "https://openapi.naver.com/v1/search/news.json",
    "shop": "https://openapi.naver.com/v1/search/shop.json",
}


@dataclass
class EvidenceRow:
    brand_id: str
    query: str
    vertical: str
    blog_total: int
    cafe_total: int
    news_total: int
    shop_total: int
    fetched_at: str

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def fetch_total(endpoint: str, query: str) -> int:
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 1}
    r = requests.get(endpoint, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return int(r.json().get("total", 0))


def main():
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("⚠️  NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정.")
        print("   Wayne이 https://developers.naver.com 에서 앱 등록 후 .env에 키 추가 필요.")
        print("   키 이름: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET")
        print("   (블로그/카페/뉴스/쇼핑 검색 API 권한 선택)")
        sys.exit(1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"🎬 외부 증거 수집 — {len(BRANDS)} 브랜드 × 4 endpoint = {len(BRANDS) * 4} 호출")
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for b in BRANDS:
            totals = {}
            try:
                for kind, url in ENDPOINTS.items():
                    totals[kind] = fetch_total(url, b["query"])
                    time.sleep(0.3)  # NAVER rate limit 여유
            except Exception as e:
                print(f"  ⚠️  {b['id']}: {e}")
                totals = {k: 0 for k in ENDPOINTS}
            row = EvidenceRow(
                brand_id=b["id"],
                query=b["query"],
                vertical=b["vertical"],
                blog_total=totals.get("blog", 0),
                cafe_total=totals.get("cafearticle", 0),
                news_total=totals.get("news", 0),
                shop_total=totals.get("shop", 0),
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )
            f.write(row.to_jsonl() + "\n")
            f.flush()
            print(f"  ✅ {b['id']:16} blog={row.blog_total:>6} cafe={row.cafe_total:>6} news={row.news_total:>6} shop={row.shop_total:>6}")

    print(f"\n✅ 저장: {OUT_PATH}")


if __name__ == "__main__":
    main()
