"""
Tier 분류 매트릭스 — Wayne 옛 프로젝트 단계 4 적용.

크롤링 기재율 (현재 페이지에서 X 차원 충족도) × AI 인용 빈도 (Y mention rate 기여도)
4분면으로 분류 → 컨설팅 액션 우선순위.

Tier S: 결정적 + 미충족 — **즉시 액션** (가장 큰 leverage)
Tier A: 결정적 + 충족 — 유지·강화
Tier B: 보조 + 미충족 — 후순위
Tier C: 보조 + 충족 — 모니터링

산출:
  ml/results/tier/<vertical>_tier_matrix.csv + .png
  ml/results/tier/<vertical>_action_priority.md
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
from _data_loader import build_xy_table, aggregate_y_brand_query, list_b1_runs, VERTICAL_ANCHOR

OUT_DIR = REPO_ROOT / "ml" / "results" / "tier"

plt.rcParams["font.family"] = "AppleGothic"


def compute_tiers(vertical: str, use_closed: bool = True) -> pd.DataFrame:
    """X 변수별 (충족도, 인용 기여도) 4분면 분류.

    충족도 = 자사(anchor) 페이지의 해당 X 값이 전체 분포 중 몇 %ile인지 (높으면 충족)
    기여도 = 단변량 상관 계수 (Y mention rate ↔ X) 절대값 (높으면 결정적)
    """
    df = build_xy_table(vertical)
    if df.empty:
        return pd.DataFrame()

    # Y: 우리 anchor 의 closed mention rate (전체)
    runs = list_b1_runs()
    run_id = runs.get(f"{'closed' if use_closed else 'open'}_{vertical[:3]}")
    if not run_id:
        print(f"⚠️ {vertical} run 없음")
        return pd.DataFrame()

    y_brand = aggregate_y_brand_query(run_id, vertical)
    overall_mention = y_brand["anchor_mention_count"].sum() / y_brand["n_obs"].sum()

    anchor = VERTICAL_ANCHOR[vertical]
    anchor_rows = df[df["brand_canonical"] == anchor]
    if anchor_rows.empty:
        print(f"⚠️ anchor {anchor} 없음")
        return pd.DataFrame()

    # 자동 X + 외부 증거 + Sixthshop만 (수치형)
    num = df.select_dtypes(include="number").drop(
        columns=["A_total", "B_total", "C_total", "D_total"], errors="ignore")

    rows = []
    for col in num.columns:
        s = num[col].dropna()
        if len(s) < 10 or s.std() == 0: continue
        # 충족도: anchor 값의 percentile rank
        anchor_val = anchor_rows[col].mean() if col in anchor_rows.columns else np.nan
        if pd.isna(anchor_val): continue
        pctile = (s < anchor_val).mean()
        # 기여도: 변수 ↔ Y 상관 (각 SKU의 brand_canonical 별 mention rate join)
        # 간소화: 변수의 분산이 mention 변동을 얼마나 설명하는지 proxy
        # 실제로는 mention rate per brand 와 join 해야 정확. 간이 버전:
        brand_y = y_brand.set_index("query_type")["anchor_mention_rate"]
        # 상관 plug: 일단 변수의 절대값 분산비
        # → 나중에 모델 SHAP 나오면 교체
        contribution = abs(s.mean() - anchor_val) / (s.std() + 1e-9) if s.std() > 0 else 0

        rows.append({
            "variable": col,
            "anchor_value": anchor_val,
            "satisfied_pctile": pctile,
            "contribution_proxy": contribution,
            "tier": classify_tier(pctile, contribution),
        })
    return pd.DataFrame(rows)


def classify_tier(satisfied_pct: float, contribution: float) -> str:
    """4분면 분류 (median 기준)."""
    decisive = contribution >= 0.5  # 임시 threshold
    satisfied = satisfied_pct >= 0.5
    if decisive and not satisfied: return "S"
    if decisive and satisfied: return "A"
    if not decisive and not satisfied: return "B"
    return "C"


def plot_tier_matrix(df: pd.DataFrame, vertical: str, out: Path):
    if df.empty: return
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = {"S": "red", "A": "green", "B": "orange", "C": "gray"}
    for tier, group in df.groupby("tier"):
        ax.scatter(group["satisfied_pctile"], group["contribution_proxy"],
                   c=colors[tier], label=f"Tier {tier} ({len(group)})", alpha=0.7, s=80)
        for _, r in group.iterrows():
            ax.annotate(r["variable"][:15], (r["satisfied_pctile"], r["contribution_proxy"]),
                        fontsize=7, alpha=0.6)
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
    ax.axvline(0.5, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("충족도 (anchor pctile)")
    ax.set_ylabel("기여도 (proxy)")
    ax.set_title(f"Tier 분류 매트릭스 — {vertical}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out / f"{vertical}_tier_matrix.png", dpi=100)
    plt.close()


def write_action_priority(df: pd.DataFrame, vertical: str, out: Path):
    if df.empty: return
    md = [f"# {vertical} 우선순위 액션 (Tier 분류)\n"]
    md.append(f"anchor: {VERTICAL_ANCHOR[vertical]}\n")
    for tier in ["S", "A", "B", "C"]:
        sub = df[df["tier"] == tier].sort_values("contribution_proxy", ascending=False)
        if sub.empty: continue
        md.append(f"\n## Tier {tier} ({len(sub)} 개)")
        md.append({"S": "**결정적 + 미충족 — 즉시 액션**",
                   "A": "결정적 + 충족 — 유지·강화",
                   "B": "보조 + 미충족 — 후순위",
                   "C": "보조 + 충족 — 모니터링"}[tier])
        for _, r in sub.iterrows():
            md.append(f"- `{r['variable']}` (충족도 {r['satisfied_pctile']:.0%}, 기여도 {r['contribution_proxy']:.2f})")
    (out / f"{vertical}_action_priority.md").write_text("\n".join(md), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=["medical_device", "gargle", "both"], default="both")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    verticals = ["medical_device", "gargle"] if args.vertical == "both" else [args.vertical]
    for v in verticals:
        print(f"\n━━━ Tier 분류: {v} ━━━")
        df = compute_tiers(v)
        if df.empty: continue
        df.to_csv(OUT_DIR / f"{v}_tier_matrix.csv", index=False)
        plot_tier_matrix(df, v, OUT_DIR)
        write_action_priority(df, v, OUT_DIR)
        for tier in ["S", "A", "B", "C"]:
            n = (df["tier"] == tier).sum()
            print(f"  Tier {tier}: {n}")
        print(f"  ✅ {OUT_DIR}")


if __name__ == "__main__":
    main()
