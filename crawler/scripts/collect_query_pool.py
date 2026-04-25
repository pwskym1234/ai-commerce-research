"""
쿼리 풀 수집 — 네이버 지식iN + 카페 + 쇼핑 + 뉴스 검색.

목표: 실제 사용자 어투의 질문 풀(~1,000개) 확보 → 8유형 자동 분류 →
     Phase B1 / 산공통 본실험에서 사용할 24개 쿼리 후보 선별 풀.

방식:
- NAVER 검색 API (Wayne 발급 키 사용)
- 의료기기 키워드 + 가글 키워드 별로 수집
- 결과를 query_pool_raw.jsonl 에 저장 (브랜드명/PII 마스킹)

산출물:
- data/processed/query_pool_raw.jsonl  — 원본 풀
- data/processed/query_pool_classified.jsonl — 8유형 자동 분류 후
- 통계 요약 stdout
"""
from __future__ import annotations

import json
import os
import re
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

OUT_RAW = REPO_ROOT / "data" / "processed" / "query_pool_raw.jsonl"
OUT_CLASSIFIED = REPO_ROOT / "data" / "processed" / "query_pool_classified.jsonl"

# 검색 키워드 — vertical 별 적정 키워드 (덜 일반적·덜 특수한 중간)
KEYWORDS = {
    "medical_device": [
        "요실금치료기", "케겔운동기", "골반저근 운동",
        "요실금 증상", "산후 회복 케겔", "전립선 운동기",
        "EMS 케겔", "요실금 가정용",
    ],
    "gargle": [
        "가글 추천", "구취 가글", "잇몸 가글",
        "구강청결제", "입냄새 가글", "산후 가글",
        "프로폴리스 가글", "어린이 가글",
    ],
}

# 검색 endpoint (지식iN + 카페 + 블로그 — 사용자 어투 풍부)
ENDPOINTS = {
    "kin": "https://openapi.naver.com/v1/search/kin.json",
    "cafe": "https://openapi.naver.com/v1/search/cafearticle.json",
    "blog": "https://openapi.naver.com/v1/search/blog.json",
}

# 필터 기준
MIN_LEN = 8
MAX_LEN = 100
SPAM_PATTERNS = ["무료증정", "공구", "공동구매", "이벤트 참여", "쿠폰 받기", "당첨"]

# 8유형 자동 분류 (간단 룰)
OUR_BRANDS_MED = ["바디닥터"]
OUR_BRANDS_GARGLE = ["프로폴린스"]
COMP_BRANDS_MED = ["이지케이", "EASY-K", "코웨이 테라솔", "테라솔", "세라젬",
                   "퓨런", "페로니언", "훌스", "웨이브케어", "스탑요",
                   "케겔매직", "휴온센", "애플힙", "비틀"]
COMP_BRANDS_GARGLE = ["리스테린", "가그린", "페리오", "2080", "어썸쿨",
                      "테라브레스", "유시몰", "콜게이트", "오랄비", "센소다인",
                      "광동"]

SYMPTOMS = ["요실금", "소변", "재채기", "출산 후", "산후", "갱년기",
            "전립선", "방광", "구취", "입냄새", "잇몸", "충치", "치주"]
USE_PATTERNS = ["산후", "갱년기", "출산", "TV", "앉아서", "매일", "식후", "취침 전",
                "회복용", "관리"]
DECISION_PATTERNS = ["하나만", "딱 하나", "1개만", "한 개만", "하나 골라",
                     "추천 1개", "딱 골라"]


@dataclass
class QueryRow:
    text: str                 # 정제 후 본문 (질문 제목)
    source: str               # kin / cafe / blog
    keyword: str              # 검색 키워드
    vertical: str             # medical_device / gargle
    raw_link: str             # 원본 URL
    fetched_at: str

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def clean_html(s: str) -> str:
    """NAVER 결과의 <b>...</b> 강조 태그 등 HTML 엔티티 제거."""
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return s.strip()


def is_realistic(text: str, vertical: str) -> bool:
    if len(text) < MIN_LEN or len(text) > MAX_LEN:
        return False
    if any(s in text for s in SPAM_PATTERNS):
        return False
    if text.count("?") > 2:
        return False
    # 도메인 키워드 — vertical별
    if vertical == "medical_device":
        domain_kw = ["요실금", "케겔", "골반", "전립선", "방광", "소변", "EMS"]
    else:
        domain_kw = ["가글", "구취", "입냄새", "구강", "잇몸", "구강청결"]
    if not any(kw in text for kw in domain_kw):
        return False
    return True


def classify(text: str, vertical: str) -> str:
    our = OUR_BRANDS_MED if vertical == "medical_device" else OUR_BRANDS_GARGLE
    comp = COMP_BRANDS_MED if vertical == "medical_device" else COMP_BRANDS_GARGLE

    if any(b in text for b in our):
        return "BRD"
    if any(c in text for c in comp) and ("말고" in text or "외에" in text or "대신" in text or "보다" in text):
        return "COM"
    if any(c in text for c in comp):
        return "CMP"
    if re.search(r"\d+\s*만\s*원", text) or "예산" in text or "가격" in text or "렌탈" in text:
        return "PRC"
    if any(s in text for s in SYMPTOMS):
        return "SYM"
    if any(u in text for u in USE_PATTERNS):
        return "USE"
    if any(d in text for d in DECISION_PATTERNS):
        return "DEC"
    return "CAT"


def fetch_naver(endpoint_url: str, query: str, display: int = 100, start: int = 1) -> list[dict]:
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "start": start, "sort": "sim"}
    r = requests.get(endpoint_url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("items", [])


def main():
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("⚠️  NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정.")
        print("   .env 의 NAVER_CLIENT_ID=, NAVER_CLIENT_SECRET= 뒤에 키 값을 붙여주세요.")
        sys.exit(1)

    OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
    rows: list[QueryRow] = []

    print(f"🎬 쿼리 풀 수집 — vertical 2 × keyword × endpoint 3")
    for vertical, keywords in KEYWORDS.items():
        for keyword in keywords:
            for src, url in ENDPOINTS.items():
                try:
                    items = fetch_naver(url, keyword, display=100)
                    time.sleep(0.3)
                except Exception as e:
                    print(f"  ⚠️  {vertical}/{keyword}/{src}: {e}")
                    continue
                kept = 0
                for it in items:
                    title = clean_html(it.get("title", ""))
                    desc = clean_html(it.get("description", ""))
                    text = title  # 질문 텍스트는 title 위주 (description은 답변 일부)
                    if not is_realistic(text, vertical):
                        continue
                    rows.append(QueryRow(
                        text=text,
                        source=src,
                        keyword=keyword,
                        vertical=vertical,
                        raw_link=it.get("link", ""),
                        fetched_at=datetime.now(timezone.utc).isoformat(),
                    ))
                    kept += 1
                print(f"  ✅ {vertical:14} {keyword:14} {src:5} {kept:>3}/{len(items)} kept")

    # 중복 제거
    seen = set()
    uniq: list[QueryRow] = []
    for r in rows:
        if r.text in seen:
            continue
        seen.add(r.text)
        uniq.append(r)
    print(f"\n수집 합계: {len(rows)} → 중복 제거: {len(uniq)}")

    with OUT_RAW.open("w", encoding="utf-8") as f:
        for r in uniq:
            f.write(r.to_jsonl() + "\n")

    # 자동 분류
    classified = []
    type_counts: dict[str, int] = {}
    for r in uniq:
        qtype = classify(r.text, r.vertical)
        d = asdict(r)
        d["query_type"] = qtype
        classified.append(d)
        key = f"{r.vertical}:{qtype}"
        type_counts[key] = type_counts.get(key, 0) + 1

    with OUT_CLASSIFIED.open("w", encoding="utf-8") as f:
        for d in classified:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"\n✅ 저장:")
    print(f"  raw:        {OUT_RAW}  ({len(uniq)} rows)")
    print(f"  classified: {OUT_CLASSIFIED}")
    print(f"\n8유형 분포:")
    for key in sorted(type_counts):
        print(f"  {key:30} {type_counts[key]:>4}")


if __name__ == "__main__":
    main()
