"""
데마 SHAP 분석 — XGBoost 학습 + 피처 기여도 분해.

입력:
  data/processed/features.jsonl (크롤링 피처)
  data/processed/sixthshop_scores.jsonl (페이지 점수)
  experiments/api_runs/<run_id>/responses.jsonl (Y2a 타겟)

출력:
  ml/results/<run_id>/
    - shap_summary.png (global 피처 중요도)
    - shap_dependence_<feature>.png (개별 피처-예측 관계)
    - shap_waterfall_bodydoctor.png (바디닥터 개별 SKU 예측 분해)
    - feature_importance.csv (gain + SHAP 기여도)
    - model_metrics.json (AUC, PR-AUC, Brier)

사용법:
  python ml/scripts/shap_analysis.py --run-id main_20260505_120000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import GroupKFold


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
EXP_DIR = REPO_ROOT / "experiments"
ML_RESULTS = REPO_ROOT / "ml" / "results"


def load_features() -> pd.DataFrame:
    """피처 + Sixthshop 점수 병합."""
    feats = pd.DataFrame([
        json.loads(l) for l in (DATA_PROCESSED / "features.jsonl").read_text(encoding="utf-8").splitlines()
    ])
    scores = pd.DataFrame([
        json.loads(l) for l in (DATA_PROCESSED / "sixthshop_scores.jsonl").read_text(encoding="utf-8").splitlines()
    ])
    scores = scores[["brand", "channel", "sku_id", "A_total", "B_total", "C_total", "D_total", "total"]]
    scores = scores.rename(columns={
        "A_total": "sixth_schema",
        "B_total": "sixth_content",
        "C_total": "sixth_media",
        "D_total": "sixth_commerce",
        "total": "sixth_total",
    })
    return feats.merge(scores, on=["brand", "channel", "sku_id"], how="left")


def load_responses(run_id: str) -> pd.DataFrame:
    """본실험 응답에서 브랜드별 Y2a 집계."""
    jsonl_path = EXP_DIR / "api_runs" / run_id / "responses.jsonl"
    rows = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines()]
    df = pd.DataFrame(rows)
    # 브랜드별 Y2a 평균 (추천 빈도)
    # 주의: 우리 본실험은 가상 페이지 × 브랜드 N=6 → 각 호출에서 mentioned brand list
    # 데마 관찰 분석에는 "실제 바디닥터 페이지 기준" 필요 → 본실험이 아닌 별도 쿼리 세트가 이상적
    # 여기선 응답 전체에서 바디닥터 언급 비율만 계산
    df["bodydoctor_mentioned"] = df["y2a_mentioned_brand_ids"].apply(lambda ids: "bodydoctor" in (ids or []))
    return df


def get_feature_matrix(feat_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """모델 입력 피처 선정."""
    feature_cols = [
        "text_length", "image_count", "table_count", "list_item_count",
        "paragraph_count", "section_count",
        "jsonld_field_count", "cert_keyword_count", "clinical_keyword_count",
        "explicit_number_count", "ambiguous_term_count", "numeric_specificity_ratio",
        "price_krw",
        "sixth_schema", "sixth_content", "sixth_media", "sixth_commerce", "sixth_total",
    ]
    # has_jsonld boolean → int
    feat_df = feat_df.copy()
    feat_df["has_jsonld"] = feat_df["has_jsonld"].astype(int)
    feature_cols.append("has_jsonld")

    X = feat_df[feature_cols].fillna(0)
    return X, feature_cols


def train_xgb(X: np.ndarray, y: np.ndarray, groups: np.ndarray = None):
    """XGBoost with grouped CV (같은 브랜드가 train/test에 동시 등장 금지)."""
    if groups is not None and len(np.unique(groups)) >= 3:
        gkf = GroupKFold(n_splits=min(3, len(np.unique(groups))))
        splits = list(gkf.split(X, y, groups))
    else:
        # 데이터 부족 시 holdout
        from sklearn.model_selection import train_test_split
        idx_train, idx_test = train_test_split(np.arange(len(X)), test_size=0.3, random_state=42)
        splits = [(idx_train, idx_test)]

    # 1차 fold 사용 (본격은 모든 fold 평균)
    train_idx, test_idx = splits[0]
    X_tr, X_te = X[train_idx], X[test_idx]
    y_tr, y_te = y[train_idx], y[test_idx]

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_tr, y_tr)
    pred = model.predict_proba(X_te)[:, 1]
    metrics = {
        "auc": float(roc_auc_score(y_te, pred)) if len(np.unique(y_te)) > 1 else None,
        "pr_auc": float(average_precision_score(y_te, pred)) if len(np.unique(y_te)) > 1 else None,
        "brier": float(brier_score_loss(y_te, pred)),
        "n_train": int(len(X_tr)),
        "n_test": int(len(X_te)),
    }
    return model, metrics, (X_tr, X_te, y_tr, y_te)


def baseline_logistic(X, y):
    """로지스틱 회귀 baseline (Harrell 권장)."""
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    return model


def run_shap(model, X_test: pd.DataFrame, feature_names: list[str], out_dir: Path, brand_col_for_waterfall: pd.Series = None):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # Global summary
    plt.figure()
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(out_dir / "shap_summary.png", dpi=100)
    plt.close()

    # Dependence plots 상위 피처 3
    mean_abs = np.abs(shap_values).mean(axis=0)
    top_indices = np.argsort(mean_abs)[::-1][:3]
    for idx in top_indices:
        plt.figure()
        shap.dependence_plot(
            idx, shap_values, X_test, feature_names=feature_names, show=False
        )
        plt.tight_layout()
        plt.savefig(out_dir / f"shap_dependence_{feature_names[idx]}.png", dpi=100)
        plt.close()

    # 바디닥터 individual waterfall
    if brand_col_for_waterfall is not None:
        bodydoctor_indices = brand_col_for_waterfall.reset_index(drop=True) == "bodydoctor"
        if bodydoctor_indices.any():
            i = bodydoctor_indices.idxmax()
            plt.figure()
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[i],
                    base_values=explainer.expected_value,
                    data=X_test.iloc[i].values,
                    feature_names=feature_names,
                ),
                show=False,
            )
            plt.tight_layout()
            plt.savefig(out_dir / "shap_waterfall_bodydoctor.png", dpi=100, bbox_inches="tight")
            plt.close()

    # 피처 중요도 CSV
    importance = pd.DataFrame({
        "feature": feature_names,
        "shap_mean_abs": mean_abs,
        "xgb_gain": model.feature_importances_,
    }).sort_values("shap_mean_abs", ascending=False)
    importance.to_csv(out_dir / "feature_importance.csv", index=False)
    return importance


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    args = p.parse_args()

    out_dir = ML_RESULTS / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    feat_df = load_features()
    resp_df = load_responses(args.run_id)

    # 타겟: 브랜드별 본실험 Y2a 비율 (또는 단순 binary)
    # 현재 구조는 산공통 본실험이 가상 페이지 × N=6 비교
    # 데마 관찰 분석에는 별도 "실제 SKU 기준" 쿼리 필요 — 시간 관계상 이 스크립트는 골격
    # 임시: bodydoctor 브랜드 피처만 골라 target = 가상 실험의 평균 멘션율
    print(f"피처 {len(feat_df)} rows, 응답 {len(resp_df)} rows")
    print(f"\n[골격 단계] 실제 실행은 본실험 종료 + 브랜드별 관찰 쿼리 실행 후")
    print(f"데마 분석은 다음 순서:")
    print(f"  1. 경쟁사별 '바디닥터·이지케이·세라젬 등 각각을 명시한 쿼리'로 별도 수집")
    print(f"  2. 브랜드별 Y2a 비율 집계")
    print(f"  3. 각 브랜드 페이지 피처와 merge")
    print(f"  4. XGBoost 학습 + SHAP")

    # Skeleton: 단순 X / y 형태만 구성
    X, feature_cols = get_feature_matrix(feat_df)
    # Dummy y (실제론 브랜드별 멘션율을 실측해야 함)
    print(f"\n피처 매트릭스 shape: {X.shape}")
    print(f"피처: {feature_cols}")
    print(f"\n다음 단계: 실제 y 수집 후 아래 호출")
    print(f"  model, metrics, _ = train_xgb(X.values, y, groups)")
    print(f"  run_shap(model, X, feature_cols, out_dir, feat_df['brand'])")


if __name__ == "__main__":
    main()
