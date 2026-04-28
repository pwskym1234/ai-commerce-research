
"""
GEO 대시보드 집계 스크립트 (초보자 친화형)

핵심 원칙:
- 전체 언급률보다 카테고리별 핵심 지표를 먼저 보여줌
- NEUTRAL: 언급률
- BRAND_ONLY: 긍정/중립/부정 비율
- COMP_ONLY: 대안 소환율 및 평균 추천 순위
- H2H: 승/무/패 비율

입력:
  - brands/<brand>/results/parsed_results.csv

출력:
  - brands/<brand>/results/dashboard/category_cards.csv
  - brands/<brand>/results/dashboard/by_prompt_type.csv
  - brands/<brand>/results/dashboard/h2h_by_competitor.csv
  - brands/<brand>/results/dashboard/comp_only_by_competitor.csv
  - brands/<brand>/results/dashboard/by_prompt.csv
  - brands/<brand>/results/dashboard/summary.json
"""

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Optional


TRUTHY = {"Y", "YES", "TRUE", "1", 1, True}
FALSY = {"N", "NO", "FALSE", "0", 0, False}
INT_FIELDS = {"run_number", "our_brand_rank", "target_competitor_rank"}

CATEGORY_LABELS = {
    "NEUTRAL": "중립",
    "BRAND_ONLY": "브랜드 지명",
    "COMP_ONLY": "경쟁사 대안",
    "H2H": "직접 비교",
}


def load_brand_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def yn_to_bool(value) -> bool:
    if value in TRUTHY:
        return True
    if value in FALSY or value is None:
        return False
    if isinstance(value, str):
        return value.strip().upper() in TRUTHY
    return bool(value)


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def clean_row(row: Dict[str, str]) -> Dict:
    out = dict(row)
    for key in INT_FIELDS:
        raw = (out.get(key) or "").strip()
        if raw == "":
            out[key] = None
        else:
            try:
                out[key] = int(float(raw))
            except ValueError:
                out[key] = None
    return out


def load_parsed_results(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return [clean_row(r) for r in csv.DictReader(f)]


def write_csv(path: str, rows: List[Dict], fieldnames: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def category_rows(rows: List[Dict], category_code: str) -> List[Dict]:
    return [r for r in rows if (r.get("category_code") or "").strip() == category_code]


def is_effective(r: Dict) -> bool:
    """clarification_request, off_topic이 아닌 '유효 응답'."""
    return not yn_to_bool(r.get("clarification_request")) and not yn_to_bool(r.get("off_topic"))


def build_category_cards(rows: List[Dict]) -> List[Dict]:
    cards: List[Dict] = []

    neutral = category_rows(rows, "NEUTRAL")
    if neutral:
        mention_count = sum(1 for r in neutral if yn_to_bool(r.get("mention_brand")))
        reco_count = sum(1 for r in neutral if yn_to_bool(r.get("our_brand_recommended")))
        clar_count = sum(1 for r in neutral if yn_to_bool(r.get("clarification_request")))
        off_count = sum(1 for r in neutral if yn_to_bool(r.get("off_topic")))
        eff_rows = [r for r in neutral if is_effective(r)]
        eff_denom = len(eff_rows)
        eff_mention = sum(1 for r in eff_rows if yn_to_bool(r.get("mention_brand")))
        eff_reco = sum(1 for r in eff_rows if yn_to_bool(r.get("our_brand_recommended")))
        cards.append({
            "category_code": "NEUTRAL",
            "category": CATEGORY_LABELS["NEUTRAL"],
            "total_rows": len(neutral),
            "primary_metric_label": "언급률",
            "primary_metric_value": pct(mention_count, len(neutral)),
            "primary_metric_count": mention_count,
            "primary_metric_denom": len(neutral),
            "secondary_metric_label": "추천률",
            "secondary_metric_value": pct(reco_count, len(neutral)),
            "secondary_metric_count": reco_count,
            "secondary_metric_denom": len(neutral),
            "clarification_count": clar_count,
            "off_topic_count": off_count,
            "effective_denom": eff_denom,
            "effective_primary_count": eff_mention,
            "effective_primary_value": pct(eff_mention, eff_denom),
            "effective_secondary_count": eff_reco,
            "effective_secondary_value": pct(eff_reco, eff_denom),
            "explain": "브랜드를 모르는 상태의 질문에서 우리 브랜드가 자연스럽게 떠오르는지",
        })

    brand_only = category_rows(rows, "BRAND_ONLY")
    if brand_only:
        mentioned = [r for r in brand_only if yn_to_bool(r.get("mention_brand"))]
        total_mentioned = len(mentioned)
        pos = sum(1 for r in mentioned if (r.get("sentiment_to_brand") or "") == "positive")
        neu = sum(1 for r in mentioned if (r.get("sentiment_to_brand") or "") == "neutral")
        neg = sum(1 for r in mentioned if (r.get("sentiment_to_brand") or "") == "negative")
        clar_count = sum(1 for r in brand_only if yn_to_bool(r.get("clarification_request")))
        off_count = sum(1 for r in brand_only if yn_to_bool(r.get("off_topic")))
        eff_rows = [r for r in mentioned if is_effective(r)]
        eff_denom = len(eff_rows)
        eff_pos = sum(1 for r in eff_rows if (r.get("sentiment_to_brand") or "") == "positive")
        eff_neg = sum(1 for r in eff_rows if (r.get("sentiment_to_brand") or "") == "negative")
        cards.append({
            "category_code": "BRAND_ONLY",
            "category": CATEGORY_LABELS["BRAND_ONLY"],
            "total_rows": len(brand_only),
            "primary_metric_label": "긍정 비율",
            "primary_metric_value": pct(pos, total_mentioned),
            "primary_metric_count": pos,
            "primary_metric_denom": total_mentioned,
            "secondary_metric_label": "부정 비율",
            "secondary_metric_value": pct(neg, total_mentioned),
            "secondary_metric_count": neg,
            "secondary_metric_denom": total_mentioned,
            "extra_metric_label": "중립 비율",
            "extra_metric_value": pct(neu, total_mentioned),
            "clarification_count": clar_count,
            "off_topic_count": off_count,
            "effective_denom": eff_denom,
            "effective_primary_count": eff_pos,
            "effective_primary_value": pct(eff_pos, eff_denom),
            "effective_secondary_count": eff_neg,
            "effective_secondary_value": pct(eff_neg, eff_denom),
            "explain": "브랜드명을 직접 넣어 물었을 때 AI가 우리 브랜드를 어떤 톤으로 말하는지",
        })

    comp_only = category_rows(rows, "COMP_ONLY")
    if comp_only:
        surfaced = sum(1 for r in comp_only if (r.get("surfacing_outcome") or "") == "surfaced")
        co_mentioned = sum(1 for r in comp_only if (r.get("surfacing_outcome") or "") == "co_mentioned")
        not_surfaced = sum(1 for r in comp_only if (r.get("surfacing_outcome") or "") == "not_surfaced")
        ranked_our = [r["our_brand_rank"] for r in comp_only if isinstance(r.get("our_brand_rank"), int)]
        ranked_target = [r["target_competitor_rank"] for r in comp_only if isinstance(r.get("target_competitor_rank"), int)]
        clar_count = sum(1 for r in comp_only if yn_to_bool(r.get("clarification_request")))
        off_count = sum(1 for r in comp_only if yn_to_bool(r.get("off_topic")))
        eff_rows = [r for r in comp_only if is_effective(r)]
        eff_denom = len(eff_rows)
        eff_surfaced = sum(1 for r in eff_rows if (r.get("surfacing_outcome") or "") == "surfaced")
        eff_co_mentioned = sum(1 for r in eff_rows if (r.get("surfacing_outcome") or "") == "co_mentioned")
        cards.append({
            "category_code": "COMP_ONLY",
            "category": CATEGORY_LABELS["COMP_ONLY"],
            "total_rows": len(comp_only),
            "primary_metric_label": "대안 소환율",
            "primary_metric_value": pct(surfaced, len(comp_only)),
            "primary_metric_count": surfaced,
            "primary_metric_denom": len(comp_only),
            "secondary_metric_label": "공동 언급률",
            "secondary_metric_value": pct(co_mentioned, len(comp_only)),
            "secondary_metric_count": co_mentioned,
            "secondary_metric_denom": len(comp_only),
            "extra_metric_label": "평균 추천 순위(우리/경쟁사)",
            "extra_metric_value": f"{round(mean(ranked_our),2) if ranked_our else '-'} / {round(mean(ranked_target),2) if ranked_target else '-'}",
            "clarification_count": clar_count,
            "off_topic_count": off_count,
            "effective_denom": eff_denom,
            "effective_primary_count": eff_surfaced,
            "effective_primary_value": pct(eff_surfaced, eff_denom),
            "effective_secondary_count": eff_co_mentioned,
            "effective_secondary_value": pct(eff_co_mentioned, eff_denom),
            "explain": "경쟁사 대신 다른 대안을 찾을 때 우리 브랜드가 얼마나 추천되는지",
        })

    h2h = category_rows(rows, "H2H")
    if h2h:
        wins = sum(1 for r in h2h if (r.get("win_loss_draw") or "").strip().lower() == "win")
        losses = sum(1 for r in h2h if (r.get("win_loss_draw") or "").strip().lower() == "loss")
        draws = sum(1 for r in h2h if (r.get("win_loss_draw") or "").strip().lower() == "draw")
        compared = wins + losses + draws
        clar_count = sum(1 for r in h2h if yn_to_bool(r.get("clarification_request")))
        off_count = sum(1 for r in h2h if yn_to_bool(r.get("off_topic")))
        eff_rows = [r for r in h2h if is_effective(r)]
        eff_denom = len(eff_rows)
        eff_wins = sum(1 for r in eff_rows if (r.get("win_loss_draw") or "").strip().lower() == "win")
        eff_losses = sum(1 for r in eff_rows if (r.get("win_loss_draw") or "").strip().lower() == "loss")
        cards.append({
            "category_code": "H2H",
            "category": CATEGORY_LABELS["H2H"],
            "total_rows": len(h2h),
            "primary_metric_label": "승률",
            "primary_metric_value": pct(wins, compared),
            "primary_metric_count": wins,
            "primary_metric_denom": compared,
            "secondary_metric_label": "패배율",
            "secondary_metric_value": pct(losses, compared),
            "secondary_metric_count": losses,
            "secondary_metric_denom": compared,
            "extra_metric_label": "무승부율",
            "extra_metric_value": pct(draws, compared),
            "clarification_count": clar_count,
            "off_topic_count": off_count,
            "effective_denom": eff_denom,
            "effective_primary_count": eff_wins,
            "effective_primary_value": pct(eff_wins, eff_denom),
            "effective_secondary_count": eff_losses,
            "effective_secondary_value": pct(eff_losses, eff_denom),
            "explain": "직접 비교 질문에서 경쟁사 대비 얼마나 이기는지",
        })

    return cards


def aggregate_by_prompt_type(rows: List[Dict]) -> List[Dict]:
    cards = {r["category_code"]: r for r in build_category_cards(rows)}
    out = []
    for code in ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"]:
        card = cards.get(code)
        if not card:
            continue
        out.append(card)
    return out


def aggregate_h2h_by_competitor(rows: List[Dict]) -> List[Dict]:
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        if (row.get("category_code") or "") == "H2H" and (row.get("target_competitor") or "").strip():
            groups[(row.get("target_competitor") or "").strip()].append(row)

    results = []
    for competitor, items in sorted(groups.items()):
        wins = sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "win")
        losses = sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "loss")
        draws = sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "draw")
        compared = wins + losses + draws
        our_ranks = [r["our_brand_rank"] for r in items if isinstance(r.get("our_brand_rank"), int)]
        target_ranks = [r["target_competitor_rank"] for r in items if isinstance(r.get("target_competitor_rank"), int)]
        results.append({
            "target_competitor": competitor,
            "total_rows": len(items),
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": pct(wins, compared),
            "loss_rate": pct(losses, compared),
            "draw_rate": pct(draws, compared),
            "avg_our_rank_when_ranked": round(mean(our_ranks), 2) if our_ranks else None,
            "avg_target_rank_when_ranked": round(mean(target_ranks), 2) if target_ranks else None,
        })
    return results


def aggregate_comp_only_by_competitor(rows: List[Dict]) -> List[Dict]:
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        if (row.get("category_code") or "") == "COMP_ONLY" and (row.get("target_competitor") or "").strip():
            groups[(row.get("target_competitor") or "").strip()].append(row)

    results = []
    for competitor, items in sorted(groups.items()):
        surfaced = sum(1 for r in items if (r.get("surfacing_outcome") or "") == "surfaced")
        co_mentioned = sum(1 for r in items if (r.get("surfacing_outcome") or "") == "co_mentioned")
        not_surfaced = sum(1 for r in items if (r.get("surfacing_outcome") or "") == "not_surfaced")
        our_ranks = [r["our_brand_rank"] for r in items if isinstance(r.get("our_brand_rank"), int)]
        target_ranks = [r["target_competitor_rank"] for r in items if isinstance(r.get("target_competitor_rank"), int)]
        results.append({
            "target_competitor": competitor,
            "total_rows": len(items),
            "surfaced_count": surfaced,
            "co_mentioned_count": co_mentioned,
            "not_surfaced_count": not_surfaced,
            "surfaced_rate": pct(surfaced, len(items)),
            "co_mentioned_rate": pct(co_mentioned, len(items)),
            "not_surfaced_rate": pct(not_surfaced, len(items)),
            "avg_our_rank_when_ranked": round(mean(our_ranks), 2) if our_ranks else None,
            "avg_target_rank_when_ranked": round(mean(target_ranks), 2) if target_ranks else None,
        })
    return results


SUBCATEGORY_LABELS = {
    "CAT": "카테고리 일반",
    "SYM": "증상/상황",
    "ALT": "솔루션 대안 비교",
    "PRC": "가격 기반",
    "USE": "유스케이스",
    "DEC": "구매의도 단일선택",
}


def aggregate_neutral_by_subcategory(rows: List[Dict]) -> List[Dict]:
    """NEUTRAL 응답을 subcategory 별로 묶어 집계. Wilson CI용 count/denom 포함."""
    neutral = category_rows(rows, "NEUTRAL")
    if not neutral:
        return []
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for r in neutral:
        code = (r.get("subcategory") or "").strip() or "UNSPEC"
        groups[code].append(r)

    order = ["CAT", "SYM", "ALT", "PRC", "USE", "DEC", "UNSPEC"]
    results = []
    for code in order:
        items = groups.get(code, [])
        if not items:
            continue
        mention = sum(1 for r in items if yn_to_bool(r.get("mention_brand")))
        reco = sum(1 for r in items if yn_to_bool(r.get("our_brand_recommended")))
        top1 = sum(1 for r in items if yn_to_bool(r.get("our_brand_top1")))
        results.append({
            "subcategory": code,
            "subcategory_label": SUBCATEGORY_LABELS.get(code, code),
            "total_rows": len(items),
            "mention_count": mention,
            "mention_rate": pct(mention, len(items)),
            "recommendation_count": reco,
            "recommendation_rate": pct(reco, len(items)),
            "top1_count": top1,
            "top1_rate": pct(top1, len(items)),
        })
    return results


def aggregate_by_prompt(rows: List[Dict], prompts_lookup: Optional[Dict[str, str]] = None) -> List[Dict]:
    prompts_lookup = prompts_lookup or {}
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        groups[row["prompt_id"]].append(row)

    results = []
    for prompt_id, items in sorted(groups.items()):
        first = items[0]
        category_code = first.get("category_code", "")
        sentiment_counter = Counter((i.get("sentiment_to_brand") or "null").strip() for i in items)

        mention_count = sum(1 for r in items if yn_to_bool(r.get("mention_brand")))
        reco_count = sum(1 for r in items if yn_to_bool(r.get("our_brand_recommended")))
        top1_count = sum(1 for r in items if yn_to_bool(r.get("our_brand_top1")))
        top3_count = sum(1 for r in items if yn_to_bool(r.get("our_brand_top3")))
        clarification_count = sum(1 for r in items if yn_to_bool(r.get("clarification_request")))
        off_topic_count = sum(1 for r in items if yn_to_bool(r.get("off_topic")))
        evasion_count = sum(1 for r in items if yn_to_bool(r.get("evasion")))
        row = {
            "prompt_id": prompt_id,
            "category_code": category_code,
            "category": first.get("category", ""),
            "subcategory": (first.get("subcategory") or "").strip(),
            "target_competitor": first.get("target_competitor", ""),
            "runs": len(items),
            "mention_count": mention_count,
            "mention_rate": pct(mention_count, len(items)),
            "recommendation_count": reco_count,
            "recommendation_rate": pct(reco_count, len(items)),
            "top1_count": top1_count,
            "top1_rate": pct(top1_count, len(items)),
            "top3_count": top3_count,
            "top3_rate": pct(top3_count, len(items)),
            "clarification_count": clarification_count,
            "off_topic_count": off_topic_count,
            "evasion_count": evasion_count,
            "positive_count": sentiment_counter.get("positive", 0),
            "neutral_count": sentiment_counter.get("neutral", 0),
            "negative_count": sentiment_counter.get("negative", 0),
            "wins": sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "win"),
            "losses": sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "loss"),
            "draws": sum(1 for r in items if (r.get("win_loss_draw") or "").strip().lower() == "draw"),
            "surfaced_count": sum(1 for r in items if (r.get("surfacing_outcome") or "") == "surfaced"),
            "co_mentioned_count": sum(1 for r in items if (r.get("surfacing_outcome") or "") == "co_mentioned"),
            "not_surfaced_count": sum(1 for r in items if (r.get("surfacing_outcome") or "") == "not_surfaced"),
            "prompt_text": prompts_lookup.get(prompt_id, ""),
            "sample_response_preview": next((i.get("response_preview", "") for i in items if i.get("response_preview")), ""),
        }
        results.append(row)
    return results


def _f(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_diagnostics_and_actions(
    cards: List[Dict],
    h2h_by_competitor: List[Dict],
    comp_only_by_competitor: List[Dict],
    neutral_by_subcategory: Optional[List[Dict]] = None,
) -> Dict[str, List]:
    card_map = {c["category_code"]: c for c in cards}
    candidates: List[Dict] = []

    # ── NEUTRAL: 언급률 + 추천률 + 서브분류별 ────────────────────────────
    neutral = card_map.get("NEUTRAL")
    if neutral:
        mention_rate = _f(neutral.get("primary_metric_value"))
        reco_rate = _f(neutral.get("secondary_metric_value"))
        if mention_rate < 30:
            severity_word = "매우 약함" if mention_rate < 5 else "약함" if mention_rate < 15 else "보통 이하"
            candidates.append({
                "severity": max(0.0, 30 - mention_rate),
                "diagnostic": f"중립 질문 언급률 {mention_rate:g}%로 신규 유입이 {severity_word}",
                "action": {
                    "problem": f"중립 질문에서 브랜드 등장률 낮음 ({mention_rate:g}%)",
                    "hypothesis": "AI가 기본 후보군으로 우리 브랜드를 잘 떠올리지 못함",
                    "actions": [
                        "제품 소개/FAQ 콘텐츠 보강",
                        "추천 리뷰·사용기 콘텐츠 확대",
                        "카테고리 탐색형 비교 콘텐츠 작성",
                    ],
                },
            })
        if reco_rate < 25 and mention_rate >= 5:
            candidates.append({
                "severity": max(0.0, 25 - reco_rate) * 0.8,
                "diagnostic": f"중립 질문 추천률 {reco_rate:g}% — 언급은 되어도 권유까지 못 감",
                "action": {
                    "problem": f"언급되지만 추천으로 이어지지 않음 ({reco_rate:g}%)",
                    "hypothesis": "AI가 단순 정보 제공만 하고 명시적 권유 표현으로 이어가지 못함",
                    "actions": [
                        "“OO에 추천드립니다” 형식의 사용 시나리오 콘텐츠",
                        "베스트 픽 리스트형 콘텐츠로 권유 시그널 노출",
                    ],
                },
            })
        for sub in neutral_by_subcategory or []:
            n = int(_f(sub.get("total_rows")))
            sub_mention = _f(sub.get("mention_rate"))
            if n >= 5 and sub_mention < 25:
                code = sub.get("subcategory", "")
                label = sub.get("subcategory_label") or code
                candidates.append({
                    "severity": max(0.0, 25 - sub_mention) * 0.6,
                    "diagnostic": f"중립 ‘{label}’ 의도 언급률 {sub_mention:g}% (n={n})",
                    "action": {
                        "problem": f"‘{label}’ 류 질문에서 브랜드 미노출 ({sub_mention:g}%, n={n})",
                        "hypothesis": f"이 의도({code})에 맞는 정확한 키워드 매칭이 부족",
                        "actions": [
                            f"{label} 시나리오에 특화된 콘텐츠 추가",
                            "관련 키워드(예시 질문 톤)로 SEO·블로그 강화",
                        ],
                    },
                })

    # ── BRAND_ONLY: 부정 톤 + 긍정 부족 ─────────────────────────────────
    brand_only = card_map.get("BRAND_ONLY")
    if brand_only:
        neg_rate = _f(brand_only.get("secondary_metric_value"))
        pos_rate = _f(brand_only.get("primary_metric_value"))
        if neg_rate > 15:
            candidates.append({
                "severity": neg_rate - 10,
                "diagnostic": f"브랜드 직접 질문 부정 톤 {neg_rate:g}%로 평판 리스크",
                "action": {
                    "problem": f"브랜드 직접 질문에서 부정 언급 비율 {neg_rate:g}%",
                    "hypothesis": "자주 언급되는 부정 주제가 AI 응답에 반영됨",
                    "actions": [
                        "부정 주제 대응 콘텐츠 작성",
                        "공식 Q&A/오해 해명 페이지 강화",
                        "긍정 리뷰·수상 이력 노출 확대",
                    ],
                },
            })
        if pos_rate < 30 and _f(brand_only.get("total_rows")) > 0:
            candidates.append({
                "severity": max(0.0, 40 - pos_rate),
                "diagnostic": f"브랜드 직접 질문 긍정 톤 {pos_rate:g}%로 인지 품질 낮음",
                "action": {
                    "problem": f"브랜드 직접 질문 응답이 중립/부정에 몰림 ({pos_rate:g}% 긍정)",
                    "hypothesis": "AI가 참조할 긍정 시그널(리뷰/수상/임상)이 부족",
                    "actions": [
                        "수상·임상·후기 페이지 강화",
                        "브랜드 스토리 콘텐츠 강화",
                    ],
                },
            })

    # ── COMP_ONLY: 모든 경쟁사 순회 (이전엔 worst 1개만) ─────────────────
    for r in comp_only_by_competitor or []:
        ns_rate = _f(r.get("not_surfaced_rate"))
        if ns_rate > 30:
            competitor = r.get("target_competitor", "경쟁사")
            candidates.append({
                "severity": ns_rate - 30,
                "diagnostic": f"{competitor} 대안 질문 미노출률 {ns_rate:g}%",
                "action": {
                    "problem": f"{competitor} 대안 질문에서 우리 브랜드 미노출 {ns_rate:g}%",
                    "hypothesis": "경쟁사 대체재 맥락에서 AI가 우리 브랜드를 후보로 인식 못 함",
                    "actions": [
                        f"\"{competitor} 대신 우리 브랜드\" 비교 콘텐츠 작성",
                        "대안 검색 키워드 타겟 리뷰 확대",
                        "경쟁사 대비 차별 포인트 페이지 강화",
                    ],
                },
            })

    # ── H2H: 모든 경쟁사 순회, 임계 완화 (loss+draw > 50 또는 win < 40) ─
    for r in h2h_by_competitor or []:
        win_rate = _f(r.get("win_rate"))
        loss_rate = _f(r.get("loss_rate"))
        draw_rate = _f(r.get("draw_rate"))
        total = int(_f(r.get("total_rows")))
        if total < 3:
            continue
        # 명확한 열세
        if win_rate < 40 and loss_rate > 20:
            competitor = r.get("target_competitor", "경쟁사")
            candidates.append({
                "severity": loss_rate - win_rate + 5,
                "diagnostic": f"{competitor} 대비 H2H 승률 {win_rate:g}%, 패배율 {loss_rate:g}%",
                "action": {
                    "problem": f"{competitor} 직접 비교에서 열세 (승률 {win_rate:g}%, 패배율 {loss_rate:g}%)",
                    "hypothesis": f"{competitor}의 특정 포지셔닝에서 밀리고 있음",
                    "actions": [
                        f"{competitor} 대비 차별 메시지 명확화",
                        "비교표/비교 리뷰 콘텐츠 강화",
                        "약점 포지션 보완 콘텐츠 작성",
                    ],
                },
            })
        # 무승부 과다 — 변별력 부족
        elif draw_rate > 50:
            competitor = r.get("target_competitor", "경쟁사")
            candidates.append({
                "severity": draw_rate - 50,
                "diagnostic": f"{competitor} 비교 무승부 {draw_rate:g}% — AI가 변별 못 함",
                "action": {
                    "problem": f"{competitor} 비교에서 우열 판정 안 됨 (무 {draw_rate:g}%)",
                    "hypothesis": f"양 브랜드 모두 추천 안 하거나 동등 추천 → 차별 시그널 부족",
                    "actions": [
                        f"{competitor}와 다른 우위 포인트 명문화",
                        "구체 수치·임상 결과로 차별점 강화",
                    ],
                },
            })

    candidates.sort(key=lambda c: -c["severity"])

    if not candidates:
        return {
            "diagnostics": ["현재 측정 기준 뚜렷한 리스크 신호는 약함"],
            "action_items": [{
                "problem": "현재 우선 개선 과제 없음",
                "hypothesis": "4가지 질문 유형 모두 기준선 이상",
                "actions": ["현 포지션 유지 모니터링"],
            }],
        }

    # diagnostics는 상위 3개(요약용), action_items는 전체 — UI에서 상위 N개를 강조 카드로,
    # 나머지를 리스트로 분리 렌더한다.
    return {
        "diagnostics": [c["diagnostic"] for c in candidates[:3]],
        "action_items": [c["action"] for c in candidates],
    }


def build_spotlights(by_prompt: List[Dict]) -> Dict[str, List[Dict]]:
    def pick(rows: List[Dict], key, reverse: bool, limit: int = 3, filter_fn=None) -> List[Dict]:
        pool = [r for r in rows if (filter_fn is None or filter_fn(r))]
        pool.sort(key=key, reverse=reverse)
        out = []
        for r in pool[:limit]:
            out.append({
                "prompt_id": r.get("prompt_id", ""),
                "category_code": r.get("category_code", ""),
                "target_competitor": r.get("target_competitor", "") or "",
                "prompt_text": r.get("prompt_text", "") or "",
                "mention_rate": _f(r.get("mention_rate")),
                "recommendation_rate": _f(r.get("recommendation_rate")),
                "wins": int(_f(r.get("wins"))),
                "losses": int(_f(r.get("losses"))),
                "draws": int(_f(r.get("draws"))),
                "surfaced_count": int(_f(r.get("surfaced_count"))),
                "not_surfaced_count": int(_f(r.get("not_surfaced_count"))),
                "positive_count": int(_f(r.get("positive_count"))),
                "negative_count": int(_f(r.get("negative_count"))),
            })
        return out

    neutral = [r for r in by_prompt if r.get("category_code") == "NEUTRAL"]
    brand_only = [r for r in by_prompt if r.get("category_code") == "BRAND_ONLY"]
    comp_only = [r for r in by_prompt if r.get("category_code") == "COMP_ONLY"]
    h2h = [r for r in by_prompt if r.get("category_code") == "H2H"]

    return {
        "neutral_strong": pick(neutral, key=lambda r: _f(r.get("mention_rate")), reverse=True,
                               filter_fn=lambda r: _f(r.get("mention_rate")) > 0),
        "neutral_weak": pick(neutral, key=lambda r: r.get("prompt_id", ""), reverse=False,
                             filter_fn=lambda r: _f(r.get("mention_rate")) == 0),
        "h2h_win": pick(h2h, key=lambda r: (int(_f(r.get("wins"))), -int(_f(r.get("losses")))), reverse=True,
                        filter_fn=lambda r: int(_f(r.get("wins"))) > 0),
        "h2h_loss": pick(h2h, key=lambda r: (int(_f(r.get("losses"))), -int(_f(r.get("wins")))), reverse=True,
                         filter_fn=lambda r: int(_f(r.get("losses"))) > 0),
        "comp_only_surfaced": pick(comp_only, key=lambda r: int(_f(r.get("surfaced_count"))), reverse=True,
                                   filter_fn=lambda r: int(_f(r.get("surfaced_count"))) > 0),
        "comp_only_not_surfaced": pick(comp_only, key=lambda r: int(_f(r.get("not_surfaced_count"))), reverse=True,
                                       filter_fn=lambda r: int(_f(r.get("not_surfaced_count"))) > 0),
        "brand_only_negative": pick(brand_only, key=lambda r: int(_f(r.get("negative_count"))), reverse=True,
                                    filter_fn=lambda r: int(_f(r.get("negative_count"))) > 0),
    }


def build_summary_json(
    brand: Dict,
    cards: List[Dict],
    h2h_by_competitor: List[Dict],
    comp_only_by_competitor: List[Dict],
    by_prompt: List[Dict],
    neutral_by_subcategory: Optional[List[Dict]] = None,
) -> Dict:
    category_map = {c["category_code"]: c for c in cards}
    diag = build_diagnostics_and_actions(
        cards, h2h_by_competitor, comp_only_by_competitor,
        neutral_by_subcategory=neutral_by_subcategory,
    )
    spotlights = build_spotlights(by_prompt)
    return {
        "brand_name": brand.get("brand_name", ""),
        "dashboard_mode": "category_first",
        "category_cards": cards,
        "neutral": category_map.get("NEUTRAL", {}),
        "brand_only": category_map.get("BRAND_ONLY", {}),
        "comp_only": category_map.get("COMP_ONLY", {}),
        "h2h": category_map.get("H2H", {}),
        "h2h_by_competitor": sorted(h2h_by_competitor, key=lambda x: (-float(x["loss_rate"]), x["target_competitor"])),
        "comp_only_by_competitor": sorted(comp_only_by_competitor, key=lambda x: (-float(x["not_surfaced_rate"]), x["target_competitor"])),
        "diagnostics": diag["diagnostics"],
        "action_items": diag["action_items"],
        "spotlights": spotlights,
        "neutral_by_subcategory": neutral_by_subcategory or [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="GEO Dashboard Aggregator (Beginner-friendly)")
    parser.add_argument("--brand", required=True, help="brand_config.json 경로")
    args = parser.parse_args()

    brand = load_brand_config(args.brand)
    brand_dir = os.path.dirname(args.brand)
    parsed_path = os.path.join(brand_dir, "results", "parsed_results.csv")
    output_dir = os.path.join(brand_dir, "results", "dashboard")

    if not os.path.exists(parsed_path):
        print(f"{parsed_path} 파일이 없습니다. 04_parse_responses.py를 먼저 실행하세요.")
        return

    rows = load_parsed_results(parsed_path)
    if not rows:
        print("parsed_results.csv에 데이터가 없습니다.")
        return

    prompts_lookup: Dict[str, str] = {}
    prompts_csv_path = os.path.join(brand_dir, "prompts.csv")
    if os.path.exists(prompts_csv_path):
        with open(prompts_csv_path, "r", encoding="utf-8-sig") as pf:
            for prow in csv.DictReader(pf):
                pid = (prow.get("prompt_id") or "").strip()
                ptext = (prow.get("prompt_text") or "").strip()
                if pid and ptext:
                    prompts_lookup[pid] = ptext

    category_cards = aggregate_by_prompt_type(rows)
    h2h_by_competitor = aggregate_h2h_by_competitor(rows)
    comp_only_by_competitor = aggregate_comp_only_by_competitor(rows)
    by_prompt = aggregate_by_prompt(rows, prompts_lookup=prompts_lookup)
    neutral_by_subcategory = aggregate_neutral_by_subcategory(rows)
    summary = build_summary_json(
        brand, category_cards, h2h_by_competitor, comp_only_by_competitor,
        by_prompt, neutral_by_subcategory=neutral_by_subcategory,
    )

    write_csv(
        os.path.join(output_dir, "category_cards.csv"),
        category_cards,
        [
            "category_code", "category", "total_rows",
            "primary_metric_label", "primary_metric_value",
            "primary_metric_count", "primary_metric_denom",
            "secondary_metric_label", "secondary_metric_value",
            "secondary_metric_count", "secondary_metric_denom",
            "extra_metric_label", "extra_metric_value",
            "clarification_count", "off_topic_count",
            "effective_denom",
            "effective_primary_count", "effective_primary_value",
            "effective_secondary_count", "effective_secondary_value",
            "explain",
        ],
    )

    write_csv(
        os.path.join(output_dir, "by_prompt_type.csv"),
        category_cards,
        [
            "category_code", "category", "total_rows",
            "primary_metric_label", "primary_metric_value",
            "primary_metric_count", "primary_metric_denom",
            "secondary_metric_label", "secondary_metric_value",
            "secondary_metric_count", "secondary_metric_denom",
            "extra_metric_label", "extra_metric_value",
            "clarification_count", "off_topic_count",
            "effective_denom",
            "effective_primary_count", "effective_primary_value",
            "effective_secondary_count", "effective_secondary_value",
            "explain",
        ],
    )

    write_csv(
        os.path.join(output_dir, "h2h_by_competitor.csv"),
        h2h_by_competitor,
        [
            "target_competitor", "total_rows",
            "wins", "losses", "draws",
            "win_rate", "loss_rate", "draw_rate",
            "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
        ],
    )

    write_csv(
        os.path.join(output_dir, "comp_only_by_competitor.csv"),
        comp_only_by_competitor,
        [
            "target_competitor", "total_rows",
            "surfaced_count", "co_mentioned_count", "not_surfaced_count",
            "surfaced_rate", "co_mentioned_rate", "not_surfaced_rate",
            "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
        ],
    )

    write_csv(
        os.path.join(output_dir, "by_prompt.csv"),
        by_prompt,
        [
            "prompt_id", "category_code", "category", "subcategory", "target_competitor", "runs",
            "mention_count", "mention_rate",
            "recommendation_count", "recommendation_rate",
            "top1_count", "top1_rate",
            "top3_count", "top3_rate",
            "clarification_count", "off_topic_count", "evasion_count",
            "positive_count", "neutral_count", "negative_count",
            "wins", "losses", "draws",
            "surfaced_count", "co_mentioned_count", "not_surfaced_count",
            "prompt_text", "sample_response_preview",
        ],
    )

    if neutral_by_subcategory:
        write_csv(
            os.path.join(output_dir, "neutral_by_subcategory.csv"),
            neutral_by_subcategory,
            [
                "subcategory", "subcategory_label", "total_rows",
                "mention_count", "mention_rate",
                "recommendation_count", "recommendation_rate",
                "top1_count", "top1_rate",
            ],
        )

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"카테고리 중심 대시보드 집계 완료 → {output_dir}")


if __name__ == "__main__":
    main()
