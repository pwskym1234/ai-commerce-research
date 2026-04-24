"""
Jinja2 템플릿 + design_matrix.csv → 54개 HTML 생성.

사용법:
    python experiments/synthetic_pages/render_pages.py
    → experiments/synthetic_pages/page_001.html ~ page_054.html
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]


def main():
    # 설계 매트릭스 로드
    matrix_path = HERE / "design_matrix.csv"
    with matrix_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 제품 정보 로드
    product_path = HERE / "_product.json"
    with product_path.open("r", encoding="utf-8") as f:
        product = json.load(f)

    # Jinja2 환경
    env = Environment(
        loader=FileSystemLoader(HERE),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
    )
    template = env.get_template("_template.html.j2")

    rendered_count = 0
    for row in rows:
        context = {
            "page_id": row["page_id"],
            "f1_html": row["F1_html"],
            "f2_jsonld": row["F2_jsonld"],
            "f3_numeric": row["F3_numeric"],
            "f4_cert_pos": row["F4_cert_pos"],
            "f5_cert_detail": row["F5_cert_detail"],
            "f6_evidence": row["F6_evidence"],
            "product": product,
        }
        html = template.render(**context)
        out_path = HERE / f"{row['page_id']}.html"
        out_path.write_text(html, encoding="utf-8")
        rendered_count += 1

    print(f"✅ {rendered_count}개 HTML 생성 → {HERE}/page_*.html")

    # 샘플 확인
    sample_path = HERE / "page_001.html"
    if sample_path.exists():
        content = sample_path.read_text(encoding="utf-8")
        print(f"\n=== page_001.html 샘플 (앞 30줄) ===")
        for line in content.splitlines()[:30]:
            print(f"  {line}")


if __name__ == "__main__":
    main()
