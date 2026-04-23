"""
크롤링한 raw HTML에서 데마 본실험 피처 추출.

입력: data/raw/<vertical>/<brand>/<channel>/<date>/*.html
출력: data/processed/features.parquet (또는 csv)

추출 피처 (CLAUDE.md §1.2):
- HTML 포맷 비율 (TABLE / BULLET / PARAGRAPH)
- JSON-LD 유무 + 필드 수
- 인증 정보 존재/위치 (정규식 + 키워드)
- 수치 구체성 점수 (정확 수치 vs 모호 표현 비율)
- 텍스트 길이
- 이미지 수
- 가격
- 섹션 구분 명확성 (header/section 태그 수)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from dataclasses import dataclass, asdict

from bs4 import BeautifulSoup  # 미설치면 pip install beautifulsoup4

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _base import REPO_ROOT  # noqa: E402

DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# 인증 키워드 (한국 + 영문)
CERT_KEYWORDS = [
    "식약처", "MFDS", "FDA", "CE", "GMP", "ISO 13485",
    "의료기기", "허가번호", "제허", "신고번호", "Class",
    "1등급", "2등급", "3등급", "4등급",
]

# 임상 키워드
CLINICAL_KEYWORDS = ["임상", "RCT", "논문", "연구", "효과 입증", "유의"]

# 수치 패턴 (단위 포함)
NUMBER_PATTERNS = [
    r"\d+\s*(Hz|단계|분|초|mm|cm|kg|g|ml|회|%|개월|년|시간)",
    r"\d+\s*등급",
]

# 모호 표현
AMBIGUOUS_PATTERNS = [
    "강력한", "다양한", "편리한", "효과적", "최고의", "최상의", "탁월한",
]


@dataclass
class PageFeatures:
    raw_path: str
    vertical: str
    brand: str
    channel: str
    sku_id: str

    text_length: int
    image_count: int
    table_count: int
    list_item_count: int
    paragraph_count: int
    section_count: int

    has_jsonld: bool
    jsonld_types: list  # ["Product", "MedicalDevice", ...]
    jsonld_field_count: int

    cert_keyword_count: int
    cert_keyword_first_position: int  # 텍스트 내 첫 등장 위치 (-1 = 없음)
    cert_grade_mentioned: list  # ["3등급"] 등

    clinical_keyword_count: int

    explicit_number_count: int
    ambiguous_term_count: int
    numeric_specificity_ratio: float  # explicit / (explicit + ambiguous)

    price_krw: int  # 추출 실패 시 -1


def extract_features(html_path: Path, vertical: str, brand: str, channel: str, sku_id: str) -> PageFeatures:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    # 텍스트 (script/style 제거)
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)

    # 구조 카운트
    tables = soup.find_all("table")
    list_items = soup.find_all("li")
    paragraphs = soup.find_all("p")
    images = soup.find_all("img")
    sections = soup.find_all(["section", "article", "header", "h1", "h2", "h3"])

    # JSON-LD
    jsonld_scripts = BeautifulSoup(html, "html.parser").find_all("script", type="application/ld+json")
    jsonld_types = []
    jsonld_field_count = 0
    for s in jsonld_scripts:
        try:
            data = json.loads(s.string or "{}")
            items = data if isinstance(data, list) else [data]
            for it in items:
                if isinstance(it, dict):
                    t = it.get("@type")
                    if t:
                        jsonld_types.append(t if isinstance(t, str) else str(t))
                    jsonld_field_count += len(it)
        except Exception:
            pass

    # 인증 키워드
    cert_count = 0
    cert_first = -1
    cert_grades = []
    for kw in CERT_KEYWORDS:
        idx = text.find(kw)
        if idx >= 0:
            cert_count += text.count(kw)
            if cert_first == -1 or idx < cert_first:
                cert_first = idx
            if "등급" in kw and kw in text:
                cert_grades.append(kw)

    # 임상 키워드
    clinical_count = sum(text.count(kw) for kw in CLINICAL_KEYWORDS)

    # 수치 구체성
    explicit_count = 0
    for pat in NUMBER_PATTERNS:
        explicit_count += len(re.findall(pat, text))
    ambiguous_count = sum(text.count(t) for t in AMBIGUOUS_PATTERNS)
    total = explicit_count + ambiguous_count
    specificity = explicit_count / total if total > 0 else 0.0

    # 가격 (한국어)
    price = -1
    price_match = re.search(r"([\d,]+)\s*원", text)
    if price_match:
        try:
            price = int(price_match.group(1).replace(",", ""))
        except ValueError:
            pass

    return PageFeatures(
        raw_path=str(html_path.relative_to(REPO_ROOT)),
        vertical=vertical,
        brand=brand,
        channel=channel,
        sku_id=sku_id,
        text_length=len(text),
        image_count=len(images),
        table_count=len(tables),
        list_item_count=len(list_items),
        paragraph_count=len(paragraphs),
        section_count=len(sections),
        has_jsonld=len(jsonld_scripts) > 0,
        jsonld_types=jsonld_types,
        jsonld_field_count=jsonld_field_count,
        cert_keyword_count=cert_count,
        cert_keyword_first_position=cert_first,
        cert_grade_mentioned=cert_grades,
        clinical_keyword_count=clinical_count,
        explicit_number_count=explicit_count,
        ambiguous_term_count=ambiguous_count,
        numeric_specificity_ratio=specificity,
        price_krw=price,
    )


def main():
    """data/raw/ 전체를 순회해 features.jsonl로 저장."""
    out_path = DATA_PROCESSED / "features.jsonl"
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for html_path in DATA_RAW.rglob("*.html"):
            # 경로에서 메타 추출: data/raw/<vertical>/<brand>/<channel>/<date>/<file>
            try:
                rel = html_path.relative_to(DATA_RAW)
                parts = rel.parts
                vertical, brand, channel = parts[0], parts[1], parts[2]
                sku_id = html_path.stem.split("_")[0]
            except (ValueError, IndexError):
                continue
            features = extract_features(html_path, vertical, brand, channel, sku_id)
            f.write(json.dumps(asdict(features), ensure_ascii=False) + "\n")
            count += 1
    print(f"✅ features 추출 완료: {count}개 페이지 → {out_path}")


if __name__ == "__main__":
    main()
