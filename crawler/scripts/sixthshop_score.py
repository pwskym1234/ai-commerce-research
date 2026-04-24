"""
Sixthshop-style AI Shopping Visibility Score 자체 산출.

출처: https://sixthshop.com 공개 배점 체계
  - Schema & Data Trust: 35점
  - Content & Intent Match: 25점
  - Media & Visual Signals: 20점
  - Commerce & Eligibility: 20점
  - 합계: 100점

우리가 이걸 직접 구현하는 이유:
1. Sixthshop은 해외 유료 SaaS — 한국어/한국 이커머스 특수성(가격 표기 "원", 의료기기 인증) 반영 약함
2. 경쟁사 전체에 동일 기준 적용한 비교 가능 (가글 5종 + 의료기기 6종)
3. 데마 본실험에 **관찰 변수** 로 투입 (H14 external evidence 가설 검정)
4. 본실험 분석에서 "Sixthshop 점수가 AI 추천 확률과 양의 상관" 관찰 가능

용도 구분:
- 프로젝트 데마: 관찰 변수 (독립변수 중 하나)
- 컨설팅 action_roadmap: Stage 2 "Evaluate" 단계의 baseline 지표 + Before/After 측정
- 둘 다에 쓰임.

사용법:
    python crawler/scripts/sixthshop_score.py
    → data/processed/sixthshop_scores.jsonl 생성
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import REPO_ROOT  # noqa: E402

DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"


# ========== 배점 체계 상세 ==========
#
# A. Schema & Data Trust — 35점
#    A1. JSON-LD 존재: 8점
#    A2. JSON-LD @type이 Product 또는 MedicalDevice: 7점
#    A3. aggregateRating 필드 포함: 5점
#    A4. offers/price/availability 필드 포함: 5점
#    A5. brand/manufacturer 필드 포함: 5점
#    A6. identifier (KFDA/FDA/GTIN) 필드 포함: 5점
#
# B. Content & Intent Match — 25점
#    B1. 스펙 표기 (TABLE 또는 BULLET): 6점
#    B2. Rufus SPN facet 언급 (use case / target audience / activity): 5점
#    B3. 비교/차별점 서술 명시: 4점
#    B4. FAQ 섹션: 4점
#    B5. 임상/근거 인용: 6점
#
# C. Media & Visual Signals — 20점
#    C1. 제품 이미지 5장 이상: 6점
#    C2. alt 텍스트 있는 이미지 비율 ≥ 50%: 4점
#    C3. 비디오 또는 3D 모델: 5점
#    C4. 인포그래픽 (치수/사용법): 5점
#
# D. Commerce & Eligibility — 20점
#    D1. 가격 명시: 5점
#    D2. 재고/배송 정보: 5점
#    D3. 리뷰 수 표시: 5점
#    D4. 구매 버튼/바로구매: 3점
#    D5. 환불/교환 정책: 2점
#


@dataclass
class SixthshopScore:
    brand: str
    channel: str
    sku_id: str
    raw_path: str

    # 세부 점수
    A_total: int
    A_details: dict
    B_total: int
    B_details: dict
    C_total: int
    C_details: dict
    D_total: int
    D_details: dict

    total: int

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def score_schema_data_trust(soup: BeautifulSoup, raw_html: str) -> tuple[int, dict]:
    """A. Schema & Data Trust (35점)"""
    details = {}
    score = 0

    # A1. JSON-LD 존재
    jsonld_tags = soup.find_all("script", type="application/ld+json")
    details["A1_jsonld_present"] = len(jsonld_tags) > 0
    if details["A1_jsonld_present"]:
        score += 8

    # JSON-LD 파싱
    jsonld_objs = []
    for tag in jsonld_tags:
        try:
            data = json.loads(tag.string or "{}")
            items = data if isinstance(data, list) else [data]
            jsonld_objs.extend(items)
        except Exception:
            pass

    # A2. @type이 Product/MedicalDevice
    types = [obj.get("@type") for obj in jsonld_objs if isinstance(obj, dict)]
    types_flat = [t if isinstance(t, str) else ",".join(t) if isinstance(t, list) else "" for t in types]
    has_product = any(t in ["Product", "MedicalDevice"] or (isinstance(t, str) and ("Product" in t or "MedicalDevice" in t)) for t in types_flat)
    details["A2_product_type"] = has_product
    if has_product:
        score += 7

    # A3. aggregateRating
    has_rating = any(isinstance(obj, dict) and "aggregateRating" in obj for obj in jsonld_objs)
    details["A3_aggregate_rating"] = has_rating
    if has_rating:
        score += 5

    # A4. offers + price
    has_offer = any(
        isinstance(obj, dict) and "offers" in obj and
        (isinstance(obj.get("offers"), dict) and obj["offers"].get("price"))
        for obj in jsonld_objs
    )
    details["A4_offers_price"] = has_offer
    if has_offer:
        score += 5

    # A5. brand/manufacturer
    has_brand = any(isinstance(obj, dict) and ("brand" in obj or "manufacturer" in obj) for obj in jsonld_objs)
    details["A5_brand"] = has_brand
    if has_brand:
        score += 5

    # A6. identifier (KFDA/FDA 같은 인증 번호, GTIN 등)
    has_id = any(
        isinstance(obj, dict) and ("identifier" in obj or "gtin" in obj or "gtin13" in obj or "sku" in obj)
        for obj in jsonld_objs
    )
    # 또는 텍스트에 "제허 XX-XXX 호" 패턴
    has_mfds_num = bool(re.search(r"제허\s*\d+-\d+\s*호|수허\s*\d+-\d+\s*호", raw_html))
    details["A6_identifier"] = has_id or has_mfds_num
    if has_id or has_mfds_num:
        score += 5

    return score, details


SPN_KEYWORDS = {
    "target_audience": ["출산 후", "산후", "임신", "40대", "50대", "60대", "여성", "남성", "노인"],
    "activity": ["앉아", "TV 보면서", "사무실", "운동 중", "수면", "자는 동안"],
    "use_case": ["요실금", "골반저근", "케겔", "회복", "예방", "강화", "재활"],
    "subjective": ["간편한", "무소음", "자동", "편안한", "안정적", "부드러운"],
    "event": ["출산 후 회복기", "갱년기", "산후조리"],
}


def score_content_intent(soup: BeautifulSoup, text: str) -> tuple[int, dict]:
    """B. Content & Intent Match (25점)"""
    details = {}
    score = 0

    # B1. 스펙 표기 (table 또는 ul/ol with >= 4 items)
    tables = soup.find_all("table")
    lists = [ul for ul in soup.find_all(["ul", "ol"]) if len(ul.find_all("li")) >= 4]
    has_structured_spec = len(tables) >= 1 or len(lists) >= 2
    details["B1_structured_spec"] = has_structured_spec
    if has_structured_spec:
        score += 6

    # B2. Rufus SPN facet — 5 카테고리 중 3개 이상 언급
    spn_hits = sum(1 for kws in SPN_KEYWORDS.values() if any(kw in text for kw in kws))
    details["B2_spn_facets"] = spn_hits
    if spn_hits >= 3:
        score += 5
    elif spn_hits >= 2:
        score += 3

    # B3. 비교/차별점
    compare_kws = ["vs", "차이", "비교", "차별", "경쟁사", "대비"]
    has_compare = any(kw in text for kw in compare_kws)
    details["B3_comparison"] = has_compare
    if has_compare:
        score += 4

    # B4. FAQ
    faq_kws = ["자주 묻는", "FAQ", "Q&A", "Q1", "Q2", "질문", "문의"]
    has_faq = sum(1 for kw in faq_kws if kw in text) >= 2
    details["B4_faq"] = has_faq
    if has_faq:
        score += 4

    # B5. 임상/근거 인용
    clinical_kws = ["임상", "RCT", "연구 결과", "p<0.", "논문", "유의", "n=", "대학병원", "검증"]
    clinical_hits = sum(1 for kw in clinical_kws if kw in text)
    details["B5_clinical"] = clinical_hits
    if clinical_hits >= 3:
        score += 6
    elif clinical_hits >= 1:
        score += 3

    return score, details


def score_media_visual(soup: BeautifulSoup) -> tuple[int, dict]:
    """C. Media & Visual Signals (20점)"""
    details = {}
    score = 0

    # C1. 제품 이미지 5장 이상 (본문 영역 추정)
    imgs = soup.find_all("img")
    product_imgs = [img for img in imgs if img.get("src") and not any(
        skip in (img.get("src") or "") for skip in ["icon", "logo", "banner"]
    )]
    details["C1_image_count"] = len(product_imgs)
    if len(product_imgs) >= 5:
        score += 6

    # C2. alt 텍스트 비율
    imgs_with_alt = sum(1 for img in imgs if img.get("alt", "").strip())
    alt_ratio = imgs_with_alt / max(len(imgs), 1)
    details["C2_alt_ratio"] = round(alt_ratio, 2)
    if alt_ratio >= 0.5:
        score += 4

    # C3. 비디오 (iframe youtube / video tag)
    has_video = bool(soup.find("iframe", src=re.compile(r"youtube|vimeo"))) or bool(soup.find("video"))
    details["C3_video"] = has_video
    if has_video:
        score += 5

    # C4. 인포그래픽 추정 — alt/filename에 "infographic"/"다이어그램"/"사용법" 등
    info_keywords = ["사용법", "가이드", "다이어그램", "인포", "infographic", "how-to", "step"]
    has_infographic = any(
        any(kw in (img.get("alt", "") + img.get("src", "")).lower() for kw in info_keywords)
        for img in imgs
    )
    details["C4_infographic"] = has_infographic
    if has_infographic:
        score += 5

    return score, details


def score_commerce_eligibility(soup: BeautifulSoup, text: str) -> tuple[int, dict]:
    """D. Commerce & Eligibility (20점)"""
    details = {}
    score = 0

    # D1. 가격 (원 또는 KRW)
    has_price = bool(re.search(r"\d[\d,]*\s*원|KRW", text))
    details["D1_price"] = has_price
    if has_price:
        score += 5

    # D2. 재고/배송 정보
    stock_kws = ["재고", "품절", "입고", "배송비", "배송 기간", "택배", "무료배송"]
    stock_hits = sum(1 for kw in stock_kws if kw in text)
    details["D2_stock_shipping"] = stock_hits
    if stock_hits >= 3:
        score += 5
    elif stock_hits >= 1:
        score += 3

    # D3. 리뷰 수 표시
    has_review_count = bool(re.search(r"리뷰\s*\(?\s*\d+|후기\s*\(?\s*\d+|\d+\s*개\s*리뷰", text))
    details["D3_review_count"] = has_review_count
    if has_review_count:
        score += 5

    # D4. 구매 버튼
    buy_kws = ["바로구매", "장바구니", "구매하기", "주문", "CART", "BUY"]
    has_buy_btn = any(kw in text for kw in buy_kws)
    details["D4_buy_button"] = has_buy_btn
    if has_buy_btn:
        score += 3

    # D5. 환불/교환 정책
    return_kws = ["교환", "반품", "환불", "취소"]
    return_hits = sum(1 for kw in return_kws if kw in text)
    details["D5_return_policy"] = return_hits
    if return_hits >= 2:
        score += 2

    return score, details


def compute_score(html_path: Path, brand: str, channel: str, sku_id: str) -> SixthshopScore:
    raw_html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw_html, "html.parser")
    # 스크립트/스타일 제거 후 텍스트
    text_soup = BeautifulSoup(raw_html, "html.parser")
    for t in text_soup(["script", "style", "noscript"]):
        t.decompose()
    text = text_soup.get_text(separator=" ", strip=True)

    A, Ad = score_schema_data_trust(soup, raw_html)
    B, Bd = score_content_intent(soup, text)
    C, Cd = score_media_visual(soup)
    D, Dd = score_commerce_eligibility(soup, text)

    total = A + B + C + D

    return SixthshopScore(
        brand=brand,
        channel=channel,
        sku_id=sku_id,
        raw_path=str(html_path.relative_to(REPO_ROOT)),
        A_total=A, A_details=Ad,
        B_total=B, B_details=Bd,
        C_total=C, C_details=Cd,
        D_total=D, D_details=Dd,
        total=total,
    )


def main():
    out_path = DATA_PROCESSED / "sixthshop_scores.jsonl"
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    scored = []
    for html_path in DATA_RAW.rglob("*.html"):
        try:
            rel = html_path.relative_to(DATA_RAW)
            parts = rel.parts
            vertical, brand, channel = parts[0], parts[1], parts[2]
            sku_id = html_path.stem.split("_")[0]
        except (ValueError, IndexError):
            continue
        s = compute_score(html_path, brand, channel, sku_id)
        scored.append(s)

    with out_path.open("w", encoding="utf-8") as f:
        for s in scored:
            f.write(s.to_jsonl() + "\n")

    # 요약 출력
    print(f"✅ {len(scored)}개 페이지 점수 산출 → {out_path}\n")
    print(f"{'brand':<14} {'channel':<15} {'sku':<20} {'A/35':<6} {'B/25':<6} {'C/20':<6} {'D/20':<6} {'총점':<6}")
    print("-" * 95)
    for s in sorted(scored, key=lambda s: (-s.total, s.brand)):
        print(f"{s.brand:<14} {s.channel:<15} {str(s.sku_id)[:18]:<20} {s.A_total:<6} {s.B_total:<6} {s.C_total:<6} {s.D_total:<6} {s.total:<6}")


if __name__ == "__main__":
    main()
