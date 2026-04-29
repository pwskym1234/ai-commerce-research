"""
데마 Baseline: 로지스틱 회귀 (XGBoost/SHAP 전 단계).

왜 baseline이 필요한가 (Harrell 2015, "Regression Modeling Strategies"):
- XGBoost 결과만 보고 바로 SHAP으로 가면 "XGBoost가 정말 필요한지" 검증 없음
- Linear baseline 대비 AUC 차이가 작으면 → XGBoost 불필요 (오컴의 면도날)
- Linear 계수는 SHAP 없이도 직접 해석 가능 (odds ratio + 95% CI)

입력:
  data/processed/features.jsonl          # 크롤링 피처
  data/processed/sixthshop_scores.jsonl  # Sixthshop 점수
  ml/data/observational_runs/<run_id>/observational.jsonl  # Y (브랜드 언급률)

출력:
  ml/results/baseline_logistic/<run_id>/
    ├── coefficients.csv (feature, coef, odds_ratio, 95% CI, p-value)
    ├── metrics.json (AUC, PR-AUC, Brier, calibration)
    ├── calibration_curve.png
    └── forest_plot_odds_ratios.png

사용법:
  python ml/scripts/baseline_logistic.py --obs-run obs_main_20260505_120000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.family"] = "AppleGothic"
matplotlib.rcParams["axes.unicode_minus"] = False

import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import GroupKFold
from sklearn.calibration import calibration_curve


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
ML_DATA = REPO_ROOT / "ml" / "data"
OUT_ROOT = REPO_ROOT / "ml" / "results" / "baseline_logistic"


def load_observational(run_id: str) -> pd.DataFrame:
    path = ML_DATA / "observational_runs" / run_id / "observational.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"관찰형 결과 파일 없음: {path}")
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    return pd.DataFrame(rows)


def aggregate_brand_target(obs_df: pd.DataFrame, our_brand_id: str = "bodydoctor") -> pd.DataFrame:
    """쿼리×반복 응답을 브랜드별 집계.
    현재 관찰형 쿼리는 페이지 없이 단순 AI prior 측정.
    → 각 응답에서 언급된 브랜드(predefined + other) 비율 집계
    → 브랜드별 'AI가 얼마나 언급하는지' = 외부 증거 proxy
    """
    # 각 응답에서 언급된 모든 브랜드 (predefined + other)
    brand_rows = []
    for _, row in obs_df.iterrows():
        all_mentioned = set(row.get("mentioned_predefined") or [])
        other = row.get("other_brands_detected") or []
        for b in other:
            all_mentioned.add(b)
        for brand in all_mentioned:
            brand_rows.append({"brand": brand, "response_id": row.name, "query_type": row["query_type"]})
    if not brand_rows:
        return pd.DataFrame()
    bdf = pd.DataFrame(brand_rows)
    return bdf.groupby("brand").size().reset_index(name="mention_count")


def load_features() -> pd.DataFrame:
    """피처 + Sixthshop 병합."""
    feats = pd.DataFrame([json.loads(l) for l in (DATA_PROCESSED / "features.jsonl").read_text(encoding="utf-8").splitlines()])
    scores = pd.DataFrame([json.loads(l) for l in (DATA_PROCESSED / "sixthshop_scores.jsonl").read_text(encoding="utf-8").splitlines()])
    scores = scores[["brand", "channel", "sku_id", "A_total", "B_total", "C_total", "D_total", "total"]]
    scores = scores.rename(columns={"A_total": "sixth_A", "B_total": "sixth_B",
                                     "C_total": "sixth_C", "D_total": "sixth_D", "total": "sixth_total"})
    df = feats.merge(scores, on=["brand", "channel", "sku_id"], how="left")
    df["has_jsonld_int"] = df["has_jsonld"].astype(int)
    return df


FEATURE_COLS = [
    "text_length", "image_count", "table_count",
    "jsonld_field_count", "has_jsonld_int",
    "cert_keyword_count", "clinical_keyword_count",
    "explicit_number_count", "numeric_specificity_ratio",
    "sixth_A", "sixth_B", "sixth_C", "sixth_D", "sixth_total",
]


def fit_logistic(X: pd.DataFrame, y: np.ndarray) -> dict:
    """statsmodels Logit for p-values + odds ratio + 95% CI.
    주의: 우리 데이터가 본실험 관찰이 아니라 페이지 수준 → binary y는 별도 정의 필요
    이 함수는 일반화 틀. 실제 y는 본실험 후 산출.
    """
    X_const = sm.add_constant(X)
    model = sm.Logit(y, X_const).fit(disp=False)
    params = model.params
    ci = model.conf_int()
    or_df = pd.DataFrame({
        "feature": params.index,
        "coef": params.values,
        "odds_ratio": np.exp(params.values),
        "ci_low": np.exp(ci[0].values),
        "ci_high": np.exp(ci[1].values),
        "p_value": model.pvalues.values,
    })
    return {
        "summary_df": or_df,
        "aic": float(model.aic),
        "pseudo_r2": float(model.prsquared),
        "llf": float(model.llf),
    }


def evaluate(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    metrics = {
        "auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else None,
        "pr_auc": float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else None,
        "brier": float(brier_score_loss(y_true, y_prob)),
        "n": int(len(y_true)),
    }
    return metrics


def forest_plot(summary_df: pd.DataFrame, out_path: Path):
    df = summary_df[summary_df["feature"] != "const"].copy()
    df = df.sort_values("odds_ratio")
    fig, ax = plt.subplots(figsize=(8, max(4, 0.4 * len(df))))
    ypos = np.arange(len(df))
    ax.errorbar(df["odds_ratio"], ypos,
                xerr=[df["odds_ratio"] - df["ci_low"], df["ci_high"] - df["odds_ratio"]],
                fmt="o", color="#1f77b4", ecolor="#888", capsize=3)
    ax.axvline(1, color="red", linestyle="--", alpha=0.5)
    ax.set_yticks(ypos)
    ax.set_yticklabels(df["feature"])
    ax.set_xlabel("Odds Ratio (95% CI)")
    ax.set_xscale("log")
    ax.set_title("로지스틱 회귀 계수 forest plot (OR × 95% CI)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=100)
    plt.close()


def calibration_plot(y_true, y_prob, out_path: Path):
    fraction_of_positives, mean_predicted_value = calibration_curve(y_true, y_prob, n_bins=10)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "k--", label="완벽 보정")
    ax.plot(mean_predicted_value, fraction_of_positives, "o-", label="모델")
    ax.set_xlabel("예측 확률")
    ax.set_ylabel("실제 비율")
    ax.set_title("Calibration curve")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=100)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--obs-run", required=False, help="ml/data/observational_runs/<id>")
    p.add_argument("--target-col", default="y2a_mention", help="학습 타겟 컬럼")
    args = p.parse_args()

    print("=" * 60)
    print("Baseline 로지스틱 회귀 (XGBoost 전 단계)")
    print("=" * 60)

    # 피처 로드
    feat_df = load_features()
    print(f"피처 row: {len(feat_df)}, features: {len(FEATURE_COLS)}")

    if args.obs_run:
        obs_df = load_observational(args.obs_run)
        print(f"관찰형 결과: {len(obs_df)} rows, run_id={args.obs_run}")

        # 브랜드별 mention count 집계
        brand_counts = aggregate_brand_target(obs_df)
        print(f"\n📊 브랜드별 AI 언급률 (상위 10):")
        total = len(obs_df)
        top = brand_counts.sort_values("mention_count", ascending=False).head(10)
        for _, r in top.iterrows():
            rate = r["mention_count"] / total * 100
            print(f"  {r['brand']:<25} {r['mention_count']:>4}회 / {total} = {rate:.1f}%")

        # 본격 merge + 학습은 관찰형 데이터가 브랜드 수준 + 피처가 SKU 수준이라
        # 브랜드별 평균 피처 산출 후 X → brand_counts를 y로 사용
        feat_brand = feat_df.groupby("brand")[FEATURE_COLS].mean().reset_index()
        merged = feat_brand.merge(brand_counts, on="brand", how="left").fillna(0)
        merged["mention_rate"] = merged["mention_count"] / total
        print(f"\n브랜드별 피처-타겟 merge: {len(merged)} rows")

        if len(merged) < 5:
            print("⚠️ 브랜드 수 부족으로 로지스틱 학습 skip. 관찰형 반복 수 늘린 후 재시도")
            return

        X = merged[FEATURE_COLS].fillna(0)
        # binary y: 평균 이상 언급 = 1
        y = (merged["mention_rate"] > merged["mention_rate"].median()).astype(int).values

        # statsmodels Logit
        try:
            result = fit_logistic(X, y)
            out_dir = OUT_ROOT / args.obs_run
            out_dir.mkdir(parents=True, exist_ok=True)
            result["summary_df"].to_csv(out_dir / "coefficients.csv", index=False, encoding="utf-8")
            forest_plot(result["summary_df"], out_dir / "forest_plot_odds_ratios.png")

            # 성능 평가 (in-sample)
            y_prob = sm.Logit(y, sm.add_constant(X)).fit(disp=False).predict(sm.add_constant(X))
            metrics = evaluate(y, np.array(y_prob))
            metrics["aic"] = result["aic"]
            metrics["pseudo_r2"] = result["pseudo_r2"]
            (out_dir / "metrics.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            calibration_plot(y, np.array(y_prob), out_dir / "calibration_curve.png")
            print(f"\n✅ {out_dir}")
            print(f"  AUC: {metrics.get('auc')}, Brier: {metrics.get('brier'):.3f}")
            print(f"  Pseudo R²: {metrics['pseudo_r2']:.3f}")
        except Exception as e:
            print(f"⚠️ 로지스틱 학습 실패: {e}")
            print("   → 관찰형 데이터 확보 후 재시도")
    else:
        print("(skip) --obs-run 인자 없음. 관찰형 쿼리 실행 후 돌리세요:")
        print("  python ml/scripts/run_observational_queries.py --mode main")
        print("  python ml/scripts/baseline_logistic.py --obs-run <run_id>")


if __name__ == "__main__":
    main()
