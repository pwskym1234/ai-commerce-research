"""
CV 평가 — 5-fold + LOOCV + Bootstrap 95% CI.

Wayne 옛 프로젝트 단계 6: precision / recall / F1 / AUROC + Brier / PR-AUC.

산출:
  ml/results/cv/<vertical>/cv_metrics.csv
  ml/results/cv/<vertical>/bootstrap_ci.csv
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
from sklearn.model_selection import StratifiedKFold, LeaveOneOut, cross_val_predict
from sklearn.metrics import (precision_score, recall_score, f1_score, roc_auc_score,
                              brier_score_loss, average_precision_score)
from sklearn.utils import resample

import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ml" / "scripts"))
from baseline_models import build_page_query_xy, fit_logistic, fit_decision_tree, fit_knn

OUT_DIR = REPO_ROOT / "ml" / "results" / "cv"


def make_pipe(model: str):
    if model == "logreg":
        return Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("clf", LogisticRegressionCV(penalty="l1", solver="saga", cv=3, max_iter=2000))])
    if model == "dt":
        return Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("clf", DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=42))])
    if model == "knn":
        return Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("sc", StandardScaler()),
                         ("clf", KNeighborsClassifier(n_neighbors=5))])


def evaluate_metrics(y_true, y_pred, y_proba):
    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "auroc": roc_auc_score(y_true, y_proba) if len(set(y_true)) > 1 else np.nan,
        "pr_auc": average_precision_score(y_true, y_proba) if len(set(y_true)) > 1 else np.nan,
        "brier": brier_score_loss(y_true, y_proba),
    }


def kfold_eval(X, y, model: str, n_splits=5):
    pipe = make_pipe(model)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    pred = cross_val_predict(pipe, X, y, cv=skf, method="predict")
    proba = cross_val_predict(pipe, X, y, cv=skf, method="predict_proba")[:, 1]
    return evaluate_metrics(y, pred, proba)


def loocv_eval(X, y, model: str):
    """LOOCV — 표본 작을 때 5-fold 보다 안정."""
    if len(y) > 200:
        return None  # too slow for 페이지×쿼리 (수천건)
    pipe = make_pipe(model)
    pred = cross_val_predict(pipe, X, y, cv=LeaveOneOut(), method="predict")
    proba = cross_val_predict(pipe, X, y, cv=LeaveOneOut(), method="predict_proba")[:, 1]
    return evaluate_metrics(y, pred, proba)


def bootstrap_ci(X, y, model: str, n_boot=200, seed=42):
    """Bootstrap 95% CI for AUROC."""
    pipe = make_pipe(model)
    pipe.fit(X, y)
    rng = np.random.default_rng(seed)
    aurocs = []
    n = len(y)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(set(y.iloc[idx])) < 2: continue
        proba = pipe.predict_proba(X.iloc[idx])[:, 1]
        aurocs.append(roc_auc_score(y.iloc[idx], proba))
    return {"auroc_mean": np.mean(aurocs), "auroc_2.5": np.percentile(aurocs, 2.5),
            "auroc_97.5": np.percentile(aurocs, 97.5), "n_boot": len(aurocs)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    p.add_argument("--n-boot", type=int, default=200)
    args = p.parse_args()

    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        print(f"\n━━━ CV: {v} ━━━")
        out = OUT_DIR / v
        out.mkdir(parents=True, exist_ok=True)

        X, y, _ = build_page_query_xy(v)
        if X.empty: print("  skip"); continue
        print(f"  X={X.shape}, Y mean={y.mean():.3f}")

        rows = []
        for model in ["logreg", "dt", "knn"]:
            r = {"model": model, "vertical": v}
            r.update({f"5fold_{k}": v_ for k, v_ in kfold_eval(X, y, model).items()})
            loo = loocv_eval(X, y, model)
            if loo:
                r.update({f"loocv_{k}": v_ for k, v_ in loo.items()})
            rows.append(r)
            print(f"  ✅ {model} 5fold AUROC={r['5fold_auroc']:.3f} F1={r['5fold_f1']:.3f}")

        pd.DataFrame(rows).to_csv(out / "cv_metrics.csv", index=False)

        # Bootstrap CI for best (logreg)
        boot = bootstrap_ci(X, y, "logreg", n_boot=args.n_boot)
        pd.DataFrame([boot]).to_csv(out / "bootstrap_ci.csv", index=False)
        print(f"  Bootstrap AUROC 95% CI: ({boot['auroc_2.5']:.3f}, {boot['auroc_97.5']:.3f})")


if __name__ == "__main__":
    main()
