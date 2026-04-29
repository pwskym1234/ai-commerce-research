"""프롬프트 품질 rubric 스코어러 (v2.1 vs 02 출력 비교용).

4축으로 각 프롬프트를 0/0.5/1 점수화:
- A. persona       : 화자 페르소나 (나이/직업/생애단계) 명시
- B. specifics     : 구체 조건 (예산/기간/시간/장소/상황)
- C. category_anchor: 제품 카테고리 단어 명시
- D. natural       : 자연스러운 한국어 구어체

Claude 한 번에 N개 프롬프트를 JSON으로 채점. 카테고리별 평균 + 합산.

사용:
  python new/tools/score_prompts.py --csv brands/bodydoctor_k/prompts.csv --label v2.1
  python new/tools/score_prompts.py --csv brands/_eval_bodydoctor/prompts.csv --label baseline --compare brands/bodydoctor_k/prompts.csv
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL  # noqa
from anthropic import Anthropic


RUBRIC = """당신은 한국어 프롬프트 품질 심사관이다. 각 프롬프트를 4축으로 0/0.5/1 채점한다.

=== 채점 기준 ===

A. persona (페르소나) — 화자 정체성·생애 단계가 드러나는가?
  1.0 — 나이/직업/생애 단계/관계가 구체적으로 명시 (예: "30대 직장인인데", "40대 산후 5년차", "60대 어머니")
  0.5 — 단순 인구학 시그널만 (예: "초보자가", "여성인데" - 약한 페르소나)
  0.0 — 화자 정체성 단서 없음

B. specifics (구체 조건) — 상황·조건·수치가 명시되는가?
  1.0 — 예산/기간/장소/시간/증상 등 구체적 수치·맥락 (예: "예산 50만원", "1년 썼는데", "층간소음 신경 쓰여", "출근 전 1분")
  0.5 — 약한 조건 (예: "오래 쓸", "조용한") — 시그널은 있지만 구체성 부족
  0.0 — 일반 추천 요청에 그침

C. category_anchor (카테고리 명시) — 제품 카테고리 단어가 들어가는가?
  1.0 — 명확한 카테고리 단어 (예: "골반저근 EMS 케겔 운동기", "구강청결제", "가글", "케겔 의자")
  0.5 — 부분/약한 카테고리어 (예: "기기", "운동기" — 너무 일반적)
  0.0 — 카테고리 단어 없음 (브랜드명만)
  ※ NEUTRAL은 의도적으로 open-ended일 수 있음 — 그래도 카테고리 단어 있으면 1.0

D. natural (자연스러움) — 한국어 구어체로 자연스러운가?
  1.0 — 친구한테 묻듯 자연스러움, 격식체·번역체 없음
  0.5 — 어색한 부분 존재 (예: "있을까?" 너무 정중, 일부 마케팅 문구 잔존)
  0.0 — 격식체/번역체/AI 가짜 톤 ("효과적인 제품을 추천해 주시기 바랍니다")

=== 출력 형식 ===

JSON 배열만 출력 (다른 텍스트 절대 금지):
[
  {{"id": "<prompt_id>", "a": 1.0, "b": 0.5, "c": 0.0, "d": 1.0, "note": "한 문장 코멘트"}},
  ...
]

=== 채점할 프롬프트 ({n}개) ===
{items}
"""


def call_claude(client: Anthropic, prompt: str) -> str:
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return next((b.text for b in resp.content if b.type == "text"), "").strip()


def parse_json(text: str) -> List[Dict]:
    # Strip code fences if present
    t = text.strip()
    if t.startswith("```"):
        t = "\n".join(t.split("\n")[1:])
        if t.endswith("```"):
            t = t.rsplit("```", 1)[0]
    return json.loads(t)


def score_csv(client: Anthropic, csv_path: str, batch_size: int = 30) -> Dict:
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    items_by_id = {r["prompt_id"]: r for r in rows}

    # Batch & call
    all_scores: List[Dict] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start:start + batch_size]
        items_str = "\n".join(
            f'- {r["prompt_id"]} [{r["category_code"]}]: "{r["prompt_text"]}"'
            for r in batch
        )
        prompt = RUBRIC.format(n=len(batch), items=items_str)
        text = call_claude(client, prompt)
        try:
            scores = parse_json(text)
        except json.JSONDecodeError as e:
            print(f"[WARN] batch {start}: JSON parse failed — {e}")
            print(f"  raw: {text[:300]}")
            continue
        all_scores.extend(scores)

    # Aggregate
    by_cat = defaultdict(lambda: {"n": 0, "a": 0, "b": 0, "c": 0, "d": 0})
    detailed = []
    for s in all_scores:
        pid = s.get("id", "")
        row = items_by_id.get(pid)
        if not row:
            continue
        cat = row["category_code"]
        for axis in ["a", "b", "c", "d"]:
            by_cat[cat][axis] += float(s.get(axis, 0) or 0)
        by_cat[cat]["n"] += 1
        detailed.append({
            "id": pid, "cat": cat,
            "text": row["prompt_text"],
            **{k: s.get(k) for k in ["a", "b", "c", "d", "note"]},
        })

    # Compute averages
    summary = {}
    for cat, agg in by_cat.items():
        n = agg["n"] or 1
        summary[cat] = {
            "n": agg["n"],
            "a_avg": round(agg["a"] / n, 3),
            "b_avg": round(agg["b"] / n, 3),
            "c_avg": round(agg["c"] / n, 3),
            "d_avg": round(agg["d"] / n, 3),
            "overall": round((agg["a"] + agg["b"] + agg["c"] + agg["d"]) / (4 * n), 3),
        }

    overall_n = sum(v["n"] for v in summary.values()) or 1
    overall = sum(
        (v["a_avg"] + v["b_avg"] + v["c_avg"] + v["d_avg"]) * v["n"] / 4
        for v in summary.values()
    ) / overall_n

    return {
        "csv_path": csv_path,
        "total_rows": len(rows),
        "scored_rows": len(all_scores),
        "summary_by_category": summary,
        "overall_avg": round(overall, 3),
        "detailed": detailed,
    }


def print_summary(label: str, result: Dict) -> None:
    print(f"\n=== {label} ({result['csv_path']}) ===")
    print(f"  scored {result['scored_rows']}/{result['total_rows']} prompts")
    print(f"  {'cat':<14}{'n':>4}  {'A persona':>10}  {'B specific':>10}  {'C cat-anchor':>12}  {'D natural':>10}  {'overall':>8}")
    for cat in ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"]:
        s = result["summary_by_category"].get(cat)
        if not s:
            continue
        print(f"  {cat:<14}{s['n']:>4}  {s['a_avg']:>10.2f}  {s['b_avg']:>10.2f}  {s['c_avg']:>12.2f}  {s['d_avg']:>10.2f}  {s['overall']:>8.2f}")
    print(f"  {'OVERALL':<14}{result['scored_rows']:>4}  {' ':>43}  {result['overall_avg']:>8.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV path")
    ap.add_argument("--label", default="prompts", help="라벨 (출력용)")
    ap.add_argument("--compare", help="비교용 두 번째 CSV 경로")
    ap.add_argument("--save", help="상세 결과 JSON 저장 경로")
    args = ap.parse_args()

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    r1 = score_csv(client, args.csv)
    print_summary(args.label, r1)

    r2 = None
    if args.compare:
        r2 = score_csv(client, args.compare)
        print_summary("compare", r2)

        # Side-by-side delta
        print(f"\n=== DELTA ({args.label} vs compare) ===")
        print(f"  {'cat':<14}{'A':>8}{'B':>8}{'C':>8}{'D':>8}{'Δ overall':>11}")
        for cat in ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"]:
            s1 = r1["summary_by_category"].get(cat)
            s2 = r2["summary_by_category"].get(cat)
            if not s1 or not s2:
                continue
            print(
                f"  {cat:<14}"
                f"{s1['a_avg']-s2['a_avg']:>+8.2f}"
                f"{s1['b_avg']-s2['b_avg']:>+8.2f}"
                f"{s1['c_avg']-s2['c_avg']:>+8.2f}"
                f"{s1['d_avg']-s2['d_avg']:>+8.2f}"
                f"{s1['overall']-s2['overall']:>+11.2f}"
            )

    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump({"label": args.label, "result": r1, "compare": r2}, f, ensure_ascii=False, indent=2)
        print(f"\n저장 → {args.save}")


if __name__ == "__main__":
    main()
