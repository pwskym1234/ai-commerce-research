#!/usr/bin/env python3
"""바디닥터 요실금치료기 JSON-LD MedicalDevice 풀스키마 생성기.

산출:
- consulting/diagnosis/bodydoctor_jsonld.json — 풀스키마 (단독 파일)
- consulting/diagnosis/bodydoctor_jsonld_snippet.html — <script> 태그로 감싼 페이지 삽입용

데이터 출처: docs/knowledge/competitors/bodydoctor.md (2026-04-23 검증).

GN 응답 받기 전 자리표시자 (코드에 TBD 주석):
- 식약처 허가번호 (kfda_approval_number)
- FDA 510(k) 번호 (fda_510k_number)
- 정확한 제조사 법인명 (제너럴네트 자체 제조 vs OEM 미확정)
- 실제 제품 이미지 URL
- 임상 데이터 출처 (있는 경우)

리뷰 캠페인 후 활성화:
- aggregateRating (review_count > 0 시 자동 포함)

사용법:
    python scripts/generate_jsonld_bodydoctor.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "consulting" / "diagnosis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 검증된 사실 (bodydoctor.md 기준 + 서울신문 2024-12-26)
PRODUCT = {
    "name": "바디닥터 요실금치료기",
    "model": "단독 모델 (GN 본사 모델명 확인 대기)",
    "manufacturer_name": "제너럴네트 (GN)",
    "manufacturer_url": "https://gncosshop.com",
    "brand_name": "바디닥터",
    # 식약처 (검증됨)
    "kfda_grade": "3",
    "kfda_category": "비이식형 요실금 신경근 전기 자극 장치 + 저주파 의료용 조합 자극기",
    "kfda_approval_number": "TBD-GN-CONFIRM",  # 예: "제허 XX-XXX 호" — GN 응답 후 갱신
    # FDA (검증됨, 등록 등급 — 등록 번호는 별도)
    "fda_classes": ["Class 1", "Class 2"],
    "fda_510k_number": "TBD-GN-CONFIRM",  # K번호 — GN 응답 후 갱신
    # 스펙
    "spec_steps": "99",
    # URL & 이미지
    "url": "https://gncosshop.com/product/detail.html?product_no=187",
    "image_url": "https://gncosshop.com/web/product/big/bodydoctor_main.jpg",  # TBD: 실제 hero image URL
    # 가격
    "price_krw": "2800000",
    "price_currency": "KRW",
    "availability": "https://schema.org/OutOfStock",  # 2026-04-23 기준 단독 품절. 재입고 시 InStock
    "valid_until": "2026-12-31",
    # 의료 적응증 (식약처 등록 카테고리 기반 — 과장 표현 회피)
    "indications": [
        "요실금 치료 (식약처 3등급 의료기기 등록 적응증)",
        "골반저근 약화 회복",
        "출산 후 골반저근 재활",
    ],
    "contraindications": [
        "심박조율기·이식형 의료기기 사용자",
        "임산부 (사용 전 의료진 상담)",
        "전기자극으로 악화될 수 있는 부위 피부 질환자",
    ],
    # 리뷰 (캠페인 후 갱신)
    "review_count": 0,
    "rating_value": None,
}


def build_jsonld(p: dict) -> dict:
    """MedicalDevice 풀스키마 — Schema.org 권장 구조 + 의료기기 특화 PropertyValue."""
    schema: dict = {
        "@context": "https://schema.org",
        "@type": "MedicalDevice",
        "name": p["name"],
        "model": p["model"],
        "url": p["url"],
        "image": p["image_url"],
        "brand": {"@type": "Brand", "name": p["brand_name"]},
        "manufacturer": {
            "@type": "Organization",
            "name": p["manufacturer_name"],
            "url": p["manufacturer_url"],
        },
        "category": p["kfda_category"],
        "indication": [
            {"@type": "MedicalIndication", "name": ind}
            for ind in p["indications"]
        ],
        "contraindication": p["contraindications"],
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "propertyID": "MFDS_grade",
                "name": "식약처 등급",
                "value": p["kfda_grade"],
                "description": "식약처 3등급 조합 의료기기 (가장 엄격한 안전성 평가 등급)",
            },
            {
                "@type": "PropertyValue",
                "propertyID": "MFDS_approval_number",
                "name": "식약처 허가번호",
                "value": p["kfda_approval_number"],
            },
            {
                "@type": "PropertyValue",
                "propertyID": "FDA_class",
                "name": "FDA 등록 등급",
                "value": ", ".join(p["fda_classes"]),
                "description": "FDA Class 1 + Class 2 동시 등록",
            },
            {
                "@type": "PropertyValue",
                "propertyID": "FDA_510k",
                "name": "FDA 510(k) 번호",
                "value": p["fda_510k_number"],
            },
            {
                "@type": "PropertyValue",
                "propertyID": "stimulation_steps",
                "name": "저주파 자극 단계",
                "value": p["spec_steps"],
                "description": "99단계 저주파 자극 — 사용자 맞춤 강도 조절 가능",
            },
        ],
        "offers": {
            "@type": "Offer",
            "url": p["url"],
            "priceCurrency": p["price_currency"],
            "price": p["price_krw"],
            "availability": p["availability"],
            "priceValidUntil": p["valid_until"],
            "seller": {
                "@type": "Organization",
                "name": "GN코스몰",
                "url": p["manufacturer_url"],
            },
        },
    }

    # 리뷰 캠페인 후 활성화
    if p["review_count"] > 0 and p["rating_value"]:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(p["rating_value"]),
            "reviewCount": str(p["review_count"]),
        }

    return schema


def main() -> None:
    data = build_jsonld(PRODUCT)

    json_path = OUT_DIR / "bodydoctor_jsonld.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ JSON: {json_path}")

    snippet = (
        "<!-- JSON-LD MedicalDevice 풀스키마 — <head> 또는 <body> 끝에 삽입 -->\n"
        '<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n</script>\n"
    )
    html_path = OUT_DIR / "bodydoctor_jsonld_snippet.html"
    html_path.write_text(snippet, encoding="utf-8")
    print(f"✓ HTML snippet: {html_path}")

    print("\n검증 도구:")
    print("  - https://validator.schema.org/ (스키마 형식 자체)")
    print("  - https://search.google.com/test/rich-results (Google 인식)")

    print("\nGN 응답 후 갱신해야 할 TBD 필드:")
    for key, val in PRODUCT.items():
        if isinstance(val, str) and "TBD" in val:
            print(f"  - {key}: {val}")


if __name__ == "__main__":
    main()
