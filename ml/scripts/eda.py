"""
데마 EDA (Exploratory Data Analysis) — 모델링 전 필수 단계.

Wayne 피드백 (2026-04-24):
  "데이터 크롤링·태깅·쿼리 결과 뽑은 다음 분석부터 하고 모델 만들어야"
  → 이 스크립트가 4단계 (EDA), XGBoost/SHAP 는 (7) 단계

입력:
  data/processed/features.jsonl           # 크롤링 피처
  data/processed/sixthshop_scores.jsonl   # Sixthshop 점수
  ml/data/observational_queries.jsonl     # 관찰형 쿼리 결과 (브랜드별 Y2a)

출력:
  ml/results/eda/
    ├── descriptive_stats.csv
    ├── correlation_heatmap.png
    ├── brand_y2a_boxplot.png
    ├── sixthshop_stacked_bar.png
    ├── scatter_top_features.png
    └── findings.md          # EDA 발견 기록 (사람이 읽는 리포트)

사용법:
  python ml/scripts/eda.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.family"] = "AppleGothic"
matplotlib.rcParams["axes.unicode_minus"] = False

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
OUT_DIR = REPO_ROOT / "ml" / "results" / "eda"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    """피처 + Sixthshop 점수 병합."""
    feats = pd.DataFrame([
        json.loads(l) for l in (DATA_PROCESSED / "features.jsonl").read_text(encoding="utf-8").splitlines()
    ])
    scores = pd.DataFrame([
        json.loads(l) for l in (DATA_PROCESSED / "sixthshop_scores.jsonl").read_text(encoding="utf-8").splitlines()
    ])
    scores_slim = scores[["brand", "channel", "sku_id", "A_total", "B_total", "C_total", "D_total", "total"]].rename(columns={
        "A_total": "sixth_schema", "B_total": "sixth_content",
        "C_total": "sixth_media", "D_total": "sixth_commerce",
        "total": "sixth_total",
    })
    df = feats.merge(scores_slim, on=["brand", "channel", "sku_id"], how="left")
    df["has_jsonld_int"] = df["has_jsonld"].astype(int)
    return df


# ========== 1. 기술통계 ==========
def descriptive(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "text_length", "image_count", "table_count", "list_item_count",
        "paragraph_count", "section_count",
        "jsonld_field_count", "cert_keyword_count", "clinical_keyword_count",
        "explicit_number_count", "ambiguous_term_count", "numeric_specificity_ratio",
        "price_krw",
        "sixth_schema", "sixth_content", "sixth_media", "sixth_commerce", "sixth_total",
    ]
    cols_present = [c for c in numeric_cols if c in df.columns]
    stats = df[cols_present].describe().T
    stats["missing"] = df[cols_present].isna().sum()
    stats.to_csv(OUT_DIR / "descriptive_stats.csv", encoding="utf-8")
    return stats


# ========== 2. 브랜드별 박스플롯 ==========
def brand_boxplot(df: pd.DataFrame, metric: str = "sixth_total"):
    if metric not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    brands_order = df.groupby("brand")[metric].median().sort_values(ascending=False).index
    data_per_brand = [df[df["brand"] == b][metric].dropna().values for b in brands_order]
    ax.boxplot(data_per_brand, labels=list(brands_order))
    ax.set_title(f"브랜드별 {metric} 분포")
    ax.set_ylabel(metric)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"brand_{metric}_boxplot.png", dpi=100)
    plt.close()


# ========== 3. Sixthshop 스택바 ==========
def sixthshop_stacked_bar(df: pd.DataFrame):
    needed = ["sixth_schema", "sixth_content", "sixth_media", "sixth_commerce"]
    if not all(c in df.columns for c in needed):
        return
    # 채널별 요약
    agg = df.groupby(["brand", "channel"])[needed].mean().reset_index()
    agg["label"] = agg["brand"] + " | " + agg["channel"]
    agg = agg.sort_values("sixth_schema", ascending=False)
    labels = agg["label"].tolist()
    bottom = np.zeros(len(agg))
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#4c72b0", "#dd8452", "#55a467", "#c44e52"]
    for col, color in zip(needed, colors):
        ax.bar(labels, agg[col], bottom=bottom, label=col, color=color)
        bottom += agg[col].values
    ax.set_ylabel("점수")
    ax.set_title("Sixthshop 점수 적층 (브랜드 × 채널)")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "sixthshop_stacked_bar.png", dpi=100)
    plt.close()


# ========== 4. 상관 heatmap ==========
def correlation_heatmap(df: pd.DataFrame):
    num = df.select_dtypes(include=[np.number])
    # 너무 sparse한 열 제거
    keep = [c for c in num.columns if num[c].notna().sum() > 3 and num[c].nunique() > 1]
    if len(keep) < 3:
        return
    corr = num[keep].corr()
    fig, ax = plt.subplots(figsize=(min(14, 0.5 * len(keep) + 4), min(12, 0.5 * len(keep) + 3)))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(keep)))
    ax.set_yticks(range(len(keep)))
    ax.set_xticklabels(keep, rotation=90)
    ax.set_yticklabels(keep)
    plt.colorbar(im, ax=ax)
    ax.set_title("피처 간 상관 heatmap")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "correlation_heatmap.png", dpi=100)
    plt.close()


# ========== 5. 상위 피처 scatter (vs 타겟) ==========
def scatter_vs_target(df: pd.DataFrame, target: str = "y2a_rate"):
    """target 컬럼이 없으면 (관찰형 쿼리 미실행) skip."""
    if target not in df.columns:
        print(f"  (skip) {target} 컬럼 없음 — 관찰형 쿼리 실행 후 재시도")
        return
    # 상위 상관 4개
    num = df.select_dtypes(include=[np.number])
    corrs = num.corrwith(df[target]).abs().sort_values(ascending=False)
    top = [c for c in corrs.index if c != target][:4]
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, c in zip(axes.flatten(), top):
        ax.scatter(df[c], df[target], alpha=0.6)
        ax.set_xlabel(c)
        ax.set_ylabel(target)
        ax.set_title(f"r = {df[c].corr(df[target]):.2f}")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "scatter_top_features.png", dpi=100)
    plt.close()


# ========== 6. 버티컬 비교 ==========
def vertical_comparison(df: pd.DataFrame):
    if "vertical" not in df.columns:
        return
    by_vert = df.groupby("vertical").agg({
        "text_length": "mean",
        "sixth_total": "mean",
        "has_jsonld_int": "mean",
        "cert_keyword_count": "mean",
        "explicit_number_count": "mean",
    }).round(2)
    by_vert.to_csv(OUT_DIR / "by_vertical.csv", encoding="utf-8")


# ========== 7. 발견 기록 ==========
def write_findings(df: pd.DataFrame):
    md = ["# EDA 발견 (자동 생성)\n"]
    md.append(f"총 {len(df)} rows, {df['brand'].nunique()} 브랜드, {df['channel'].nunique()} 채널\n")

    # 브랜드별 Sixthshop 최고/최저
    if "sixth_total" in df.columns:
        top = df.loc[df["sixth_total"].idxmax()]
        bot = df.loc[df["sixth_total"].idxmin()]
        md.append(f"- Sixthshop 최고: **{top['brand']} / {top['channel']}** — {top['sixth_total']}점")
        md.append(f"- Sixthshop 최저: **{bot['brand']} / {bot['channel']}** — {bot['sixth_total']}점")

    # JSON-LD 보유 비율
    if "has_jsonld_int" in df.columns:
        md.append(f"- JSON-LD 보유 비율: {df['has_jsonld_int'].mean():.1%}")

    # 버티컬별 차이
    if "vertical" in df.columns and "sixth_total" in df.columns:
        by_v = df.groupby("vertical")["sixth_total"].mean()
        for v, s in by_v.items():
            md.append(f"- {v} 평균 Sixthshop: {s:.1f}")

    md.append("\n## 시각화")
    md.append("- `descriptive_stats.csv` — 피처 기술통계")
    md.append("- `brand_sixth_total_boxplot.png` — 브랜드별 박스플롯")
    md.append("- `sixthshop_stacked_bar.png` — 소점수 적층")
    md.append("- `correlation_heatmap.png` — 상관 heatmap")
    md.append("- `scatter_top_features.png` — 타겟과 상관 상위 4 (타겟 있을 때)")

    (OUT_DIR / "findings.md").write_text("\n".join(md), encoding="utf-8")


def main():
    df = load_data()
    print(f"📊 EDA 대상: {len(df)} rows × {df.shape[1]} cols")

    stats = descriptive(df)
    print(f"  ✅ descriptive_stats.csv")

    brand_boxplot(df, "sixth_total")
    brand_boxplot(df, "text_length")
    print(f"  ✅ brand_boxplot")

    sixthshop_stacked_bar(df)
    print(f"  ✅ sixthshop_stacked_bar")

    correlation_heatmap(df)
    print(f"  ✅ correlation_heatmap")

    scatter_vs_target(df, target="y2a_rate")  # 관찰형 쿼리 결과 있을 때만

    vertical_comparison(df)

    write_findings(df)
    print(f"\n✅ 모든 EDA 산출물 → {OUT_DIR}")


if __name__ == "__main__":
    main()
