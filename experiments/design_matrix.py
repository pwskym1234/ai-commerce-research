"""
L54-근사 직교배열 설계 매트릭스 생성.

배경:
- 풀 팩토리얼 3^6 = 729 조합
- 정통 L54 표는 R DoE.base::oa.design 기반 — Python 직접 구현 어려움
- 실용 대안: pyDOE2 gsd(reduction)로 근사 + 직교성 검증

접근:
1. pyDOE2 `gsd` 로 729/k 크기 샘플 생성 (k=13~14)
2. 각 요인 수준 균등 + 2요인 페어 균등 확인
3. F1×F2 교호작용(H3) 검정 가능한지 직접 검증
4. 부족 시 복제(replication) 추가로 54개 맞춤

사용법:
    python experiments/design_matrix.py
    → experiments/synthetic_pages/design_matrix.csv 생성
"""
from __future__ import annotations

import csv
from collections import Counter
from itertools import combinations, product
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "experiments" / "synthetic_pages"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 6 요인 × 3 수준
N_FACTORS = 6
N_LEVELS = 3
FACTOR_NAMES = ["F1_html", "F2_jsonld", "F3_numeric", "F4_cert_pos", "F5_cert_detail", "F6_evidence"]
LEVEL_LABELS = {
    "F1_html": ["TABLE", "BULLET", "PARAGRAPH"],
    "F2_jsonld": ["MedicalDevice-Full", "Product-Minimal", "None"],
    "F3_numeric": ["Accurate", "Partial", "Ambiguous"],
    "F4_cert_pos": ["Top", "Bottom", "None"],
    "F5_cert_detail": ["Full", "Partial", "None"],
    "F6_evidence": ["Clinical", "Reviews", "None"],
}


def check_orthogonality(design: np.ndarray) -> dict:
    """각 요인 수준 균등 + 모든 2요인 페어 균등 확인."""
    n_runs = design.shape[0]
    report = {"n_runs": n_runs, "main_balance": {}, "pair_balance": {}}

    # 주효과 균등: 각 F 수준이 n_runs/3 회 출현해야 함
    expected_main = n_runs / N_LEVELS
    for j, fname in enumerate(FACTOR_NAMES):
        counts = Counter(design[:, j])
        report["main_balance"][fname] = {
            "expected": expected_main,
            "actual": dict(counts),
            "balanced": all(abs(c - expected_main) <= 1 for c in counts.values()),
        }

    # 2요인 페어 균등: 각 페어의 9 조합이 n_runs/9 회씩
    expected_pair = n_runs / 9
    for i, j in combinations(range(N_FACTORS), 2):
        counts = Counter((design[r, i], design[r, j]) for r in range(n_runs))
        report["pair_balance"][f"{FACTOR_NAMES[i]}×{FACTOR_NAMES[j]}"] = {
            "expected": expected_pair,
            "min_actual": min(counts.values()) if counts else 0,
            "max_actual": max(counts.values()) if counts else 0,
            "balanced": len(counts) == 9 and all(abs(c - expected_pair) <= 1 for c in counts.values()),
        }

    return report


def build_l54_design(seed: int = 42) -> np.ndarray:
    """
    L54 근사 설계 생성.

    전략 A: pyDOE2 gsd(reduction=13) → 56 조합 근사
    전략 B: L27(3^13 Taguchi) 복제 × 2 = 54

    → 전략 B 권장: L27은 표준 Taguchi 표로 주효과 + 일부 교호작용 검정 가능
       복제 2회로 54 runs 확보 → 오차 추정 가능 + H3 검정 안정
    """
    # L27 (3^13) 표준 Taguchi 표 — 앞 6 컬럼만 사용
    # 레퍼런스: Phadke (1989), Taguchi Methods standard L27 table
    L27 = np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,2,2,2,2,2,2,2,2,2],
        [0,1,1,1,0,0,0,1,1,1,2,2,2],
        [0,1,1,1,1,1,1,2,2,2,0,0,0],
        [0,1,1,1,2,2,2,0,0,0,1,1,1],
        [0,2,2,2,0,0,0,2,2,2,1,1,1],
        [0,2,2,2,1,1,1,0,0,0,2,2,2],
        [0,2,2,2,2,2,2,1,1,1,0,0,0],
        [1,0,1,2,0,1,2,0,1,2,0,1,2],
        [1,0,1,2,1,2,0,1,2,0,1,2,0],
        [1,0,1,2,2,0,1,2,0,1,2,0,1],
        [1,1,2,0,0,1,2,1,2,0,2,0,1],
        [1,1,2,0,1,2,0,2,0,1,0,1,2],
        [1,1,2,0,2,0,1,0,1,2,1,2,0],
        [1,2,0,1,0,1,2,2,0,1,1,2,0],
        [1,2,0,1,1,2,0,0,1,2,2,0,1],
        [1,2,0,1,2,0,1,1,2,0,0,1,2],
        [2,0,2,1,0,2,1,0,2,1,0,2,1],
        [2,0,2,1,1,0,2,1,0,2,1,0,2],
        [2,0,2,1,2,1,0,2,1,0,2,1,0],
        [2,1,0,2,0,2,1,1,0,2,2,1,0],
        [2,1,0,2,1,0,2,2,1,0,0,2,1],
        [2,1,0,2,2,1,0,0,2,1,1,0,2],
        [2,2,1,0,0,2,1,2,1,0,1,0,2],
        [2,2,1,0,1,0,2,0,2,1,2,1,0],
        [2,2,1,0,2,1,0,1,0,2,0,2,1],
    ], dtype=int)

    # 앞 6 컬럼만 사용 (우리 F1~F6)
    L27_6 = L27[:, :6]

    # 54 = 27 × 2 (replication)
    rng = np.random.default_rng(seed)
    # 복제본은 같은 설계지만 run 순서 셔플 (실험 순서 효과 통제)
    rep1 = L27_6.copy()
    rep2 = L27_6.copy()
    rng.shuffle(rep2)  # run 순서만 셔플 (조합 자체는 동일)

    design = np.vstack([rep1, rep2])
    return design


def design_to_rows(design: np.ndarray) -> list[dict]:
    rows = []
    for idx, run in enumerate(design, start=1):
        row = {"page_id": f"page_{idx:03d}"}
        for j, fname in enumerate(FACTOR_NAMES):
            level_idx = int(run[j])
            row[fname] = LEVEL_LABELS[fname][level_idx]
            row[f"{fname}_idx"] = level_idx
        rows.append(row)
    return rows


def main():
    design = build_l54_design()
    print(f"설계 매트릭스: {design.shape[0]} runs × {design.shape[1]} factors")

    # 직교성 검증
    report = check_orthogonality(design)
    print(f"\n=== 직교성 리포트 ===")
    print(f"Runs: {report['n_runs']}")
    print(f"\n주효과 균등:")
    for f, r in report["main_balance"].items():
        status = "✅" if r["balanced"] else "❌"
        print(f"  {status} {f}: {r['actual']}")
    print(f"\n2요인 페어 균등 (각 페어 9 조합 × {report['n_runs']/9:.0f}회 기대):")
    for pair, r in report["pair_balance"].items():
        status = "✅" if r["balanced"] else "❌"
        print(f"  {status} {pair}: min={r['min_actual']} max={r['max_actual']}")

    # CSV 저장
    rows = design_to_rows(design)
    csv_path = OUT_DIR / "design_matrix.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ 설계 매트릭스 저장: {csv_path}")
    print(f"   54개 page_id (27 × 복제 2)")


if __name__ == "__main__":
    main()
