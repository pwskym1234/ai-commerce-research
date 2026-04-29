# `_legacy/` — 구버전 스크립트

다음은 신규 모듈로 대체된 구버전 코드입니다. 참조용으로만 보관 — **새 작업에는 사용하지 마세요**.

| 구버전 | 신규 (사용 중) |
|------|----------|
| `eda.py` | `../eda_analysis.py` |
| `baseline_logistic.py` | `../baseline_models.py` (LR/DT/KNN 통합) |
| `shap_analysis.py` | `../shap_pipeline.py` (XGBoost + SHAP + dependence) |
| `run_observational_queries.py` | `../run_b1_async.py` (비동기 + budget + 두 모드) |
