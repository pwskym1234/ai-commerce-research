"""
EDA — 변수 분포·결측률·VIF·이상치·Y 클래스 불균형.

태깅 완료 후 풀 EDA 실행. 태깅 비어있으면 자동 X만으로 부분 EDA.

산출:
  ml/results/eda/<vertical>/{distributions, missing, vif, correlations}.csv + .png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
from _data_loader import build_xy_table, aggregate_y_brand_query, list_b1_runs

OUT_DIR = REPO_ROOT / "ml" / "results" / "eda"

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def variable_distributions(df: pd.DataFrame, out: Path):
    """수치형 X 분포 — 히스토그램."""
    num = df.select_dtypes(include="number")
    if num.empty: return
    rows = (len(num.columns) + 3) // 4
    fig, axes = plt.subplots(rows, 4, figsize=(16, rows * 3))
    for i, col in enumerate(num.columns):
        ax = axes.flat[i] if rows > 1 else axes[i % 4]
        num[col].hist(bins=20, ax=ax)
        ax.set_title(col, fontsize=9)
    for j in range(len(num.columns), rows * 4):
        axes.flat[j].axis("off")
    plt.tight_layout()
    plt.savefig(out / "distributions.png", dpi=100)
    plt.close()
    num.describe().to_csv(out / "distributions_summary.csv")


def missingness(df: pd.DataFrame, out: Path):
    """결측률 변수별."""
    miss = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    miss.to_csv(out / "missing_rate.csv", header=["missing_pct"])
    fig, ax = plt.subplots(figsize=(10, max(4, len(miss) * 0.2)))
    miss[miss > 0].plot.barh(ax=ax)
    ax.set_xlabel("결측률 %")
    plt.tight_layout()
    plt.savefig(out / "missing.png", dpi=100)
    plt.close()


def vif_analysis(df: pd.DataFrame, out: Path):
    """다중공선성 VIF — 자동 X 수치 변수만."""
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    num = df.select_dtypes(include="number").dropna(axis=0, how="any")
    if num.shape[1] < 2: return
    num = num.loc[:, num.std() > 0]  # 분산 0 제외
    vifs = []
    for i, c in enumerate(num.columns):
        try:
            v = variance_inflation_factor(num.values, i)
            vifs.append({"variable": c, "VIF": v})
        except Exception:
            vifs.append({"variable": c, "VIF": np.nan})
    pd.DataFrame(vifs).sort_values("VIF", ascending=False).to_csv(out / "vif.csv", index=False)


def correlations(df: pd.DataFrame, out: Path):
    """상관행렬."""
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2: return
    corr = num.corr()
    corr.to_csv(out / "correlation_matrix.csv")
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90, fontsize=7)
    ax.set_yticks(range(len(corr.columns)))
    ax.set_yticklabels(corr.columns, fontsize=7)
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(out / "correlations.png", dpi=100)
    plt.close()


def y_class_balance(vertical: str, out: Path):
    """Y 클래스 불균형."""
    runs = list_b1_runs()
    for mode in ["open", "closed"]:
        run = runs.get(f"{mode}_{vertical[:3]}")
        if not run: continue
        y = aggregate_y_brand_query(run, vertical)
        y.to_csv(out / f"y_class_balance_{mode}.csv", index=False)


def outlier_detection(df: pd.DataFrame, out: Path):
    """IQR 기반 이상치 탐지."""
    num = df.select_dtypes(include="number")
    rows = []
    for c in num.columns:
        s = num[c].dropna()
        if len(s) == 0: continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers_idx = s[(s < lo) | (s > hi)].index.tolist()
        rows.append({"variable": c, "n_outliers": len(outliers_idx),
                     "outlier_indices": outliers_idx[:10]})
    pd.DataFrame(rows).to_csv(out / "outliers_iqr.csv", index=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    args = p.parse_args()

    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        out = OUT_DIR / v
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n━━━ EDA: {v} ━━━")
        df = build_xy_table(v)
        print(f"  X-Y table shape: {df.shape}")
        variable_distributions(df, out)
        missingness(df, out)
        vif_analysis(df, out)
        correlations(df, out)
        y_class_balance(v, out)
        outlier_detection(df, out)
        print(f"  ✅ {out}")


if __name__ == "__main__":
    main()
