"""
공통 데이터 로딩 — features + manual_tags + Y(B1) + external_evidence + sixthshop.

모든 분석 모듈(eda/tier/baseline/shap/waterfall)이 import.
manual_tags 가 비어있으면 자동 X만으로 동작 (graceful degradation).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = REPO_ROOT / "data" / "processed"
B1_RUNS = REPO_ROOT / "ml" / "data" / "b1_runs"

VERTICAL_ANCHOR = {"medical_device": "bodydoctor", "gargle": "propolinse"}

FEATURE_BRAND_ALIAS = {
    "furun": "furenhealth",
    "2080": "gargle_2080",
}

# 채널 → 자사몰 / 리테일 분류 (Wayne 결정 2026-04-25, 옵션 C 채널 통제)
CHANNEL_TYPE_MAP = {
    # 자사·제조사 채널
    "self_mall": "owned",
    "gncosshop": "owned",
    "manufacturer_site": "owned",
    "hiliving_mall": "owned",
    "lgcaremall": "owned",
    "coreatech": "owned",
    "official_global": "owned",
    # 리테일·오픈마켓
    "11st": "retail",
    "smartstore": "retail",
    "coupang": "retail",
    "kakao_store": "retail",
    "gsshop": "retail",
    "ssg": "retail",
    "dmall": "retail",
    "oliveyoung": "retail",
    "emart_mall": "retail",
}


def channel_type_of(channel: str) -> str:
    return CHANNEL_TYPE_MAP.get(channel, "unknown")


def read_jsonl(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.DataFrame(json.loads(l) for l in path.open("r", encoding="utf-8"))


def load_features() -> pd.DataFrame:
    """features.jsonl 로드 + brand_canonical 컬럼 추가."""
    df = read_jsonl(PROCESSED / "features.jsonl")
    df["brand_canonical"] = df["brand"].map(lambda b: FEATURE_BRAND_ALIAS.get(b, b))
    return df


def load_manual_tags() -> pd.DataFrame:
    """manual_tags.jsonl 로드. 없거나 비어있으면 빈 DataFrame."""
    p = PROCESSED / "manual_tags.jsonl"
    return read_jsonl(p)


def load_external_evidence() -> pd.DataFrame:
    """NAVER 검색 카운트 (브랜드 단위)."""
    df = read_jsonl(PROCESSED / "external_evidence.jsonl")
    if not df.empty:
        df = df.rename(columns={"brand_id": "brand_canonical"})
    return df


def load_sixthshop() -> pd.DataFrame:
    """Sixthshop 점수 (sku 단위). vertical 은 raw_path 에서 추출."""
    df = read_jsonl(PROCESSED / "sixthshop_scores.jsonl")
    df["brand_canonical"] = df["brand"].map(lambda b: FEATURE_BRAND_ALIAS.get(b, b))
    # raw_path: data/raw/<vertical>/<brand>/<channel>/...
    df["vertical"] = df["raw_path"].str.split("/").str[2]
    return df


def load_brand_aggregated() -> pd.DataFrame:
    return read_jsonl(PROCESSED / "brand_aggregated_features.jsonl")


def load_b1_responses(run_id: str, parsed: bool = True) -> pd.DataFrame:
    """B1 본실험 응답 로드. parsed=True면 Claude haiku 정밀 파싱본."""
    fname = "parsed_claude.jsonl" if parsed else "b1.jsonl"
    return read_jsonl(B1_RUNS / run_id / fname)


def list_b1_runs() -> dict:
    """현재 디렉토리의 가장 최근 4 run_id (open/closed × med/gar) 자동 탐지."""
    runs = sorted([p.name for p in B1_RUNS.glob("b1_*") if p.is_dir()], reverse=True)
    out = {}
    for prefix in ["b1_open_medical_device", "b1_closed_medical_device",
                   "b1_open_gargle", "b1_closed_gargle"]:
        match = next((r for r in runs if r.startswith(prefix)), None)
        if match:
            out[prefix.replace("b1_", "").replace("_medical_device", "_med")
                .replace("_gargle", "_gar")] = match
    return out


def aggregate_y_brand_query(b1_run_id: str, vertical: str) -> pd.DataFrame:
    """B1 응답을 brand × query_type 단위로 집계 → mention_rate."""
    df = load_b1_responses(b1_run_id, parsed=True)
    if df.empty:
        return pd.DataFrame()

    anchor = VERTICAL_ANCHOR.get(vertical, "bodydoctor")
    df["query_type"] = df["query_id"].str.split("-").str[0]

    # brand × query_type → mention_rate (anchor 기준)
    agg = df.groupby("query_type").agg(
        n_obs=("our_mention", "size"),
        anchor_mention_count=("our_mention", "sum"),
    ).reset_index()
    agg["anchor_mention_rate"] = agg["anchor_mention_count"] / agg["n_obs"]
    agg["vertical"] = vertical
    agg["anchor"] = anchor
    agg["b1_run_id"] = b1_run_id
    return agg


def aggregate_y_page_level(closed_run_id: str, vertical: str) -> pd.DataFrame:
    """B1-B 응답을 페이지(brand) × query_type 단위로 집계.

    각 호출의 mentioned_brands 에서 sku 단위 추출 → 페이지 단위 mention rate.
    """
    df = load_b1_responses(closed_run_id, parsed=True)
    if df.empty:
        return pd.DataFrame()

    df["query_type"] = df["query_id"].str.split("-").str[0]

    rows = []
    # 각 query_type 의 모든 brand 노출 횟수 카운트
    for qt, group in df.groupby("query_type"):
        n_calls = len(group)
        # mentioned_brands 자유 형식 — competitor id 매핑 필요
        from collections import Counter
        brand_count = Counter()
        for _, row in group.iterrows():
            for b in row["mentioned_brands"]:
                # 브랜드명 정규화 (대소문자·공백)
                brand_count[b.strip().lower()] += 1
        for b, c in brand_count.most_common():
            rows.append({
                "vertical": vertical, "query_type": qt,
                "brand_text": b, "mention_count": c, "n_calls": n_calls,
                "mention_rate": c / n_calls,
            })
    return pd.DataFrame(rows)


def build_xy_table(
    vertical: str,
    use_manual_tags: bool = True,
    use_external_evidence: bool = True,
) -> pd.DataFrame:
    """X (페이지 피처 + 태깅 + 외부 증거) join + Y (anchor mention rate per query type)."""
    feats = load_features()
    feats = feats[feats["vertical"] == vertical].copy()
    feats["channel_type"] = feats["channel"].map(CHANNEL_TYPE_MAP).fillna("unknown")

    # 자동 X 컬럼만 (numeric)
    drop_cols = ["raw_path", "vertical", "brand", "channel", "sku_id",
                 "brand_canonical", "jsonld_types", "cert_grade_mentioned"]
    auto_x = feats.drop(columns=[c for c in drop_cols if c in feats.columns]).select_dtypes(include="number")
    auto_x.columns = [f"auto_{c}" for c in auto_x.columns]
    feats_x = pd.concat([feats[["brand_canonical", "channel", "sku_id"]].reset_index(drop=True),
                         auto_x.reset_index(drop=True)], axis=1)

    # Sixthshop 점수
    six = load_sixthshop()
    six_x = six[six["vertical"] == vertical][["brand_canonical", "channel", "sku_id",
                                                "A_total", "B_total", "C_total", "D_total", "total"]]
    six_x.columns = [c if c in ["brand_canonical", "channel", "sku_id"] else f"six_{c}"
                     for c in six_x.columns]

    df = feats_x.merge(six_x, on=["brand_canonical", "channel", "sku_id"], how="left")

    # 수동 태깅 (있으면)
    if use_manual_tags:
        tags = load_manual_tags()
        if not tags.empty:
            df = df.merge(tags, on=["brand", "channel", "sku_id"], how="left", suffixes=("", "_tag"))

    # 외부 증거 (브랜드 단위)
    if use_external_evidence:
        ext = load_external_evidence()
        if not ext.empty:
            df = df.merge(ext[["brand_canonical", "blog_total", "cafe_total",
                                "news_total", "shop_total"]],
                          on="brand_canonical", how="left")
    return df


if __name__ == "__main__":
    runs = list_b1_runs()
    print("B1 run_ids 자동 탐지:")
    for k, v in runs.items():
        print(f"  {k}: {v}")
    print()
    for v in ["medical_device", "gargle"]:
        df = build_xy_table(v)
        print(f"\n{v}: shape={df.shape}, columns={list(df.columns)[:8]}...")
        if "open_med" in str(runs):
            run = runs.get(f"open_{v[:3]}")
            if run:
                y = aggregate_y_brand_query(run, v)
                print(f"  Y (anchor mention rate by query_type):")
                print(y[["query_type", "n_obs", "anchor_mention_rate"]].to_string(index=False))
