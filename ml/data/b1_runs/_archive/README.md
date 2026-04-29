# `_archive/` — 구버전 / pilot / 부분 실행 b1 run

`list_b1_runs()` (ml/scripts/_data_loader.py) 는 부모 폴더의 `b1_*` glob 만 매칭하므로, 본 `_archive/` 안의 run은 자동 탐지에서 제외됩니다.

활성 run (부모 폴더):
- `b1_open_medical_device_20260425_110019` — 본실험 1차 open
- `b1_closed_medical_device_20260425_205723` — 재실행 closed (페이지 13개)
- `b1_open_gargle_20260425_110221` — 본실험 1차 open
- `b1_closed_gargle_20260425_205908` — 재실행 closed (페이지 10개)
- `brd_per_brand_20260425_145754` — BRD per-brand (25 브랜드)
