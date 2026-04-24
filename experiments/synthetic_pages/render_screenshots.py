"""
54개 가상 페이지 스크린샷 + index.html 생성 — 시각 검수용.

산출물:
  experiments/synthetic_pages/screenshots/page_NNN.png
  experiments/synthetic_pages/index.html (54개 링크 + F 수준 표)

사용법:
    python experiments/synthetic_pages/render_screenshots.py

검수 방법:
    open experiments/synthetic_pages/index.html
    (또는 python -m http.server 8000 으로 로컬 서버)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SHOT_DIR = HERE / "screenshots"
SHOT_DIR.mkdir(exist_ok=True)


def main():
    # 설계 매트릭스 로드
    with (HERE / "design_matrix.csv").open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 스크린샷 생성
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 1200})
        for row in rows:
            pid = row["page_id"]
            html_path = HERE / f"{pid}.html"
            page.goto(f"file://{html_path}")
            page.screenshot(path=str(SHOT_DIR / f"{pid}.png"), full_page=True)
        browser.close()
    print(f"✅ 스크린샷 54장 → {SHOT_DIR}")

    # index.html 생성
    idx_rows = []
    for row in rows:
        pid = row["page_id"]
        idx_rows.append(f"""
        <tr>
          <td><a href="{pid}.html" target="_blank">{pid}</a></td>
          <td>{row['F1_html']}</td>
          <td>{row['F2_jsonld']}</td>
          <td>{row['F3_numeric']}</td>
          <td>{row['F4_cert_pos']}</td>
          <td>{row['F5_cert_detail']}</td>
          <td>{row['F6_evidence']}</td>
          <td><a href="screenshots/{pid}.png" target="_blank"><img src="screenshots/{pid}.png" width="160"></a></td>
        </tr>
        """)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>가상 페이지 54개 — 시각 검수 Index</title>
<style>
  body {{ font-family: sans-serif; padding: 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 13px; }}
  th {{ background: #f0f0f0; position: sticky; top: 0; }}
  img {{ border: 1px solid #ddd; }}
  tr:nth-child(even) {{ background: #fafafa; }}
</style>
</head>
<body>
<h1>가상 페이지 54개 시각 검수 Index</h1>
<p>총 {len(rows)}개 페이지 (L27 × 복제 2). 클릭해서 HTML 또는 스크린샷 확대.</p>
<table>
<thead>
<tr><th>Page</th><th>F1 HTML</th><th>F2 JSON-LD</th><th>F3 수치</th><th>F4 인증위치</th><th>F5 인증상세</th><th>F6 근거</th><th>스크린샷</th></tr>
</thead>
<tbody>
{''.join(idx_rows)}
</tbody>
</table>
</body>
</html>
"""
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"✅ index.html → {HERE / 'index.html'}")
    print(f"\n검수하려면:")
    print(f"  open {HERE / 'index.html'}")


if __name__ == "__main__":
    main()
