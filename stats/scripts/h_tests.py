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


# ========== H2, H4: 파싱 정확도 주효과 ==========
def h2_f2_effect_on_y1(df: pd.DataFrame) -> dict:
    """H2: F2(JSON-LD)가 Y1 파싱 정확도에 영향."""
    if "y1_parsing_accuracy" not in df.columns:
        return {"hypothesis": "H2", "status": "Y1 측정 로직 추가 필요 (runner 보강)"}
    m = smf.ols("y1_parsing_accuracy ~ C(F2_jsonld)", data=df).fit()
    return {
        "hypothesis": "H2 (F2 → Y1)",
        "f_pvalue": float(m.f_pvalue),
        "r2": float(m.rsquared),
        "coefs": m.params.to_dict(),
    }


def h4_f3_effect_on_y1(df: pd.DataFrame) -> dict:
    """H4: F3(수치 구체성)이 Y1 파싱 정확도 ↑."""
    if "y1_parsing_accuracy" not in df.columns:
        return {"hypothesis": "H4", "status": "Y1 측정 로직 추가 필요"}
    m = smf.ols("y1_parsing_accuracy ~ C(F3_numeric)", data=df).fit()
    return {
        "hypothesis": "H4 (F3 → Y1)",
        "f_pvalue": float(m.f_pvalue),
        "r2": float(m.rsquared),
        "coefs": m.params.to_dict(),
    }


# ========== H7: 임상 > 후기 ==========
def h7_clinical_vs_reviews(df: pd.DataFrame) -> dict:
    """H7: F6=Clinical 이 F6=Reviews 보다 Y2a 추천 ↑."""
    sub = df[df["F6_evidence"].isin(["Clinical", "Reviews"])].copy()
    m = smf.logit("y2a ~ C(F6_evidence, Treatment(reference='Reviews'))", data=sub).fit(disp=False)
    or_clinical = np.exp(m.params.get("C(F6_evidence, Treatment(reference='Reviews'))[T.Clinical]", 0))
    return {
        "hypothesis": "H7 (Clinical > Reviews)",
        "p_value": float(m.llr_pvalue),
        "or_clinical_vs_reviews": round(float(or_clinical), 3),
        "n": int(len(sub)),
    }


# ========== H9: 경쟁 상황 ==========
def h9_structure_in_competition(df: pd.DataFrame) -> dict:
    """H9: 경쟁 상황에서 F1(구조화 포맷) 효과가 더 큰가.
       → 본 설계는 항상 경쟁 상황(N=6). 단독 베이스라인 없음.
       → EXPLORATORY로 처리. '경쟁사 응답 수' 변동으로 proxy."""
    if "products_order" not in df.columns:
        return {"hypothesis": "H9", "status": "products_order 필드로 경쟁 강도 proxy 필요"}
    df = df.copy()
    df["n_competitors_mentioned"] = df["y2a_mentioned_brand_ids"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    m = smf.logit("y2a ~ C(F1_html) * n_competitors_mentioned", data=df).fit(disp=False)
    return {
        "hypothesis": "H9 (F1 × 경쟁 강도 EXPLORATORY)",
        "p_value": float(m.llr_pvalue),
        "pseudo_r2": float(m.prsquared),
    }


# ========== H10: 의료기기/비의료기기 구분 ==========
def h10_medical_vs_non(df: pd.DataFrame) -> dict:
    """H10: AI가 비의료기기 노이즈(닥터케이 등)를 섞어 추천하는가.
       → 응답에서 'drk' (닥터케이) 언급률 측정."""
    df = df.copy()
    df["mentions_noise_drk"] = df["y2a_mentioned_brand_ids"].apply(lambda x: "drk" in (x or []))
    rate_noise = df["mentions_noise_drk"].mean()
    rate_bodydoctor = df["y2a"].mean()
    return {
        "hypothesis": "H10 (비의료기기 혼용)",
        "drk_mention_rate": round(float(rate_noise), 4),
        "bodydoctor_mention_rate": round(float(rate_bodydoctor), 4),
        "note": "drk 언급률이 높으면 AI가 카테고리 구분 실패",
    }


# ========== H11: 쿼리 키워드 명시 효과 ==========
def h11_medical_keyword_effect(df: pd.DataFrame) -> dict:
    """H11: '의료기기' 키워드 포함 쿼리(SYM, DEC 일부)에서 노이즈 혼용 ↓.
       → 쿼리 유형별 drk 언급률 비교."""
    df = df.copy()
    df["mentions_noise_drk"] = df["y2a_mentioned_brand_ids"].apply(lambda x: "drk" in (x or []))
    by_qtype = df.groupby("query_id")["mentions_noise_drk"].mean().to_dict()
    return {
        "hypothesis": "H11 (쿼리 키워드 × 카테고리 구분)",
        "drk_rate_by_query": {k: round(float(v), 4) for k, v in by_qtype.items()},
        "note": "SYM/DEC (증상·의료기기 키워드) 쿼리의 drk_rate가 CAT보다 낮으면 H11 지지",
    }


# ========== H12: Rufus SPN (USE × F6) ==========
def h12_spn_use_interaction(df: pd.DataFrame) -> dict:
    """H12: USE 쿼리 × F6(근거) 교호작용 — SPN 맥락 서술이 근거 효과를 증폭하는가."""
    # 쿼리에서 유형 추출 (query_id = "USE-1" 등)
    df = df.copy()
    df["q_is_use"] = df["query_id"].str.startswith("USE-")
    m_main = smf.logit("y2a ~ C(F6_evidence) + q_is_use", data=df).fit(disp=False)
    m_int = smf.logit("y2a ~ C(F6_evidence) * q_is_use", data=df).fit(disp=False)
    lr = 2 * (m_int.llf - m_main.llf)
    dfd = m_int.df_model - m_main.df_model
    p = stats.chi2.sf(lr, dfd)
    return {
        "hypothesis": "H12 (USE × F6 SPN)",
        "lr_statistic": round(float(lr), 3),
        "df": int(dfd),
        "p_value": round(float(p), 5),
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
    # 주효과
    results.append(h1_f1_main_effect(df))
    results.append(h2_f2_effect_on_y1(df))
    results.append(h4_f3_effect_on_y1(df))
    results.append(h5_cert_detail_effect(df))
    results.append(h6_cert_reduces_y4(df))
    results.append(h7_clinical_vs_reviews(df))
    # 교호작용
    results.append(h3_f1xf2_interaction(df))
    results.append(h9_structure_in_competition(df))
    results.append(h12_spn_use_interaction(df))
    results.append(h15_q_by_f(df))
    # 탐색·관찰
    results.append(h8_y1_y2a_decoupling(df))
    results.append(h10_medical_vs_non(df))
    results.append(h11_medical_keyword_effect(df))
    # 종합
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
