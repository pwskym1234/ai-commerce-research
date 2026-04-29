# `_legacy/` — 일회성 / 구버전 크롤 스크립트

각각 1회성 크롤 배치 또는 시도 단계 코드. 결과 데이터(`data/raw/`, `data/processed/`)는 활용 중이지만 코드 자체는 재실행 안 함.

활성 크롤 코드는 부모 폴더의 다음만 사용:
- `_base.py`, `_playwright_base.py` — 공통 모듈
- `extract_features.py`, `sixthshop_score.py` — 후처리
- `collect_external_evidence.py`, `collect_query_pool.py` — NAVER API
- `mfds_medical_device_api.py` — 식약처 API
- `scrape_elvie.py`, `scrape_phase_a_plus.py`, `scrape_gargle_extra.py`, `scrape_bodydoctor_k_and_drk.py`, `scrape_stopyo_coupang.py` — 신규 크롤 (2026-04-24~26)
