"""
Markdown → PDF 변환 (한국어 비즈니스 문서 톤).

엔진: Python markdown → HTML → Chrome headless print-to-pdf
시스템 폰트(Apple SD Gothic Neo)를 그대로 사용해 한글 안정.

사용:
    python consulting/_md_to_pdf.py consulting/gn_communication/gn_approval_request.md
    → consulting/gn_communication/gn_approval_request.pdf
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS_STYLE = """
@page { size: A4; margin: 22mm 18mm 22mm 18mm; }

* { box-sizing: border-box; }

body {
    font-family: "Apple SD Gothic Neo", "AppleGothic", sans-serif;
    font-size: 10pt;
    line-height: 1.55;
    color: #222;
    max-width: 100%;
}

h1 {
    font-size: 18pt; font-weight: 700; color: #1a1a1a;
    border-bottom: 2px solid #333;
    padding-bottom: 6pt; margin: 0 0 14pt 0;
    page-break-after: avoid;
}
h2 {
    font-size: 14pt; font-weight: 700; color: #1a1a1a;
    border-bottom: 1px solid #999;
    padding-bottom: 4pt; margin: 18pt 0 10pt 0;
    page-break-after: avoid;
}
h3 {
    font-size: 11.5pt; font-weight: 700; color: #2a2a2a;
    margin: 14pt 0 6pt 0;
    page-break-after: avoid;
}
h4 {
    font-size: 10.5pt; font-weight: 700; color: #333;
    margin: 10pt 0 4pt 0;
    page-break-after: avoid;
}

p { margin: 4pt 0; }
ul, ol { margin: 4pt 0; padding-left: 18pt; }
li { margin: 2pt 0; }

strong { font-weight: 700; color: #111; }
em { font-style: italic; }

code {
    font-family: "SF Mono", Menlo, monospace;
    font-size: 9pt;
    background: #f3f3f3;
    padding: 1pt 4pt;
    border-radius: 2pt;
}
pre {
    background: #f7f7f7;
    border: 1px solid #ddd;
    border-radius: 3pt;
    padding: 8pt;
    font-size: 8.5pt;
    line-height: 1.4;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-wrap: break-word;
}
pre code { background: transparent; padding: 0; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #bbb;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}
th { background: #f0f0f0; font-weight: 700; }
tr:nth-child(even) td { background: #fafafa; }

blockquote {
    border-left: 3px solid #888;
    padding: 4pt 10pt;
    margin: 8pt 0;
    background: #f7f7f7;
    color: #444;
    page-break-inside: avoid;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 14pt 0;
}

a { color: #0a58ca; text-decoration: none; }

ul.task-list { list-style: none; padding-left: 0; }
li.task-list-item input[type="checkbox"] { margin-right: 6pt; }
"""


def md_to_html(md_path: Path) -> str:
    md_text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "toc", "nl2br"],
    )
    body = (
        body
        .replace("<li>[ ] ", '<li class="task-list-item"><input type="checkbox" disabled> ')
        .replace("<li>[x] ", '<li class="task-list-item"><input type="checkbox" checked disabled> ')
        .replace("<li>[X] ", '<li class="task-list-item"><input type="checkbox" checked disabled> ')
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{md_path.stem}</title>
<style>{CSS_STYLE}</style>
</head>
<body>
{body}
</body>
</html>
"""


def convert(md_path: Path) -> Path:
    html = md_to_html(md_path)
    pdf_path = md_path.with_suffix(".pdf")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", encoding="utf-8", delete=False, dir=md_path.parent
    ) as tmp:
        tmp.write(html)
        tmp_html = Path(tmp.name)

    try:
        result = subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--virtual-time-budget=2000",
                f"--print-to-pdf={pdf_path}",
                f"file://{tmp_html}",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Chrome 오류:\n{result.stderr}")
    finally:
        tmp_html.unlink(missing_ok=True)

    return pdf_path


def main():
    if len(sys.argv) < 2:
        print("usage: python _md_to_pdf.py <markdown_file> [<markdown_file> ...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        md_path = Path(arg).resolve()
        if not md_path.exists():
            print(f"❌ 없음: {md_path}")
            continue
        pdf_path = convert(md_path)
        size_kb = pdf_path.stat().st_size / 1024
        print(f"✅ {md_path.name}{pdf_path.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
