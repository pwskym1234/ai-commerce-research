"""
B2 Baseline 모델 — 로지스틱 / 디시젼트리 / KNN.

Wayne 옛 프로젝트 단계 5 + 보강:
  · L1 정규화 로지스틱 (자동 feature selection)
  · DecisionTree (max_depth=4)
  · KNN (k=5)
  · 페이지 단위 mention rate 예측 (의료/가글 분리)

산출:
  ml/results/baseline/<vertical>/{model}_coefficients.csv (logreg)
  ml/results/baseline/<vertical>/{model}_metrics.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegressionCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
from _data_loader import build_xy_table, list_b1_runs, load_b1_responses, VERTICAL_ANCHOR

OUT_DIR = REPO_ROOT / "ml" / "results" / "baseline"


def build_page_query_xy(vertical: str) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """페이지 × 쿼리 단위 X-Y. closed mode B1 활용.

    X: 페이지 피처 (자동 + 태깅 + 외부 증거)
    Y: 해당 호출에서 그 페이지가 mentioned 되었는가 (binary)
    """
    runs = list_b1_runs()
    closed_id = runs.get(f"closed_{vertical[:3]}")
    if not closed_id:
        print(f"⚠️ closed run 없음")
        return pd.DataFrame(), pd.Series(dtype=int), []

    df = load_b1_responses(closed_id, parsed=True)
    if df.empty:
        return pd.DataFrame(), pd.Series(dtype=int), []

    # 페이지 X 테이블
    page_x = build_xy_table(vertical)
    # 페이지 X에서 brand_canonical 단위 1개씩 (best 페이지)
    page_x_best = page_x.groupby("brand_canonical").first().reset_index()

    # 각 호출 × 각 페이지의 mention 여부
    rows = []
    for _, call in df.iterrows():
        mentioned_brands = [b.lower() for b in call.get("mentioned_brands", [])]
        for _, p in page_x_best.iterrows():
            brand_id = p["brand_canonical"].lower()
            mention = any(brand_id in m or m in brand_id for m in mentioned_brands)
            row = {**p.to_dict(), "query_id": call["query_id"],
                   "query_type": call["query_id"].split("-")[0],
                   "repeat_idx": call["repeat_idx"], "mentioned": int(mention)}
            rows.append(row)

    full = pd.DataFrame(rows)
    drop_cols = ["brand_canonical", "channel", "sku_id", "query_id"]
    drop_cols += [c for c in full.columns if full[c].dtype == "object"]
    drop_cols = list(set(drop_cols) - {"mentioned"})
    X = full.drop(columns=[c for c in drop_cols if c in full.columns]).select_dtypes(include="number")
    y = full["mentioned"]
    if "mentioned" in X.columns: X = X.drop(columns=["mentioned"])
    return X, y, full["brand_canonical"].tolist()


def fit_logistic(X, y):
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
        ("clf", LogisticRegressionCV(penalty="l1", solver="saga", cv=5,
                                     max_iter=5000, scoring="roc_auc")),
    ])
    pipe.fit(X, y)
    coefs = pd.DataFrame({
        "feature": X.columns,
        "coefficient": pipe.named_steps["clf"].coef_[0],
    }).sort_values("coefficient", key=abs, ascending=False)
    return pipe, coefs


def fit_decision_tree(X, y):
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("clf", DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=42)),
    ])
    pipe.fit(X, y)
    importances = pd.DataFrame({
        "feature": X.columns,
        "importance": pipe.named_steps["clf"].feature_importances_,
    }).sort_values("importance", ascending=False)
    return pipe, importances


def fit_knn(X, y):
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
        ("clf", KNeighborsClassifier(n_neighbors=5)),
    ])
    pipe.fit(X, y)
    return pipe


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    args = p.parse_args()

    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        print(f"\n━━━ Baseline: {v} ━━━")
        out = OUT_DIR / v
        out.mkdir(parents=True, exist_ok=True)

        X, y, brands = build_page_query_xy(v)
        if X.empty:
            print("  ⚠️ X 비어있음 — skip"); continue
        print(f"  X shape: {X.shape}, Y mean: {y.mean():.3f}")

        # Logistic
        log_pipe, log_coefs = fit_logistic(X, y)
        log_coefs.to_csv(out / "logreg_coefficients.csv", index=False)
        print(f"  ✅ Logistic — top feature: {log_coefs.iloc[0]['feature']} (coef={log_coefs.iloc[0]['coefficient']:.3f})")

        # Decision Tree
        dt_pipe, dt_imp = fit_decision_tree(X, y)
        dt_imp.to_csv(out / "dt_importance.csv", index=False)
        print(f"  ✅ DT — top feature: {dt_imp.iloc[0]['feature']}")

        # KNN
        knn_pipe = fit_knn(X, y)
        print(f"  ✅ KNN fit done")

        # Save metadata
        meta = {"vertical": v, "n_samples": len(y), "n_features": X.shape[1],
                "y_positive_rate": float(y.mean()), "n_brands": len(set(brands))}
        (out / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
