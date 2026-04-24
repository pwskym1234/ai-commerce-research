"""
산공통 가설 검정 일괄 실행 — H1~H15.

입력:
  experiments/api_runs/<run_id>/responses.jsonl (본실험 결과)
  experiments/synthetic_pages/design_matrix.csv (F 수준 매핑)

출력:
  stats/results/<run_id>/
    - h_tests_summary.csv (가설별 p-value, effect size, CI)
    - h1_f1_main.png ~ h15_q_by_f.png (시각화)
    - interaction_heatmap.png

사용법:
  python stats/scripts/h_tests.py --run-id main_20260505_120000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = REPO_ROOT / "experiments"
STATS_RESULTS = REPO_ROOT / "stats" / "results"


def load_run_data(run_id: str) -> pd.DataFrame:
    """jsonl + design_matrix 결합."""
    jsonl_path = EXP_DIR / "api_runs" / run_id / "responses.jsonl"
    rows = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines()]
    df_runs = pd.DataFrame(rows)

    design_path = EXP_DIR / "synthetic_pages" / "design_matrix.csv"
    df_design = pd.read_csv(design_path)

    df = df_runs.merge(df_design, on="page_id", how="left")
    # Y2a binary
    df["y2a"] = df["y2a_our_selected"].astype(int)
    # Y4 binary
    df["y4"] = df["y4_safety_avoidance"].astype(int)
    return df


# ========== H1~H7: 주효과 ==========
def h1_f1_main_effect(df: pd.DataFrame) -> dict:
    """H1: F1 HTML 포맷이 Y1 파싱 정확도에 영향. (Y1은 별도 측정 필요)
    → 여기선 예시로 Y2a에 대해 F1 주효과."""
    model = smf.logit("y2a ~ C(F1_html)", data=df).fit(disp=False)
    return {
        "hypothesis": "H1 (F1 주효과)",
        "p_value": model.llr_pvalue,
        "pseudo_r2": model.prsquared,
        "coefs": model.params.to_dict(),
    }


def h5_cert_detail_effect(df: pd.DataFrame) -> dict:
    """H5: F5 (인증 상세)가 Y2a 추천 ↑."""
    model = smf.logit("y2a ~ C(F5_cert_detail)", data=df).fit(disp=False)
    # Full vs None 대조
    or_full = np.exp(model.params.get("C(F5_cert_detail)[T.Full]", 0))
    ci = model.conf_int().loc.get("C(F5_cert_detail)[T.Full]")
    return {
        "hypothesis": "H5 (F5 → Y2a)",
        "p_value": model.llr_pvalue,
        "odds_ratio_Full_vs_ref": round(or_full, 3),
        "ci95": [round(np.exp(ci[0]), 3), round(np.exp(ci[1]), 3)] if ci is not None else None,
    }


def h6_cert_reduces_y4(df: pd.DataFrame) -> dict:
    """H6: F5 인증 명시가 Y4 회피 반응 ↓."""
    model = smf.logit("y4 ~ C(F5_cert_detail)", data=df).fit(disp=False)
    return {
        "hypothesis": "H6 (F5 → Y4)",
        "p_value": model.llr_pvalue,
        "coefs": model.params.to_dict(),
    }


# ========== H3, H15: 교호작용 ==========
def h3_f1xf2_interaction(df: pd.DataFrame) -> dict:
    """H3: F1 × F2 교호작용 on Y2a."""
    # 주효과만 모델
    m_main = smf.logit("y2a ~ C(F1_html) + C(F2_jsonld)", data=df).fit(disp=False)
    # 교호작용 포함 모델
    m_int = smf.logit("y2a ~ C(F1_html) * C(F2_jsonld)", data=df).fit(disp=False)
    # Likelihood ratio test
    lr_stat = 2 * (m_int.llf - m_main.llf)
    df_diff = m_int.df_model - m_main.df_model
    p_value = stats.chi2.sf(lr_stat, df_diff)
    return {
        "hypothesis": "H3 (F1×F2 교호작용)",
        "lr_statistic": round(lr_stat, 3),
        "df": int(df_diff),
        "p_value": round(p_value, 5),
    }


def h15_q_by_f(df: pd.DataFrame) -> dict:
    """H15: Q × F 교호작용 (쿼리 유형별 F 효과 차이)."""
    m_main = smf.logit(
        "y2a ~ C(F1_html) + C(F2_jsonld) + C(F5_cert_detail) + C(query_id)",
        data=df
    ).fit(disp=False)
    m_int = smf.logit(
        "y2a ~ C(F1_html) + C(F2_jsonld) + C(F5_cert_detail) + C(query_id) + C(query_id):C(F5_cert_detail)",
        data=df
    ).fit(disp=False)
    lr_stat = 2 * (m_int.llf - m_main.llf)
    df_diff = m_int.df_model - m_main.df_model
    p_value = stats.chi2.sf(lr_stat, df_diff)
    return {
        "hypothesis": "H15 (Q × F5 교호작용)",
        "lr_statistic": round(lr_stat, 3),
        "df": int(df_diff),
        "p_value": round(p_value, 5),
    }


# ========== H8: Y1 ≠ Y2a 상관 ==========
def h8_y1_y2a_decoupling(df: pd.DataFrame) -> dict:
    """H8: 파싱 정확도(Y1)와 선택률(Y2a)이 낮은 상관 (GEO ≠ AiEO)."""
    if "y1_parsing_accuracy" not in df.columns:
        return {"hypothesis": "H8", "status": "Y1 미측정 — 응답 파싱 로직 추가 필요"}
    r, p = stats.pearsonr(df["y1_parsing_accuracy"], df["y2a"])
    return {
        "hypothesis": "H8 (Y1 ≠ Y2a)",
        "pearson_r": round(r, 3),
        "p_value": round(p, 5),
        "interpretation": "r이 작으면 (|r| < 0.3) GEO와 AiEO가 분리됨",
    }


# ========== 종합 모델 (모든 F + Q + 교호) ==========
def full_model(df: pd.DataFrame) -> dict:
    """본실험 메인 회귀 — 모든 주효과 + 주요 교호작용."""
    formula = (
        "y2a ~ C(F1_html) + C(F2_jsonld) + C(F3_numeric) "
        "+ C(F4_cert_pos) + C(F5_cert_detail) + C(F6_evidence) "
        "+ C(query_id) "
        "+ C(F1_html):C(F2_jsonld) "          # H3
        "+ C(F5_cert_detail):C(query_id)"      # H15 대표
    )
    model = smf.logit(formula, data=df).fit(disp=False)
    return {
        "model": "full (주효과 + 핵심 교호작용)",
        "aic": round(model.aic, 2),
        "bic": round(model.bic, 2),
        "pseudo_r2": round(model.prsquared, 4),
        "n_observations": int(model.nobs),
    }


# ========== 이항 비율 95% CI (Wilson) ==========
def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0, 1)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0, center - half), min(1, center + half))


def ci_by_cell(df: pd.DataFrame, group_cols: list) -> pd.DataFrame:
    """각 F 수준 × 쿼리 조합의 Y2a 비율 + Wilson 95% CI."""
    grouped = df.groupby(group_cols).agg(
        n=("y2a", "size"),
        mean=("y2a", "mean"),
    ).reset_index()
    grouped["successes"] = (grouped["mean"] * grouped["n"]).round().astype(int)
    grouped[["ci_low", "ci_high"]] = grouped.apply(
        lambda r: pd.Series(wilson_ci(r["successes"], r["n"])), axis=1
    )
    return grouped


# ========== main ==========
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True, help="experiments/api_runs/<run-id>")
    args = p.parse_args()

    df = load_run_data(args.run_id)
    print(f"📊 {len(df):,} rows loaded from run {args.run_id}")

    out_dir = STATS_RESULTS / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    results.append(h1_f1_main_effect(df))
    results.append(h5_cert_detail_effect(df))
    results.append(h6_cert_reduces_y4(df))
    results.append(h3_f1xf2_interaction(df))
    results.append(h15_q_by_f(df))
    results.append(h8_y1_y2a_decoupling(df))
    results.append(full_model(df))

    # 저장
    summary_path = out_dir / "h_tests_summary.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {summary_path}")

    # 셀별 CI
    cell_ci = ci_by_cell(df, ["F5_cert_detail", "query_id"])
    cell_ci.to_csv(out_dir / "f5xq_wilson_ci.csv", index=False, encoding="utf-8")

    # 출력
    print("\n=== 가설 검정 결과 ===")
    for r in results:
        print(f"\n{r.get('hypothesis', r.get('model'))}")
        for k, v in r.items():
            if k not in ("hypothesis", "model"):
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
