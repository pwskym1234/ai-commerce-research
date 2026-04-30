"""
run 디렉토리 후처리 — responses.jsonl 한 개에서 3개 산출물 생성.

산출물:
- responses.csv     : 스프레드시트(구글시트/엑셀) import용. raw_response는 200자 truncate.
                      전체 본문은 jsonl의 response_id로 역참조.
- SUMMARY.md        : 사람·Claude 가독용. Y 변수 분포, 캐시 히트, 토큰/비용.
- ANOMALIES.md      : 자동 검수. 짧은 응답·회피만·사전정의 외 브랜드만·중복응답 등.

단독 실행도 가능:
    python experiments/_postprocess.py experiments/api_runs/<run_id>/
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev


# ── 자동 검수 임계값 ──
MIN_RESPONSE_LENGTH = 100        # 이보다 짧으면 의심
TRUNCATE_RAW_FOR_CSV = 200       # CSV의 raw_response 컬럼은 200자만
SAFETY_AVOID_PATTERNS = [
    "전문가와 상담", "의사와 상담", "의료진 상담",
    "병원 방문", "진료를 받으",
]


# ── jsonl 로드 ──
def load_responses(jsonl_path: Path) -> list[dict]:
    out = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"⚠️ JSONL 파싱 실패 (라인 스킵): {e}")
    return out


# ── 1. CSV 변환 ──
CSV_COLUMNS = [
    # 식별/메타
    "response_id", "run_id", "page_id", "query_id", "query_type",
    "query_text", "repeat_idx", "seed", "model_version", "persona_id",
    # 응답
    "response_length", "raw_response_excerpt",
    # Y 변수
    "y2a_mention", "y2a_our_selected", "y2a_positive",
    "y2a_alternative", "y2a_no_show", "y2a_wintieloss", "y2a_singleselect",
    "y4_safety_avoidance",
    # 사전 정의 + 외부 브랜드
    "y2a_mentioned_brand_ids_joined",
    "other_brands_detected_joined",
    # 비용/시간
    "tokens_in", "tokens_out", "cost_usd", "from_cache", "timestamp",
]


def write_csv(rows: list[dict], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in rows:
            raw = (r.get("raw_response") or "").replace("\n", " ").replace("\r", " ")
            excerpt = raw[:TRUNCATE_RAW_FOR_CSV]
            if len(raw) > TRUNCATE_RAW_FOR_CSV:
                excerpt += "…"
            writer.writerow({
                "response_id": r.get("response_id", ""),
                "run_id": r.get("run_id", ""),
                "page_id": r.get("page_id", ""),
                "query_id": r.get("query_id", ""),
                "query_type": r.get("query_type", ""),
                "query_text": r.get("query_text", ""),
                "repeat_idx": r.get("repeat_idx", ""),
                "seed": r.get("seed", ""),
                "model_version": r.get("model_version", ""),
                "persona_id": r.get("persona_id", ""),
                "response_length": r.get("response_length", len(raw)),
                "raw_response_excerpt": excerpt,
                "y2a_mention": r.get("y2a_mention", ""),
                "y2a_our_selected": r.get("y2a_our_selected", ""),
                "y2a_positive": r.get("y2a_positive", "") or "",
                "y2a_alternative": r.get("y2a_alternative", "") if r.get("y2a_alternative") is not None else "",
                "y2a_no_show": r.get("y2a_no_show", "") if r.get("y2a_no_show") is not None else "",
                "y2a_wintieloss": r.get("y2a_wintieloss", "") or "",
                "y2a_singleselect": r.get("y2a_singleselect", "") if r.get("y2a_singleselect") is not None else "",
                "y4_safety_avoidance": r.get("y4_safety_avoidance", ""),
                "y2a_mentioned_brand_ids_joined": "|".join(r.get("y2a_mentioned_brand_ids", [])),
                "other_brands_detected_joined": "|".join(r.get("other_brands_detected", [])),
                "tokens_in": r.get("tokens_in", 0),
                "tokens_out": r.get("tokens_out", 0),
                "cost_usd": round(r.get("cost_usd", 0.0), 6),
                "from_cache": r.get("from_cache", False),
                "timestamp": r.get("timestamp", ""),
            })


# ── 2. SUMMARY.md ──
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """이항 비율 Wilson 95% CI (R7 룰)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def write_summary(rows: list[dict], out_path: Path) -> None:
    n = len(rows)
    if n == 0:
        out_path.write_text("# Run Summary\n\n_빈 run (응답 0건)_\n", encoding="utf-8")
        return

    run_id = rows[0].get("run_id", "?")
    model = rows[0].get("model_version", "?")

    cache_hits = sum(1 for r in rows if r.get("from_cache"))
    total_cost = sum(r.get("cost_usd", 0) for r in rows)
    total_in = sum(r.get("tokens_in", 0) for r in rows)
    total_out = sum(r.get("tokens_out", 0) for r in rows)

    # Y2a 우리 언급률
    our_k = sum(1 for r in rows if r.get("y2a_our_selected"))
    our_lo, our_hi = wilson_ci(our_k, n)

    # Y4 회피율
    y4_k = sum(1 for r in rows if r.get("y4_safety_avoidance"))
    y4_lo, y4_hi = wilson_ci(y4_k, n)

    # 쿼리 유형별 우리 언급률
    by_qtype = defaultdict(lambda: {"k": 0, "n": 0})
    for r in rows:
        qt = r.get("query_type", "?")
        by_qtype[qt]["n"] += 1
        if r.get("y2a_our_selected"):
            by_qtype[qt]["k"] += 1

    # 응답 길이 분포
    lengths = [r.get("response_length", 0) for r in rows]
    len_mean = mean(lengths) if lengths else 0
    len_min = min(lengths) if lengths else 0
    len_max = max(lengths) if lengths else 0

    # 사전 정의 외 브랜드 빈도
    other_counter = Counter()
    for r in rows:
        for b in r.get("other_brands_detected", []) or []:
            other_counter[b] += 1

    # CMP win/tie/loss 분포
    wtl = Counter()
    for r in rows:
        v = r.get("y2a_wintieloss")
        if v:
            wtl[v] += 1

    # 작성
    lines = []
    lines.append(f"# Run Summary: `{run_id}`\n")
    lines.append(f"- 모델: **{model}**")
    lines.append(f"- 총 응답: **{n:,}** 건 (캐시 히트 {cache_hits} = {cache_hits/n*100:.1f}%)")
    lines.append(f"- 총 토큰: input {total_in:,} / output {total_out:,}")
    lines.append(f"- 총 비용: **${total_cost:.4f}**")
    lines.append(f"- 응답 길이: mean={len_mean:.0f} 자, [{len_min}~{len_max}]")
    lines.append("")

    lines.append("## 핵심 Y 변수")
    lines.append(f"- **Y2a 우리(바디닥터) 언급률**: {our_k}/{n} = **{our_k/n*100:.1f}%** (Wilson 95% CI [{our_lo*100:.1f}%, {our_hi*100:.1f}%])")
    lines.append(f"- **Y4 안전성 회피율**: {y4_k}/{n} = **{y4_k/n*100:.1f}%** (CI [{y4_lo*100:.1f}%, {y4_hi*100:.1f}%])")
    lines.append("")

    lines.append("## 쿼리 유형별 우리 언급률")
    lines.append("| 유형 | n | k | 비율 | 95% CI |")
    lines.append("|------|---|---|------|--------|")
    for qt, d in sorted(by_qtype.items()):
        lo, hi = wilson_ci(d["k"], d["n"])
        lines.append(f"| {qt} | {d['n']} | {d['k']} | {d['k']/d['n']*100:.1f}% | [{lo*100:.1f}%, {hi*100:.1f}%] |")
    lines.append("")

    if wtl:
        lines.append("## CMP 쿼리 win/tie/loss 분포")
        for k, v in wtl.most_common():
            lines.append(f"- {k}: {v}")
        lines.append("")

    if other_counter:
        lines.append("## 사전 정의 외 등장 브랜드 (NER 발굴, 상위 15)")
        for b, c in other_counter.most_common(15):
            lines.append(f"- {b}: {c}")
        lines.append("")

    lines.append("---")
    lines.append("_상세는 `responses.jsonl` (raw) / `responses.csv` (스프레드시트) / `ANOMALIES.md` (자동 검수) 참조._")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ── 3. ANOMALIES.md ──
def detect_anomalies(rows: list[dict]) -> dict[str, list[dict]]:
    """자동 플래그. 각 그룹마다 의심 응답 목록."""
    groups = defaultdict(list)

    # 응답 짧음
    for r in rows:
        if r.get("response_length", 0) < MIN_RESPONSE_LENGTH:
            groups["short_response"].append(r)

    # 사전 정의 브랜드 0개 + 응답 충분히 길음 (= 사전 정의 외 답변만)
    for r in rows:
        if (
            r.get("response_length", 0) >= MIN_RESPONSE_LENGTH
            and len(r.get("y2a_mentioned_brand_ids", []) or []) == 0
        ):
            groups["no_predefined_brand"].append(r)

    # 회피만 + 사전 정의 0개
    for r in rows:
        if r.get("y4_safety_avoidance") and len(r.get("y2a_mentioned_brand_ids", []) or []) == 0:
            groups["only_safety_avoidance"].append(r)

    # 같은 (page, query, repeat_idx, seed)인데 응답이 다른 경우 (캐시 깨짐 의심)
    seen = {}
    for r in rows:
        key = (r.get("page_id"), r.get("query_id"), r.get("repeat_idx"), r.get("seed"))
        if key in seen and seen[key] != r.get("raw_response"):
            groups["seed_collision"].append(r)
        else:
            seen[key] = r.get("raw_response")

    return groups


def write_anomalies(rows: list[dict], out_path: Path) -> None:
    groups = detect_anomalies(rows)

    lines = ["# 자동 검수 (Anomalies)\n"]
    lines.append(f"총 응답: {len(rows):,}")
    lines.append("")

    if not any(groups.values()):
        lines.append("✅ 의심 사례 없음 (모든 자동 플래그 통과).")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return

    flag_titles = {
        "short_response": f"⚠️ 응답이 {MIN_RESPONSE_LENGTH}자 미만 — 회피·에러 의심",
        "no_predefined_brand": "⚠️ 사전 정의 브랜드 0개 등장 — 응답이 무관한 답변일 수 있음",
        "only_safety_avoidance": "⚠️ 안전성 회피만 + 추천 0개",
        "seed_collision": "🔴 같은 seed에서 다른 응답 — 캐시·시드 무효화 의심",
    }

    for flag, items in groups.items():
        if not items:
            continue
        lines.append(f"## {flag_titles.get(flag, flag)} ({len(items)}건)\n")
        for r in items[:10]:  # 그룹당 최대 10개 샘플
            raw = (r.get("raw_response") or "")[:200].replace("\n", " ")
            lines.append(
                f"- `{r.get('response_id','?')[:8]}` "
                f"[{r.get('query_id')} / {r.get('page_id')} / rep={r.get('repeat_idx')} / "
                f"seed={r.get('seed')}] len={r.get('response_length')}자"
            )
            lines.append(f"  > {raw}{'…' if r.get('response_length',0) > 200 else ''}")
        if len(items) > 10:
            lines.append(f"  _...외 {len(items)-10}건. 전체는 `responses.jsonl`에서 검색._")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ── 메인 ──
def postprocess_run(run_dir: Path) -> None:
    run_dir = Path(run_dir)
    jsonl_path = run_dir / "responses.jsonl"
    if not jsonl_path.exists():
        raise FileNotFoundError(f"{jsonl_path} 없음 — runner가 안 돌았거나 경로 이상")

    rows = load_responses(jsonl_path)

    write_csv(rows, run_dir / "responses.csv")
    write_summary(rows, run_dir / "SUMMARY.md")
    write_anomalies(rows, run_dir / "ANOMALIES.md")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python _postprocess.py <run_dir>")
        sys.exit(1)
    postprocess_run(Path(sys.argv[1]))
    print(f"✅ 후처리 완료: {sys.argv[1]}")
