"""
B3 XGBoost + SHAP — 페이지 피처 → mention 확률 예측 + 기여도 해석.

산출:
  ml/results/shap/<vertical>/shap_summary.png  (top-N feature 기여도)
  ml/results/shap/<vertical>/shap_dependence/<feature>.png
  ml/results/shap/<vertical>/waterfall_anchor.png  (anchor SKU SHAP)
  ml/results/shap/<vertical>/feature_importance.csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
from baseline_models import build_page_query_xy
from _data_loader import VERTICAL_ANCHOR

OUT_DIR = REPO_ROOT / "ml" / "results" / "shap"

plt.rcParams["font.family"] = "AppleGothic"


def fit_xgboost_and_shap(vertical: str):
    import xgboost as xgb
    import shap

    out = OUT_DIR / vertical
    out.mkdir(parents=True, exist_ok=True)
    (out / "shap_dependence").mkdir(exist_ok=True)

    X, y, brands = build_page_query_xy(vertical)
    if X.empty:
        print(f"⚠️ {vertical} skip"); return

    # 결측 제거
    X = X.fillna(X.median(numeric_only=True))

    pos_weight = (y == 0).sum() / max((y == 1).sum(), 1)
    model = xgb.XGBClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        scale_pos_weight=pos_weight, random_state=42, eval_metric="auc",
        n_jobs=-1,
    )
    model.fit(X, y)

    # SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, max_display=20, show=False)
    plt.tight_layout()
    plt.savefig(out / "shap_summary.png", dpi=100)
    plt.close()

    # Feature importance
    mean_abs_shap = pd.DataFrame({
        "feature": X.columns,
        "mean_abs_shap": np.abs(shap_values).mean(axis=0),
    }).sort_values("mean_abs_shap", ascending=False)
    mean_abs_shap.to_csv(out / "feature_importance.csv", index=False)

    # Top 5 dependence plots
    for f in mean_abs_shap.head(5)["feature"]:
        try:
            plt.figure(figsize=(6, 4))
            shap.dependence_plot(f, shap_values, X, show=False)
            plt.tight_layout()
            plt.savefig(out / f"shap_dependence/{f}.png", dpi=100)
            plt.close()
        except Exception:
            pass

    # Anchor SKU 워터폴 — 우리 anchor row 평균
    anchor = VERTICAL_ANCHOR[vertical]
    anchor_brands = pd.Series(brands)
    anchor_mask = anchor_brands == anchor
    if anchor_mask.any():
        idx = anchor_mask[anchor_mask].index[0]
        try:
            plt.figure(figsize=(8, 6))
            shap.plots._waterfall.waterfall_legacy(
                explainer.expected_value, shap_values[idx], X.iloc[idx],
                max_display=15, show=False,
            )
            plt.tight_layout()
            plt.savefig(out / f"waterfall_{anchor}.png", dpi=100)
            plt.close()
        except Exception as e:
            print(f"  ⚠️ waterfall: {e}")

    # 모델 저장
    model.save_model(str(out / "xgb_model.json"))

    print(f"  ✅ {out}")
    print(f"  Top 5 feature: {mean_abs_shap.head(5)['feature'].tolist()}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    args = p.parse_args()

    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        print(f"\n━━━ XGBoost + SHAP: {v} ━━━")
        fit_xgboost_and_shap(v)


if __name__ == "__main__":
    main()
