"""
B4 Before/After 워터폴 — anchor 페이지(바디닥터/프로폴린스) 개선 시 추천 확률 변화 시뮬.

학습된 XGBoost (shap_pipeline.py) 로드 → anchor row 의 X 변경 (예: JSON-LD 추가, USP HIGH 등)
→ 새 mention 확률 예측 → Δ 계산.

산출:
  ml/results/waterfall/<vertical>/scenarios.csv
  ml/results/waterfall/<vertical>/scenario_comparison.png
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

OUT_DIR = REPO_ROOT / "ml" / "results" / "waterfall"
MODEL_DIR = REPO_ROOT / "ml" / "results" / "shap"

plt.rcParams["font.family"] = "AppleGothic"


# 시나리오 정의 — 컨설팅 권장 액션
# 각 시나리오: anchor row의 X 컬럼을 어떻게 변경할지
SCENARIOS = {
    "current": {},  # baseline
    "JSON_LD_추가": {"auto_has_jsonld": 1, "auto_jsonld_field_count": 6,
                  "six_A_total": 35},
    "임상근거_추가": {"auto_clinical_keyword_count": 5},
    "수치_구체성_보강": {"auto_explicit_number_count": 12,
                  "auto_numeric_specificity_ratio": 0.6},
    "외부_권위_보강": {"news_total": 1000, "blog_total": 5000},
    "전체_개선": {"auto_has_jsonld": 1, "auto_jsonld_field_count": 6,
              "six_A_total": 35, "auto_clinical_keyword_count": 5,
              "auto_explicit_number_count": 12, "news_total": 1000},
}


def simulate(vertical: str):
    import xgboost as xgb

    model_path = MODEL_DIR / vertical / "xgb_model.json"
    if not model_path.exists():
        print(f"⚠️ {model_path} 없음 — shap_pipeline.py 먼저 실행")
        return

    out = OUT_DIR / vertical
    out.mkdir(parents=True, exist_ok=True)

    X, y, brands = build_page_query_xy(vertical)
    if X.empty: return
    X = X.fillna(X.median(numeric_only=True))

    model = xgb.XGBClassifier()
    model.load_model(str(model_path))

    anchor = VERTICAL_ANCHOR[vertical]
    anchor_idx = [i for i, b in enumerate(brands) if b == anchor]
    if not anchor_idx:
        print(f"⚠️ anchor {anchor} 없음"); return

    rows = []
    for scenario, changes in SCENARIOS.items():
        X_mod = X.copy()
        for col, val in changes.items():
            if col in X_mod.columns:
                X_mod.loc[anchor_idx, col] = val
        # anchor 의 모든 query 노출 평균 mention 확률
        proba = model.predict_proba(X_mod.iloc[anchor_idx])[:, 1].mean()
        rows.append({"scenario": scenario, "anchor_mention_prob": proba})

    df = pd.DataFrame(rows)
    baseline = df[df["scenario"] == "current"]["anchor_mention_prob"].iloc[0]
    df["delta_pp"] = (df["anchor_mention_prob"] - baseline) * 100
    df.to_csv(out / "scenarios.csv", index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df["scenario"], df["delta_pp"], color=["gray" if s == "current"
                                                           else "steelblue" for s in df["scenario"]])
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("추천 확률 변화 (%p, vs current)")
    ax.set_title(f"{anchor} 페이지 개선 시나리오 — {vertical}")
    for bar, val in zip(bars, df["delta_pp"]):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, f"{val:+.1f}%p",
                va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(out / "scenario_comparison.png", dpi=100)
    plt.close()

    print(f"  ✅ {anchor} baseline: {baseline:.3f}")
    for _, r in df.iterrows():
        print(f"    {r['scenario']:25} {r['anchor_mention_prob']:.3f} ({r['delta_pp']:+.1f}%p)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    args = p.parse_args()

    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        print(f"\n━━━ Waterfall: {v} ━━━")
        simulate(v)


if __name__ == "__main__":
    main()
