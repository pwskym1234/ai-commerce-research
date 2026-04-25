"""
수동 태깅 템플릿 CSV 자동 생성.

입력: data/processed/sixthshop_scores.jsonl (47 SKU)
출력: data/processed/manual_tags_template.csv

차원: A(T1~T12) + B(Q1~Q8) + 버티컬 분기 (의료기기 M1~M7 / 가글 G1~G7)
참고: docs/knowledge/methods/manual_tagging_guide.md
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SIX_PATH = REPO_ROOT / "data" / "processed" / "sixthshop_scores.jsonl"
OUT_PATH = REPO_ROOT / "data" / "processed" / "manual_tags_template.csv"

GARGLE_BRANDS = {
    "propolinse", "listerine", "garglin", "perio", "2080", "gargle_2080",
    "awesomecool", "therabreath", "usimol", "colgate", "oralb",
    "sensodyne", "kwangdong",
}

# (key, allowed_values, priority) — guide 와 일치
COMMON_DIMENSIONS = [
    # A. 페이지 구조 (12)
    ("T1_format_dominance", "TABLE/BULLET/PARAGRAPH/IMAGE_HEAVY", "P0"),
    ("T2_cert_position", "TOP/MIDDLE/BOTTOM/NONE", "P0"),
    ("T3_evidence_type", "CLINICAL/REVIEWS/MARKETING/VISUAL_DEMO/NONE", "P0"),
    ("T4_section_clarity", "HIGH/MID/LOW", "P1"),
    ("T5_image_category", "LIFESTYLE/PRODUCT_ONLY/INFOGRAPHIC/MIXED", "P1"),
    ("T6_message_tone", "EXPERT/FRIENDLY/SALES", "P1"),
    ("T7_eat_score", "0/1/2/3", "P0"),
    ("T8_cta_type", "BUY/RENTAL/INQUIRY/CONSULT", "P1"),
    ("T9_comparison_present", "YES/NO", "P1"),
    ("T10_usp_clarity", "HIGH/MID/LOW", "P0"),
    ("T11_price_display", "LIST/DISCOUNT/RENTAL/HIDDEN", "P1"),
    ("T12_personalization", "YES/NO", "P1"),
    # B. 공통 정성 (8)
    ("Q1_content_depth", "SHALLOW/MID/DEEP", "P0"),
    ("Q2_safety_disclaimer", "EXPLICIT/IMPLICIT/NONE", "P0"),
    ("Q3_educational_resources", "RICH/SOME/NONE", "P1"),
    ("Q4_social_proof_count", "0~8 (count from checklist)", "P0"),
    ("Q5_return_policy", "CLEAR/PARTIAL/MISSING", "P1"),
    ("Q6_customer_support", "RICH/BASIC/NONE", "P1"),
    ("Q7_trust_claim_tone", "AUTHORITY/HERITAGE/INNOVATION/COMMUNITY/MIXED/WEAK", "P0"),
    ("Q8_retention_mechanism", "YES/NO", "P1"),
]

MEDICAL_DIMENSIONS = [
    ("M1_efficacy_claim", "MEDICAL/FUNCTIONAL/LIFESTYLE/AMBIGUOUS", "P0"),
    ("M2_clinical_evidence", "OWN_TRIAL/LITERATURE/EXPERT/TESTIMONIAL/MARKETING/NONE", "P0"),
    ("M3_kfda_class", "EXPLICIT/PARTIAL/KEYWORD_ONLY/NONE", "P0"),
    ("M4_target_specificity", "SPECIFIC/GENERAL/MISSING", "P0"),
    ("M5_adverse_effects", "FULL/BRIEF/MISSING", "P0"),
    ("M6_manufacturing_origin", "EXPLICIT_OWN/EXPLICIT_OEM/AMBIGUOUS/MISSING", "P1"),
    ("M7_clinical_adoption", "YES_NAMED/YES_GENERIC/NO", "P1"),
]

GARGLE_DIMENSIONS = [
    ("G1_product_class", "EXPLICIT/KEYWORD/MISSING", "P0"),
    ("G2_active_ingredient", "FULL/PARTIAL/KEYWORD/NONE", "P0"),
    ("G3_efficacy_scope", "LICENSED_ONLY/EXPANDED/OVERREACH/AMBIGUOUS", "P0"),
    ("G4_visual_demo", "STRONG/WEAK/NONE", "P0"),
    ("G5_alcohol_display", "EXPLICIT/MENTIONED/MISSING", "P1"),
    ("G6_usage_guidance", "DETAILED/BRIEF/MISSING", "P1"),
    ("G7_origin_display", "EXPLICIT/BRAND_ONLY/MISSING", "P1"),
]


def vertical_of(brand: str) -> str:
    return "gargle" if brand in GARGLE_BRANDS else "medical_device"


def main():
    rows = []
    with SIX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            rows.append({
                "brand": d["brand"],
                "channel": d["channel"],
                "sku_id": d["sku_id"],
                "raw_path": d["raw_path"],
                "vertical": vertical_of(d["brand"]),
                "sixthshop_total": d["total"],
            })

    rows.sort(key=lambda r: (r["vertical"], r["brand"], r["channel"]))

    base_cols = ["brand", "channel", "sku_id", "vertical", "raw_path", "sixthshop_total", "tagger", "notes"]
    common_cols = [d[0] for d in COMMON_DIMENSIONS]
    medical_cols = [d[0] for d in MEDICAL_DIMENSIONS]
    gargle_cols = [d[0] for d in GARGLE_DIMENSIONS]
    all_cols = base_cols + common_cols + medical_cols + gargle_cols

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        # 헤더 가이드 라인 2줄: 컬럼명, 허용 값
        writer = csv.writer(f)
        writer.writerow(all_cols)
        guide_row = [""] * len(base_cols)
        for d in COMMON_DIMENSIONS + MEDICAL_DIMENSIONS + GARGLE_DIMENSIONS:
            guide_row.append(f"{d[1]} ({d[2]})")
        writer.writerow(guide_row)

        for row in rows:
            line = [row.get(c, "") for c in base_cols]
            # 버티컬 분기: 의료기기 row는 G* 컬럼 N/A, 가글 row는 M* 컬럼 N/A
            for col in common_cols:
                line.append("")
            if row["vertical"] == "medical_device":
                line.extend([""] * len(medical_cols))
                line.extend(["N/A"] * len(gargle_cols))
            else:
                line.extend(["N/A"] * len(medical_cols))
                line.extend([""] * len(gargle_cols))
            writer.writerow(line)

    print(f"✅ 템플릿 생성: {OUT_PATH}")
    print(f"   SKU 수: {len(rows)}")
    print(f"   차원 (의료기기): A {len(common_cols)} + B {len(medical_cols)} = {len(common_cols)+len(medical_cols)}")
    print(f"   차원 (가글): A {len(common_cols)} + B {len(gargle_cols)} = {len(common_cols)+len(gargle_cols)}")
    med = [r for r in rows if r["vertical"] == "medical_device"]
    gar = [r for r in rows if r["vertical"] == "gargle"]
    print(f"   판정 총량: {len(med)*(len(common_cols)+len(medical_cols)) + len(gar)*(len(common_cols)+len(gargle_cols))}")


if __name__ == "__main__":
    main()
