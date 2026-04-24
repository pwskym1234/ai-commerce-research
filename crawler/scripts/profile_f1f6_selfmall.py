"""
F1~F6 + JSON-LD + 리뷰 정밀 프로파일러.

extract_features.py의 확장: 자사몰 한 브랜드의 다중 페이지를 받아
- F1 HTML 포맷 구성 (TABLE/UL/P 비율 + spec 영역 우세 포맷)
- F2 JSON-LD @type, 키/값 트리, aggregateRating 유무
- F3 수치 구체성 (explicit / ambiguous 비율 + 핵심 클레임 실제 수치 목록)
- F4 인증 위치 (자사몰 상단 nav/메인/푸터 중 어디)
- F5 인증 상세 (번호/기관/등급 포함도)
- F6 근거 (임상/RCT/논문/brand authority/user_reviews)
- 리뷰: aggregateRating, review widgets, 평점/건수

입력: data/raw/<vertical>/<brand>/<channel>/<date>/*.html (인자로 지정)
출력: consulting/diagnosis/<brand>_selfmall_<date>.json
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]

# --- 키워드 사전 ---
CERT_KEYWORDS_GARGLE = ["의약외품", "식약처", "MFDS", "허가", "신고번호", "KFDA"]
CERT_KEYWORDS_MEDICAL = ["의료기기", "식약처", "MFDS", "FDA", "CE", "GMP",
                        "ISO 13485", "허가번호", "제허", "1등급", "2등급", "3등급", "4등급"]
CLINICAL_KEYWORDS = ["임상", "RCT", "논문", "연구", "효과 입증", "유의",
                     "clinical", "study", "trial"]
EVIDENCE_BRAND_AUTHORITY = ["No.1", "글로벌", "세계", "1위", "최초", "original",
                           "world", "global", "#1"]
EVIDENCE_USER_REVIEW = ["후기", "리뷰", "review", "rating", "별점", "평점",
                       "사용자", "구매자"]

# F3 수치 구체성 — 클레임별 정확 수치 패턴
EXPLICIT_NUMBER_PATTERNS = [
    r"\d{1,3}\.?\d*\s*%",              # 99.9%
    r"\d+\s*시간",                      # 12시간
    r"\d+\s*초",                        # 30초
    r"\d+\s*배",                        # 5배
    r"\d+\s*(Hz|단계|분|mm|cm|kg|g|ml|회|개월|년)",
    r"\d+\s*등급",
    r"\d+\s*가지",                      # 4가지 에센셜 오일
    r"\d+\s*성분",
]
AMBIGUOUS_PATTERNS = [
    "강력한", "다양한", "편리한", "효과적", "최고의", "최상의", "탁월한",
    "우수한", "뛰어난", "최신", "혁신적",
]


@dataclass
class PageProfile:
    sku_id: str
    raw_path: str
    html_length: int
    text_length: int

    # F1
    table_count: int
    ul_count: int
    li_count: int
    p_count: int
    section_count: int
    spec_format_dominant: str  # TABLE | BULLET | PARAGRAPH

    # F2
    jsonld_scripts: int
    jsonld_types: list
    jsonld_has_product: bool
    jsonld_has_aggregate_rating: bool
    jsonld_field_count: int
    jsonld_sample: dict

    # F3
    explicit_numbers: list          # 실제 추출된 수치 문자열 (최대 50개)
    explicit_number_count: int
    ambiguous_term_count: int
    numeric_specificity_ratio: float

    # F4/F5
    cert_keyword_count: int
    cert_keywords_found: list
    cert_first_position_ratio: float  # 0.0=맨앞 1.0=맨끝

    # F6
    clinical_keyword_count: int
    brand_authority_count: int
    user_review_count: int
    f6_dominant_evidence: str

    # 리뷰
    review_widget_hints: list
    aggregate_rating_value: float | None
    aggregate_rating_count: int | None


@dataclass
class BrandReport:
    brand: str
    vertical: str
    channel: str
    fetched_date: str
    generated_at: str
    pages: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)


def classify_spec_format(soup: BeautifulSoup) -> str:
    """본문 내 스펙 설명 영역의 우세 포맷."""
    tables = len(soup.find_all("table"))
    lists = len(soup.find_all(["ul", "ol"]))
    paragraphs = len(soup.find_all("p"))
    # 가중치: table이 가장 구조화, ul 중간, p 가장 비구조
    scores = {"TABLE": tables * 3, "BULLET": lists * 2, "PARAGRAPH": paragraphs}
    return max(scores, key=scores.get)


def extract_jsonld(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    types = []
    has_product = False
    has_rating = False
    field_count = 0
    sample = {}
    rating_value = None
    rating_count = None

    for s in scripts:
        try:
            data = json.loads(s.string or "{}")
            items = data if isinstance(data, list) else [data]
            for it in items:
                if not isinstance(it, dict):
                    continue
                t = it.get("@type")
                if t:
                    ts = t if isinstance(t, str) else " ".join(t) if isinstance(t, list) else str(t)
                    types.append(ts)
                    if "Product" in ts or "MedicalDevice" in ts:
                        has_product = True
                field_count += len(it)
                if "aggregateRating" in it:
                    has_rating = True
                    ar = it["aggregateRating"]
                    if isinstance(ar, dict):
                        try:
                            rating_value = float(ar.get("ratingValue", 0)) or None
                            rv = ar.get("reviewCount") or ar.get("ratingCount")
                            rating_count = int(rv) if rv else None
                        except (ValueError, TypeError):
                            pass
                if not sample and isinstance(it, dict):
                    sample = {k: (v if not isinstance(v, (dict, list)) else type(v).__name__)
                              for k, v in list(it.items())[:15]}
        except Exception:
            pass

    return {
        "scripts": len(scripts),
        "types": types,
        "has_product": has_product,
        "has_aggregate_rating": has_rating,
        "field_count": field_count,
        "sample": sample,
        "rating_value": rating_value,
        "rating_count": rating_count,
    }


def extract_explicit_numbers(text: str, limit: int = 50) -> list:
    found = []
    for pat in EXPLICIT_NUMBER_PATTERNS:
        for m in re.finditer(pat, text):
            found.append(m.group(0).strip())
            if len(found) >= limit:
                return found
    return found


def profile_page(html_path: Path, vertical: str) -> PageProfile:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text_len = len(text)

    # F1
    table_c = len(BeautifulSoup(html, "html.parser").find_all("table"))
    ul_c = len(BeautifulSoup(html, "html.parser").find_all(["ul", "ol"]))
    li_c = len(BeautifulSoup(html, "html.parser").find_all("li"))
    p_c = len(BeautifulSoup(html, "html.parser").find_all("p"))
    section_c = len(BeautifulSoup(html, "html.parser").find_all(
        ["section", "article", "header", "h1", "h2", "h3"]))
    dominant = classify_spec_format(BeautifulSoup(html, "html.parser"))

    # F2
    jld = extract_jsonld(html)

    # F3
    explicit_nums = extract_explicit_numbers(text)
    explicit_c = 0
    for pat in EXPLICIT_NUMBER_PATTERNS:
        explicit_c += len(re.findall(pat, text))
    ambiguous_c = sum(text.count(t) for t in AMBIGUOUS_PATTERNS)
    specificity = explicit_c / (explicit_c + ambiguous_c) if (explicit_c + ambiguous_c) > 0 else 0.0

    # F4/F5 — 인증
    cert_keywords = CERT_KEYWORDS_GARGLE if vertical == "gargle" else CERT_KEYWORDS_MEDICAL
    cert_count = 0
    cert_found = []
    first_pos = -1
    for kw in cert_keywords:
        if kw in text:
            c = text.count(kw)
            cert_count += c
            cert_found.append(f"{kw}×{c}")
            idx = text.find(kw)
            if first_pos == -1 or idx < first_pos:
                first_pos = idx
    first_pos_ratio = first_pos / text_len if (text_len > 0 and first_pos >= 0) else -1.0

    # F6 — evidence
    clinical_c = sum(text.count(kw) for kw in CLINICAL_KEYWORDS)
    brand_auth_c = sum(text.count(kw) for kw in EVIDENCE_BRAND_AUTHORITY)
    user_review_c = sum(text.count(kw) for kw in EVIDENCE_USER_REVIEW)
    evidence_scores = {
        "clinical": clinical_c,
        "brand_authority": brand_auth_c,
        "user_reviews": user_review_c,
    }
    dominant_evidence = max(evidence_scores, key=evidence_scores.get) if max(evidence_scores.values()) > 0 else "none"

    # 리뷰 — JSON-LD aggregateRating + 위젯 힌트
    review_widget_hints = []
    for hint in ["review-widget", "reviews-section", "ratingList", "bazaarvoice",
                 "yotpo", "bv_", "powerreviews", "stamped-io", "feefo",
                 "#reviews", "id=\"reviews\"", "class=\"reviews", "review__"]:
        if hint.lower() in html.lower():
            review_widget_hints.append(hint)

    return PageProfile(
        sku_id=html_path.stem,
        raw_path=str(html_path.relative_to(REPO_ROOT)),
        html_length=len(html),
        text_length=text_len,
        table_count=table_c,
        ul_count=ul_c,
        li_count=li_c,
        p_count=p_c,
        section_count=section_c,
        spec_format_dominant=dominant,
        jsonld_scripts=jld["scripts"],
        jsonld_types=jld["types"],
        jsonld_has_product=jld["has_product"],
        jsonld_has_aggregate_rating=jld["has_aggregate_rating"],
        jsonld_field_count=jld["field_count"],
        jsonld_sample=jld["sample"],
        explicit_numbers=explicit_nums,
        explicit_number_count=explicit_c,
        ambiguous_term_count=ambiguous_c,
        numeric_specificity_ratio=round(specificity, 3),
        cert_keyword_count=cert_count,
        cert_keywords_found=cert_found,
        cert_first_position_ratio=round(first_pos_ratio, 3),
        clinical_keyword_count=clinical_c,
        brand_authority_count=brand_auth_c,
        user_review_count=user_review_c,
        f6_dominant_evidence=dominant_evidence,
        review_widget_hints=review_widget_hints,
        aggregate_rating_value=jld["rating_value"],
        aggregate_rating_count=jld["rating_count"],
    )


def build_summary(pages: list[PageProfile]) -> dict:
    """브랜드 전체 요약."""
    # 유효 페이지만 (5KB 이상)
    valid = [p for p in pages if p.html_length > 5000]
    if not valid:
        return {"note": "유효 페이지 없음 (모든 HTML <5KB, 차단 추정)"}

    # F1 우세 포맷 (다수결)
    from collections import Counter
    fmt = Counter(p.spec_format_dominant for p in valid).most_common(1)[0][0]

    # F2 JSON-LD
    all_types = set()
    for p in valid:
        all_types.update(p.jsonld_types)
    any_product = any(p.jsonld_has_product for p in valid)
    any_rating = any(p.jsonld_has_aggregate_rating for p in valid)

    # F3
    avg_spec = sum(p.numeric_specificity_ratio for p in valid) / len(valid)
    all_numbers = []
    for p in valid:
        all_numbers.extend(p.explicit_numbers)
    top_numbers = Counter(all_numbers).most_common(15)

    # F4/F5
    avg_cert_pos = None
    pos_ratios = [p.cert_first_position_ratio for p in valid if p.cert_first_position_ratio >= 0]
    if pos_ratios:
        avg_cert_pos = sum(pos_ratios) / len(pos_ratios)
    all_certs = Counter()
    for p in valid:
        for c in p.cert_keywords_found:
            kw = c.split("×")[0]
            all_certs[kw] += int(c.split("×")[1])

    # F6
    evidence = Counter(p.f6_dominant_evidence for p in valid)

    return {
        "valid_pages": len(valid),
        "f1_spec_format_dominant": fmt,
        "f2_jsonld_types_union": sorted(all_types),
        "f2_has_product_schema": any_product,
        "f2_has_aggregate_rating": any_rating,
        "f3_avg_numeric_specificity": round(avg_spec, 3),
        "f3_top_explicit_numbers": top_numbers,
        "f4_avg_cert_first_position_ratio": round(avg_cert_pos, 3) if avg_cert_pos else None,
        "f4_cert_position_label": (
            "top" if (avg_cert_pos is not None and avg_cert_pos < 0.33)
            else "middle" if (avg_cert_pos is not None and avg_cert_pos < 0.66)
            else "bottom" if avg_cert_pos is not None else "none"
        ),
        "f5_cert_keywords": dict(all_certs),
        "f6_dominant_evidence_distribution": dict(evidence),
        "review_widget_hints_any": sorted({h for p in valid for h in p.review_widget_hints}),
    }


def main(brand_dir: str, vertical: str, channel: str = "self_mall"):
    brand_path = Path(brand_dir)
    if not brand_path.is_absolute():
        brand_path = REPO_ROOT / brand_dir
    assert brand_path.exists(), f"brand 디렉토리 없음: {brand_path}"

    # 최신 날짜 폴더 선택
    date_dirs = sorted([d for d in (brand_path / channel).iterdir() if d.is_dir()])
    assert date_dirs, f"{channel} 내 날짜 폴더 없음"
    date_dir = date_dirs[-1]

    brand_name = brand_path.name
    pages = []
    for html_path in sorted(date_dir.glob("*.html")):
        pages.append(profile_page(html_path, vertical))

    report = BrandReport(
        brand=brand_name,
        vertical=vertical,
        channel=channel,
        fetched_date=date_dir.name,
        generated_at=datetime.now(timezone.utc).isoformat(),
        pages=[asdict(p) for p in pages],
        summary=build_summary(pages),
    )

    out_dir = REPO_ROOT / "consulting" / "diagnosis"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{brand_name}_{channel}_{date_dir.name}.json"
    out_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(f"✅ 저장: {out_path.relative_to(REPO_ROOT)}")

    # 요약 콘솔 출력
    s = report.summary
    print(f"\n--- {brand_name} / {vertical} / {channel} ---")
    for k, v in s.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: profile_f1f6_selfmall.py <brand_dir> <vertical> [channel]")
        sys.exit(1)
    main(*sys.argv[1:])
