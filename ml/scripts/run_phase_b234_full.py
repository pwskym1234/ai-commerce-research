"""
Phase B2/B3/B4 풀 wrapper — 태깅 완료 후 한 명령으로 전체 분석 실행.

순서:
  1. EDA (분포·결측·VIF·이상치)
  2. Tier 분류 매트릭스
  3. Baseline 모델 (logreg/DT/KNN)
  4. CV 평가 (5-fold + LOOCV + Bootstrap)
  5. XGBoost + SHAP
  6. Before/After 워터폴

사용:
  python ml/scripts/run_phase_b234_full.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "ml" / "scripts"

PIPELINE = [
    ("EDA", "eda_analysis.py"),
    ("Tier 분류", "tier_classifier.py"),
    ("Baseline 모델", "baseline_models.py"),
    ("CV 평가", "cv_evaluation.py"),
    ("XGBoost + SHAP", "shap_pipeline.py"),
    ("Before/After 워터폴", "waterfall_simulator.py"),
]


def run_step(label: str, script: str):
    print(f"\n{'━' * 60}\n  Step: {label}\n{'━' * 60}")
    t0 = time.time()
    try:
        subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)
        print(f"  ✅ {time.time() - t0:.0f}s")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {label} 실패: {e}")
        return False
    return True


def main():
    print("🎯 Phase B2/B3/B4 풀 분석")
    t0 = time.time()
    for label, script in PIPELINE:
        ok = run_step(label, script)
        if not ok:
            print(f"\n중단: {label} 단계 실패")
            break
    print(f"\n✅ 완료 — 총 {time.time() - t0:.0f}s ({(time.time()-t0)/60:.1f}분)")
    print(f"\n결과 위치:")
    print(f"  ml/results/eda/")
    print(f"  ml/results/tier/")
    print(f"  ml/results/baseline/")
    print(f"  ml/results/cv/")
    print(f"  ml/results/shap/")
    print(f"  ml/results/waterfall/")


if __name__ == "__main__":
    main()
