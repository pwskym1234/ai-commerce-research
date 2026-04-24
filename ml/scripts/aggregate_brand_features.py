"""
SKU 매칭 + brand-level 집계 (1차 발표 피드백 2.3 반영).

입력: data/processed/features.jsonl (brand × channel × sku_id 단위 row)
출력: data/processed/brand_aggregated_features.jsonl (brand 단위)

집계 방식:
- 수치형 피처: 평균(mean) + 최대(max) + row 수(n_skus_crawled)
- Sixthshop 점수도 함께 join 해서 brand별 평균/최대
- 외부 증거(external_evidence.jsonl) 있으면 left join

주의:
- 한국 식약처 미등록 공산품(페로니언/애플힙 등)은 복수 채널에서 판매되어 여러 SKU로 등장
- brand-level 집계로 "같은 제품의 채널별 표기 차이"는 compress
- 채널별 차이 자체를 분석하려면 원본 features.jsonl 사용 (아직 있음)
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
FEAT_PATH = REPO_ROOT / "data" / "processed" / "features.jsonl"
SIX_PATH = REPO_ROOT / "data" / "processed" / "sixthshop_scores.jsonl"
EXT_PATH = REPO_ROOT / "data" / "processed" / "external_evidence.jsonl"
OUT_PATH = REPO_ROOT / "data" / "processed" / "brand_aggregated_features.jsonl"


def read_jsonl(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def main():
    feat = read_jsonl(FEAT_PATH)
    six = read_jsonl(SIX_PATH)

    # Sixthshop: brand × channel × sku_id 로 key → brand별 평균/최대
    six_by_brand = (
        six.groupby("brand")
        .agg(
            sixthshop_mean=("total", "mean"),
            sixthshop_max=("total", "max"),
            sixthshop_median=("total", "median"),
            n_skus_scored=("total", "size"),
        )
        .reset_index()
    )

    # Features: 수치형 피처 추출 → brand별 집계
    # features.jsonl 의 실제 컬럼은 스크립트마다 다를 수 있음 → object 제외하고 자동 집계
    numeric_cols = feat.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        feat_by_brand = feat.groupby("brand")[numeric_cols].agg(["mean", "max"])
        # 컬럼 flatten
        feat_by_brand.columns = [f"{c}_{a}" for c, a in feat_by_brand.columns]
        feat_by_brand = feat_by_brand.reset_index()
        feat_by_brand["n_skus_features"] = feat.groupby("brand").size().values
    else:
        feat_by_brand = pd.DataFrame({"brand": feat["brand"].unique()})
        feat_by_brand["n_skus_features"] = feat.groupby("brand").size().values

    # Merge
    merged = six_by_brand.merge(feat_by_brand, on="brand", how="outer")

    # External evidence (optional)
    if EXT_PATH.exists():
        ext = read_jsonl(EXT_PATH)
        if not ext.empty:
            ext = ext.rename(columns={"brand_id": "brand"})
            merged = merged.merge(
                ext[["brand", "blog_total", "cafe_total", "news_total", "shop_total"]],
                on="brand",
                how="left",
            )
    else:
        print("ℹ️  external_evidence.jsonl 없음 — NAVER API 키 설정 후 collect_external_evidence.py 실행")

    # Write
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for _, row in merged.iterrows():
            f.write(json.dumps(row.to_dict(), ensure_ascii=False, default=str) + "\n")

    print(f"✅ brand 집계 완료 — {len(merged)} 브랜드 → {OUT_PATH}")
    # 요약 출력
    cols_preview = ["brand", "sixthshop_mean", "sixthshop_max", "n_skus_scored"]
    cols_preview = [c for c in cols_preview if c in merged.columns]
    print("\n" + merged[cols_preview].sort_values("sixthshop_mean", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
