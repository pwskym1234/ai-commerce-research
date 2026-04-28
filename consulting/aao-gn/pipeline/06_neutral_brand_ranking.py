"""
NEUTRAL 응답에서 모든 브랜드 언급 집계 & 랭킹.

1. raw_responses.json에서 NEUTRAL 카테고리 응답 텍스트 수집
2. bold/heading 패턴으로 브랜드 후보 추출
3. Claude에 한 번 요청 → 실제 브랜드/제품명만 정제, 동일 브랜드 통합
4. 정제된 브랜드 리스트 + config 브랜드를 응답 전체에서 재스캔
5. 브랜드별 등장 응답 수 → % → 순위
6. <brand>/results/dashboard/neutral_brand_ranking.json 저장

출력 구조:
{
  "total_responses": 150,
  "our_brand_name": "프로폴린스",
  "our_brand_rank": 8,
  "our_brand_share": 0.0,
  "rows": [
    {"rank": 1, "brand": "리스테린", "hit_count": 41, "share": 27.33, "is_ours": false, "is_known_competitor": true},
    ...
  ]
}
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from anthropic import Anthropic


BOLD_PAT = re.compile(r"\*\*([^*\n]{1,50})\*\*")
HEAD_PAT = re.compile(r"^#+\s+([^\n#]+)$", re.M)

EXTRACTION_PROMPT = """당신은 한국어 커머스 응답 분석가입니다.
아래는 한 제품 카테고리의 AI 답변에서 반복적으로 등장한 bold/헤딩 문구 후보들입니다.
이 중 **실제 브랜드 또는 상표(제품 라인업명)** 만 골라내고, 같은 브랜드의 다양한 표기는
**하나의 대표 한국어 이름**으로 통합해 주세요.

제품 카테고리: {category}
후보 (빈도 내림차순):
{candidates}

[브랜드 vs 일반 제품군 — 매우 중요]

✓ 브랜드인 것 (포함):
- 고유명사 회사·제품명: "리스테린", "가그린", "케어플란트", "Listerine"
- 영문 회사명·로고가 있는 것: "Philips", "P&G"
- 특정 제조사가 출시한 라인업명: "리스테린 토탈케어", "오랄비 PRO"

✗ 브랜드가 아닌 것 (반드시 제외):
- 일반 제품군·기기 종류: "케겔 트레이너", "바이오피드백 기기", "저항밴드",
  "골반저근 운동기", "전기자극 기기", "EMS 기기", "혀클리너", "치실"
- 성분·재료명: "알코올", "불소", "프로폴리스"
- 사용법·기능 설명: "혀 클리너 사용", "양치 후 헹굼"
- 신체 부위·증상명: "골반저근", "잇몸", "구취"
- 운동·시술 카테고리: "케겔 운동", "스케일링"
- 형용 수식어 단독: "프리미엄", "휴대용", "입문용"

[판정 기준]
- 한국어 또는 외래어 **고유명사**여야 함 (회사명/상표명).
- 일반 명사구가 "OO 트레이너", "OO 기기", "OO 밴드"처럼 끝나면 100% 브랜드 아님.
- 확신 50% 미만이면 **반드시 빼기** — 빠뜨리는 게 잘못 포함하는 것보다 낫다.

출력 규칙:
- JSON 배열만 출력. 다른 설명 금지.
- 각 요소 구조: {{"canonical": "대표명", "aliases": ["표기1", "표기2", ...]}}
- 라인업/버전명은 상위 브랜드로 통합 (예: "리스테린 토탈케어" → canonical "리스테린").
- 영문 표기(예: "Listerine")가 있으면 aliases에 포함.
- 최대 20개. 후보 중 진짜 브랜드가 0개면 빈 배열 [] 반환.

JSON:"""


def load_brand_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_raw_responses(brand_dir: str) -> List[Dict]:
    path = os.path.join(brand_dir, "results", "raw_responses.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_candidates(neutral_responses: List[Dict], top_n: int = 80) -> List[str]:
    tokens = []
    for r in neutral_responses:
        text = r.get("response") or ""
        tokens.extend(BOLD_PAT.findall(text))
        tokens.extend(h.strip() for h in HEAD_PAT.findall(text))
    counter = Counter(t.strip() for t in tokens if t.strip())
    return [t for t, _ in counter.most_common(top_n)]


def call_claude_filter(client: Anthropic, category: str, candidates: List[str]) -> List[Dict]:
    cand_lines = "\n".join(f"- {c}" for c in candidates)
    prompt = EXTRACTION_PROMPT.format(category=category, candidates=cand_lines)
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = next((b.text for b in resp.content if b.type == "text"), "").strip()
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        print("경고: Claude 응답에서 JSON 배열을 찾지 못함")
        print("원본:", text[:500])
        return []
    try:
        parsed = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {e}")
        return []
    out = []
    for item in parsed:
        canon = (item.get("canonical") or "").strip()
        aliases = [a.strip() for a in (item.get("aliases") or []) if a and a.strip()]
        if not canon:
            continue
        if canon not in aliases:
            aliases.insert(0, canon)
        out.append({"canonical": canon, "aliases": aliases})
    return out


def _low(s: str) -> str:
    return (s or "").lower()


def count_brand_hits(
    responses: List[Dict],
    brand_entries: List[Dict],
) -> Dict[str, int]:
    counts: Dict[str, int] = {e["canonical"]: 0 for e in brand_entries}
    for r in responses:
        text_low = _low(r.get("response"))
        if not text_low:
            continue
        for e in brand_entries:
            if any(_low(a) in text_low for a in e["aliases"]):
                counts[e["canonical"]] += 1
    return counts


def strict_our_aliases(brand: Dict) -> List[str]:
    name = (brand.get("brand_name") or "").strip()
    raw = list(brand.get("brand_keywords") or [])
    if brand.get("brand_name"):
        raw.insert(0, brand["brand_name"])
    if brand.get("brand_name_en"):
        raw.insert(1, brand["brand_name_en"])
    out = []
    seen = set()
    for v in raw:
        v = (v or "").strip()
        if not v or v.lower() in seen:
            continue
        seen.add(v.lower())
        out.append(v)
    # 바디닥터K: 'K' 없는 '바디닥터' 토큰 제거 (false positive 방지)
    if name.replace(" ", "").lower() == "바디닥터k":
        out = [v for v in out if v.strip() != "바디닥터"]
    return out


def build_brand_entries(brand: Dict, claude_extracted: List[Dict]) -> List[Dict]:
    """우리 브랜드 + 경쟁사 + Claude 추출 브랜드를 통합."""
    our_canonical = brand.get("brand_name", "")
    our_aliases = strict_our_aliases(brand)

    entries: List[Dict] = []
    entries.append({
        "canonical": our_canonical,
        "aliases": our_aliases,
        "is_ours": True,
        "is_known_competitor": False,
    })

    known_competitor_canonicals: Set[str] = set()
    for comp in brand.get("competitors") or []:
        cname = (comp.get("name") or "").strip()
        if not cname:
            continue
        aliases = [cname] + [k for k in (comp.get("keywords") or []) if k]
        aliases = list(dict.fromkeys(a.strip() for a in aliases if a and a.strip()))
        entries.append({
            "canonical": cname,
            "aliases": aliases,
            "is_ours": False,
            "is_known_competitor": True,
        })
        known_competitor_canonicals.add(_low(cname))

    # Claude 추출 브랜드 병합: 우리 + 경쟁사 canonical과 겹치면 alias만 보강하고 스킵
    lookup = {_low(e["canonical"]): e for e in entries}
    for extra in claude_extracted:
        canon = extra["canonical"]
        low = _low(canon)
        if low in lookup:
            # 기존 엔트리에 alias 추가
            existing = lookup[low]
            for a in extra["aliases"]:
                if a not in existing["aliases"]:
                    existing["aliases"].append(a)
            continue
        # 새 브랜드 후보: 경쟁사 이름 중 일부 포함이면 경쟁사로 병합
        matched_competitor = None
        for e in entries:
            if not e.get("is_known_competitor"):
                continue
            # e.canonical 또는 aliases 중 일부가 extra 이름에 들어있으면 병합
            if any(_low(a) in low or low in _low(a) for a in e["aliases"]):
                matched_competitor = e
                break
        if matched_competitor:
            for a in extra["aliases"]:
                if a not in matched_competitor["aliases"]:
                    matched_competitor["aliases"].append(a)
            continue
        entries.append({
            "canonical": canon,
            "aliases": extra["aliases"],
            "is_ours": False,
            "is_known_competitor": False,
        })
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--top-candidates", type=int, default=80)
    args = ap.parse_args()

    brand = load_brand_config(args.brand)
    brand_dir = os.path.dirname(args.brand)
    print(f"[{brand['brand_name']}] NEUTRAL 브랜드 랭킹 집계 시작")

    responses = load_raw_responses(brand_dir)
    neutral = [r for r in responses if r.get("category_code") == "NEUTRAL"]
    # 중복 응답 제거 대신, prompt_id 기준 응답 수(runs 포함)를 기준으로
    total_runs = len(neutral)
    distinct_prompts = len({r["prompt_id"] for r in neutral})
    print(f"  NEUTRAL: {distinct_prompts} prompts × runs = {total_runs}건")

    candidates = extract_candidates(neutral, top_n=args.top_candidates)
    print(f"  bold/heading 후보: {len(candidates)}개")

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    extracted = call_claude_filter(
        client,
        brand.get("product_category", "구매 카테고리"),
        candidates,
    )
    print(f"  Claude 정제 후 브랜드: {len(extracted)}개")

    entries = build_brand_entries(brand, extracted)
    counts = count_brand_hits(neutral, entries)

    # 순위 계산 — 기준: "distinct prompt에서 등장한 건수" 또는 "총 응답 건수". 후자로 간다.
    rows: List[Dict] = []
    for e in entries:
        hit = counts[e["canonical"]]
        rows.append({
            "brand": e["canonical"],
            "hit_count": hit,
            "share": round(hit / total_runs * 100, 2) if total_runs else 0.0,
            "aliases": e["aliases"],
            "is_ours": bool(e.get("is_ours")),
            "is_known_competitor": bool(e.get("is_known_competitor")),
        })

    # 등장한 브랜드만 남김 (hit_count=0는 제외하되 우리 브랜드는 항상 포함)
    visible = [r for r in rows if r["hit_count"] > 0 or r["is_ours"]]
    visible.sort(key=lambda r: (-r["hit_count"], r["brand"]))

    # 순위 부여 (동점 처리: 표준 "경합 없음" 방식 — 같은 hit_count면 같은 순위)
    rank = 0
    last_hit = None
    for i, r in enumerate(visible):
        if r["hit_count"] != last_hit:
            rank = i + 1
            last_hit = r["hit_count"]
        r["rank"] = rank

    our_row = next((r for r in visible if r["is_ours"]), None)
    our_rank = our_row["rank"] if our_row else None
    our_share = our_row["share"] if our_row else 0.0

    out = {
        "brand_name": brand.get("brand_name", ""),
        "total_runs": total_runs,
        "distinct_prompts": distinct_prompts,
        "our_brand_rank": our_rank,
        "our_brand_share": our_share,
        "our_brand_hit_count": our_row["hit_count"] if our_row else 0,
        "total_brands_detected": len(visible),
        "rows": visible,
    }

    out_path = os.path.join(brand_dir, "results", "dashboard", "neutral_brand_ranking.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n  === 결과 ({brand['brand_name']}) ===")
    print(f"  우리 브랜드 등장 {our_row['hit_count'] if our_row else 0}/{total_runs}건, share {our_share}%, 순위 {our_rank or '순외'}")
    print(f"  상위 10개:")
    for r in visible[:10]:
        mark = "◉ 우리" if r["is_ours"] else ("▲ 경쟁사" if r["is_known_competitor"] else "  기타")
        print(f"    {r['rank']:>3}. {r['brand']:25} {r['hit_count']:>3}건 ({r['share']:>5.2f}%) {mark}")
    print(f"  saved: {out_path}")


if __name__ == "__main__":
    main()
