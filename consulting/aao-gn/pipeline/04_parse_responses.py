"""
GEO 감사 응답 파싱 — brand_config.json에서 키워드·경쟁사 동적 로드

사용법:
  python 04_parse_responses.py --brand brands/bodydoctor/brand_config.json
"""

import argparse
import csv
import json
import os
import re
import time
from collections import defaultdict
from typing import Dict, List, Literal, Optional

from anthropic import Anthropic
from pydantic import BaseModel, Field

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

DEFAULT_COMPETITOR_LIMIT = 5


# ────────────────────────────────────────────────────────────────────
# Pydantic 출력 스키마 — Claude messages.parse() 가 자동 검증
# ────────────────────────────────────────────────────────────────────

YN = Literal["Y", "N"]


class ParseResult(BaseModel):
    our_brand_mentioned: YN
    our_brand_recommended: YN
    our_brand_rank: Optional[int] = None
    our_brand_top1: YN
    our_brand_top3: YN
    our_brand_sentiment: Optional[Literal["positive", "neutral", "negative"]] = None
    evidence_type: Optional[Literal["official", "review", "community", "media", "unknown"]] = None
    evasion: YN
    # 응답 자체가 추천을 안 한 게 아니라 "정보 더 주면 추천할게" 같은 되묻기.
    # 추천률 계산 시 분모에서 제외하거나 별도 카테고리로 다룰 수 있도록 분리.
    clarification_request: YN
    # 질문 의도와 응답이 안 맞는 경우. 예: "X보다 나은 거 뭐 있어?" → "X에 대해 설명"
    # COMP_ONLY/H2H 같은 비교 질문에서 특히 중요 — 진짜 미노출과 구분해야 함.
    off_topic: YN
    top_exposed_brands: List[str] = Field(default_factory=list)
    recommended_brands: List[str] = Field(default_factory=list)
    mentioned_competitors: List[str] = Field(default_factory=list)
    recommended_competitors: List[str] = Field(default_factory=list)
    top1_brand: str = ""
    final_recommendation: str = ""
    target_competitor_mentioned: YN
    target_competitor_recommended: YN
    target_competitor_rank: Optional[int] = None
    target_competitor_top1: YN


# ────────────────────────────────────────────────────────────────────
# System prompt 빌더 — 1000회 호출에서 동일 (prompt caching 대상)
# ────────────────────────────────────────────────────────────────────

PARSE_RULES = """다음은 {product_category} 관련 질문에 대한 AI 응답을 분석하는 작업입니다.
브랜드 노출·추천 상태를 **엄격한 정의에 따라** JSON으로 구조화해야 합니다.

[브랜드 컨텍스트 — 매 호출마다 동일]

우리 브랜드:
- 브랜드명: {brand_name}
- 영문명: {brand_name_en}

경쟁사 목록:
{competitor_names}

[엄격한 정의 — 잘못 분류 시 진단 결과가 오염됩니다]

▼ mentioned (Y/N): 응답 본문에 브랜드명/제품명이 한 번이라도 등장하면 Y.

▼ recommended (Y/N): AI가 사용자에게 그 브랜드/제품을 **사용·구매하도록 명시적으로 권유**했을 때만 Y.
  ✓ Y 인 경우 (명시적 추천 표현):
    - "...추천합니다", "...권장합니다", "...권해드립니다"
    - "고려하시면 좋습니다", "선택하시면 좋습니다", "...을 추천드립니다"
    - "...이 좋은 옵션입니다", "탁월한 선택입니다"
    - 번호 매긴 추천 목록에 포함
  ✗ N 인 경우 (추천 아님):
    - 단순 정보 제공: "X는 ~한 제품입니다", "X는 ~기능을 합니다"
    - 사실 진술: "X는 2020년 수상했습니다", "X는 FDA 인증을 받았습니다"
    - 비교 설명: "A는 ~하고 B는 ~합니다" (어느 쪽도 권유 안 함)
    - 사용법·주의사항 안내: "X 사용 시 주의하세요" (사용을 전제로 한 안내일 뿐 권유 아님)

▼ top1 (Y/N): 응답이 **명시적으로 순위를 매기고 1위로 지목**한 경우만 Y.
  ✓ Y 인 경우:
    - "1위로 추천", "가장 추천드리는 것은", "최우선 선택", "베스트는"
    - 번호 매긴 추천 목록의 1번
    - "X가 가장 좋습니다"
  ✗ N 인 경우:
    - 본문에서 첫 번째로 언급됨 (단순 텍스트 순서) → top1 아님
    - 회피·정보부족 답변에서 우리만 등장 → top1 아님
    - 비교 설명에서 우리가 먼저 나옴 → top1 아님
    - "X도 추천", "Y도 좋다"식 병렬 추천 → 어느 것도 top1 아님 (모두 N)

▼ top3 (Y/N): 명시적 ranking에서 상위 3위 안에 있을 때만 Y. top1 규칙과 동일하게 엄격.

▼ evasion (Y/N): AI가 답을 회피했으면 Y.
  ✓ 회피 패턴:
    - "현재 제공된 정보로는...어렵습니다"
    - "확인할 수 없습니다", "확인하기 어렵습니다"
    - "죄송하지만...찾을 수 없었습니다"
    - "구체적인 정보를 제공하기 어렵습니다"
    - 일반 정보만 제공하고 구체적 추천 회피
  ✓ evasion=Y 인 경우, recommended/top1/top3 는 모두 N (회피 시 추천 아님)

▼ clarification_request (Y/N): AI가 추천하기 전에 **사용자에게 추가 정보를 요구**한 경우 Y.
  ✓ 패턴:
    - "어떤 용도로 쓰실 건가요?"
    - "예산이 어느 정도세요?", "사용 시간대를 알려주시면..."
    - "더 자세한 정보를 알려주시면 추천드릴게요"
    - "사용자분의 상황을 더 알려주시면 적합한 제품을..."
  ✗ 일반 질문 답변 후 부가 안내가 들어간 경우는 N
    (예: "...추천드립니다. 추가로 OOO 상황이라면 다른 제품이 더 맞을 수 있어요" — 이미 추천했음)
  ✓ 의미: clarification_request=Y 인 응답은 "추천 거부"가 아니라 "정보 부족으로 보류" 상태.
    추천률 분모에서 제외해 해석할 수도 있음 (집계 단계 결정).

▼ off_topic (Y/N): 응답이 **질문 의도와 일치하지 않을** 때 Y.
  ✓ 대표 패턴:
    - "X보다 나은 거 뭐 있어?" → 대안을 묻는 질문인데 응답이 X(경쟁사)에 대한 설명만 함
    - "X 대신 살 만한 거?" → 대안 추천이 아니라 X 자체 리뷰
    - "A vs B 어디가 나아?" → 비교 없이 한쪽만 길게 설명 (직접 비교 회피)
    - "1만원대 추천" → 가격대 무시한 일반 추천
  ✗ 응답이 질문에 정확히 답하면 N
  ✓ 의미: off_topic=Y 면 진단 지표(comp_only 미노출, h2h 무승부 등) 분모에서 제외 고려 가치.

▼ sentiment (positive/neutral/negative/null):
  - positive: "탁월한", "효과 좋다", "강력 추천" 등
  - negative: "단점이 많다", "권장하지 않는다", "주의가 필요하다 (안전 경고)", "효과 미미"
  - neutral: 단순 정보 제공, 중립 비교, 사용법 안내
  - null: 우리 브랜드 미언급

▼ top_exposed_brands: 응답에서 명시적 추천 순위가 있을 때 순서대로. 명시 순위 없으면 [].

▼ top1_brand: 응답이 명시적으로 1위로 꼽은 브랜드. 명시 없으면 빈 문자열.

▼ mentioned_competitors / recommended_competitors: 우리 브랜드 제외, 경쟁사 목록 중 해당하는 것만.

엄격하게 판단하세요 — 애매하면 N으로. 출력 스키마는 시스템이 자동으로 검증합니다.

[입력 형식]
사용자 메시지에 다음 형식으로 응답이 전달됩니다:

타깃 경쟁사: <경쟁사명 또는 "없음">

응답:
---
<AI 응답 본문>
---

각 호출마다 응답을 분석해 ParseResult 스키마에 맞춰 반환하세요."""


def build_parse_system(brand: Dict, competitors: List[Dict]) -> str:
    """매 호출에서 동일한 system 프롬프트. 캐시 대상."""
    competitor_names = "\n".join(f"- {c['name']}" for c in competitors) or "- 없음"
    return PARSE_RULES.format(
        product_category=brand["product_category"],
        brand_name=brand["brand_name"],
        brand_name_en=brand.get("brand_name_en", ""),
        competitor_names=competitor_names,
    )


def load_brand_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_audit_settings(brand: Dict) -> Dict:
    return brand.get("audit_settings", {}) if isinstance(brand.get("audit_settings"), dict) else {}


def get_competitors(brand: Dict) -> List[Dict]:
    settings = get_audit_settings(brand)
    competitor_limit = int(settings.get("competitor_limit", DEFAULT_COMPETITOR_LIMIT) or DEFAULT_COMPETITOR_LIMIT)
    raw = brand.get("competitors", [])
    cleaned = [c for c in raw if isinstance(c, dict) and c.get("name", "").strip()]
    return cleaned[:competitor_limit]


def expand_name_variants(name: str) -> List[str]:
    """
    브랜드·경쟁사명 자동 변형 파생.
    원본 + 괄호 제거 + 괄호 속 영문 + 공백/하이픈 제거 + 소문자 버전.
    """
    raw = (name or "").strip()
    if not raw:
        return []
    variants = {raw}
    no_paren = re.sub(r"\s*\([^\)]*\)", "", raw).strip()
    if no_paren:
        variants.add(no_paren)
    paren_parts = re.findall(r"\(([^\)]*)\)", raw)
    for p in paren_parts:
        p = p.strip()
        if p:
            variants.add(p)
    compact = re.sub(r"[\s\-_/\.]", "", raw)
    if compact:
        variants.add(compact)
    for v in list(variants):
        variants.add(v.lower())
    return sorted(v for v in variants if v)


def competitor_match_keywords(comp: Dict) -> List[str]:
    """경쟁사 매칭용 키워드 — name + keywords + 자동 파생 변형"""
    name = (comp.get("name") or "").strip()
    if not name:
        return []
    extras = [str(k).strip() for k in comp.get("keywords", []) if str(k).strip()]
    all_names: List[str] = []
    for candidate in [name] + extras:
        all_names.extend(expand_name_variants(candidate))
    return sorted(set(all_names))


def brand_match_keywords(brand: Dict) -> List[str]:
    """자사 브랜드 매칭 키워드 — brand_name/en + brand_keywords + 자동 파생 변형"""
    bits = [brand.get("brand_name", "") or "", brand.get("brand_name_en", "") or ""]
    bits.extend(brand.get("brand_keywords") or [])
    out: List[str] = []
    for b in bits:
        out.extend(expand_name_variants(b))
    return sorted(set(k for k in out if k))


def load_responses(filepath: str) -> List[Dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """
    브랜드/경쟁사 탐지용 정규화 — 괄호·하이픈·슬래시·공백 전부 제거하고 소문자.
    이렇게 해야 'Easy-K' vs 'easy k' vs 'EasyK' 변형이 모두 매칭됨.
    """
    text = (text or "").lower().strip()
    text = re.sub(r"[\(\)\[\]\-_/\.]", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def quick_mention_check(text: str, brand_keywords: List[str]) -> bool:
    text_lower = normalize_text(text)
    return any(normalize_text(kw) in text_lower for kw in brand_keywords if kw)


def quick_competitor_check(text: str, competitors: List[Dict]) -> List[str]:
    found = []
    text_lower = normalize_text(text)
    if not text_lower:
        return []
    for comp in competitors:
        keywords = competitor_match_keywords(comp)
        for kw in keywords:
            kw_norm = normalize_text(kw)
            if kw_norm and kw_norm in text_lower:
                found.append(comp["name"])
                break
    return sorted(set(found))


def domain_from_url(url: str) -> str:
    """URL → 도메인 (인용 출처 분류용)"""
    try:
        from urllib.parse import urlparse
        netloc = urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


# evidence_type 자동 분류용 도메인 패턴
EVIDENCE_DOMAIN_RULES = [
    ("official", ["bodydoctor", "propolinse", "gncos", "store.", "shop.", "official", "brand.naver.com"]),
    ("media", ["news.", "chosun.com", "joongang.co.kr", "donga.com", "hankyung.com", "mk.co.kr",
               "yna.co.kr", "ytn.co.kr", "edaily.co.kr", "moneys.co.kr", "etoday.co.kr",
               "asiae.co.kr", "newsis.com", "fnnews.com", "biz.chosun.com"]),
    ("review", ["coupang.com", "11st.co.kr", "gmarket.co.kr", "auction.co.kr",
                "ssg.com", "tmon.co.kr", "wemakeprice.com", "smartstore.naver.com",
                "ohou.se", "olive", "review", "blog.naver.com/.*review"]),
    ("community", ["dcinside.com", "fmkorea.com", "ppomppu.co.kr", "82cook.com",
                   "ruliweb.com", "clien.net", "instiz.net", "theqoo.net",
                   "naver.com", "blog.", "cafe.", "tistory.com",
                   "youtube.com", "youtu.be", "instagram.com", "facebook.com",
                   "x.com", "twitter.com", "reddit.com", "pann.nate.com"]),
]


def infer_evidence_type_from_domains(domains: List[str]) -> Optional[str]:
    """인용된 URL 도메인들로부터 evidence_type 추론. 가장 자주 매칭된 유형 반환."""
    if not domains:
        return None
    counts: Dict[str, int] = defaultdict(int)
    for d in domains:
        d_low = d.lower()
        for ev_type, patterns in EVIDENCE_DOMAIN_RULES:
            if any(p in d_low for p in patterns):
                counts[ev_type] += 1
                break
        else:
            counts["unknown"] += 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def infer_rank_from_list(name: str, ranked_items: List[str]) -> Optional[int]:
    if not name:
        return None
    name_lower = normalize_text(name)
    for idx, item in enumerate(ranked_items, start=1):
        item_lower = normalize_text(item)
        if name_lower and name_lower in item_lower:
            return idx
    return None


# ────────────────────────────────────────────────────────────────────
# Post-validation — LLM 파서 결과를 응답 본문과 교차 검증
# ────────────────────────────────────────────────────────────────────

# AI가 추천을 명시했다고 볼 수 있는 시그널 단어들 (한국어)
# 선택형 프롬프트는 '적합', '낫다', '무난' 같은 비교 판정형 표현도 자주 씀 → 포함.
RECOMMENDATION_SIGNALS = [
    "추천", "권장", "권합니다", "권해", "권유",
    "고려해", "고려하시", "선택하는 것이", "선택하시면",
    "좋은 선택", "좋은 옵션", "추천드립니다", "추천 드립니다",
    "탁월", "최고의 선택", "베스트", "1순위", "1위로",
    "낫", "더 낫", "더 맞", "적합", "무난", "유리", "괜찮",
    "선호", "좋", "권할 만", "잘 맞",
]

# AI가 답을 회피했다고 볼 수 있는 시그널 (응답 도입부에 있어야 함)
EVASION_SIGNALS = [
    "확인할 수 없", "확인하기 어렵", "정보가 없", "정보를 찾을 수 없",
    "찾을 수 없었", "제공된 정보로는", "구체적인 정보를 제공하기 어렵",
    "죄송하지만", "정확한 정보를 제공하기 어렵", "현재로서는 알 수 없",
    "정보가 부족", "데이터가 부족",
]


def has_evasion_signal(response_text: str) -> bool:
    """응답 도입부(600자)에 회피 표현이 있는지만 체크."""
    head = (response_text or "")[:600]
    return any(sig in head for sig in EVASION_SIGNALS)


def has_recommendation_signal(response_text: str) -> bool:
    return any(sig in (response_text or "") for sig in RECOMMENDATION_SIGNALS)


def detect_evasion(response_text: str, row: Dict) -> bool:
    """
    엄격 회피 판정: 회피 표현이 있어도 아래 중 하나라도 있으면 회피 아님(부분 회피).
    - 추천 시그널
    - final_recommendation 값
    - 우리 또는 타깃 경쟁사 recommended=Y
    - 명시적 rank (우리 또는 타깃)
    """
    if not has_evasion_signal(response_text):
        return False
    if has_recommendation_signal(response_text):
        return False
    if (row.get("final_recommendation") or "").strip():
        return False
    if row.get("our_brand_recommended") == "Y" or row.get("target_competitor_recommended") == "Y":
        return False
    if row.get("our_brand_rank") is not None or row.get("target_competitor_rank") is not None:
        return False
    return True


def _has_any_decision_signal(row: Dict, response_text: str) -> bool:
    """LLM 판정을 뒤집지 않기 위한 '판단이 실제로 있었다'는 복합 신호."""
    if has_recommendation_signal(response_text):
        return True
    if (row.get("final_recommendation") or "").strip():
        return True
    if row.get("our_brand_rank") is not None:
        return True
    if row.get("our_brand_top1") == "Y" or row.get("our_brand_top3") == "Y":
        return True
    return False


def post_validate(row: Dict, response_text: str) -> List[str]:
    """
    LLM 파서 결과를 응답 본문 시그널과 교차 검증.

    완화된 원칙:
    - 회피 시그널 + (추천/final_rec/rank 전부 없음) 일 때만 evasion=Y
    - recommended 다운그레이드도 복합 신호(_has_any_decision_signal)가 모두 없을 때만 수행
    """
    downgrades: List[str] = []
    text = response_text or ""

    is_evasion = detect_evasion(text, row)
    row["evasion"] = "Y" if is_evasion else "N"

    if is_evasion:
        if row.get("our_brand_top1") == "Y":
            row["our_brand_top1"] = "N"
            downgrades.append("our_top1→N (evasion)")
        if row.get("our_brand_top3") == "Y":
            row["our_brand_top3"] = "N"
            downgrades.append("our_top3→N (evasion)")
        if row.get("target_competitor_top1") == "Y":
            row["target_competitor_top1"] = "N"
            downgrades.append("target_top1→N (evasion)")
        if row.get("our_brand_rank") is not None:
            row["our_brand_rank"] = None
            downgrades.append("our_rank→null (evasion)")

    # 추천 다운그레이드: LLM이 Y라고 했는데 판단 신호가 하나도 없을 때만 뒤집음
    if not _has_any_decision_signal(row, text):
        if row.get("our_brand_recommended") == "Y":
            row["our_brand_recommended"] = "N"
            row["our_brand_top1"] = "N"
            row["our_brand_top3"] = "N"
            row["our_brand_rank"] = None
            downgrades.append("our_rec→N (no decision signal)")
        if row.get("target_competitor_recommended") == "Y":
            row["target_competitor_recommended"] = "N"
            row["target_competitor_top1"] = "N"
            row["target_competitor_rank"] = None
            downgrades.append("target_rec→N (no decision signal)")

    return downgrades


def determine_win_loss_draw(row: Dict, brand: Dict) -> str:
    """
    H2H 전용 결과 판정. COMP_ONLY는 의미가 다르므로 별도로 determine_surfacing_outcome 사용.
    """
    category_code = row.get("category_code", "")
    if category_code != "H2H":
        return ""

    brand_name = brand["brand_name"]
    our_rank = row.get("our_brand_rank")
    target_rank = row.get("target_competitor_rank")
    final_rec = row.get("final_recommendation", "") or ""
    target_comp = (row.get("target_competitor") or "").strip()

    if not target_comp:
        return ""

    our_rec = row.get("our_brand_recommended") == "Y"
    their_rec = row.get("target_competitor_recommended") == "Y"

    if our_rec and not their_rec:
        return "win"
    if their_rec and not our_rec:
        return "loss"

    if isinstance(our_rank, int) and isinstance(target_rank, int):
        if our_rank < target_rank:
            return "win"
        if our_rank > target_rank:
            return "loss"
        return "draw"

    if our_rec and their_rec:
        if brand_name and brand_name in final_rec and target_comp not in final_rec:
            return "win"
        if target_comp and target_comp in final_rec and brand_name not in final_rec:
            return "loss"
        return "draw"

    # 둘 다 명시 추천 없음 — AI가 한쪽을 고르지 않고 양쪽 설명만 한 경우도 비교 결과의 하나로,
    # "무승부(결정 유보)"로 흡수한다. 그래야 H2H 총 runs가 전부 W/L/D에 잡힌다.
    return "draw"


def determine_surfacing_outcome(row: Dict) -> str:
    """
    COMP_ONLY 전용 outcome. "경쟁사 지명 질문에 우리 브랜드가 대안으로 떠오르는가".

    - surfaced: 우리 브랜드가 명시 추천됨 (대안 탐색 성공)
    - co_mentioned: 언급은 되었으나 추천은 아님
    - not_surfaced: 전혀 언급되지 않음
    - "" : COMP_ONLY 아니면 빈값
    """
    if row.get("category_code") != "COMP_ONLY":
        return ""
    if row.get("our_brand_recommended") == "Y":
        return "surfaced"
    if row.get("mention_brand") == "Y":
        return "co_mentioned"
    return "not_surfaced"


def parse_with_llm(
    client: Anthropic,
    system_prompt: str,
    response_text: str,
    target_competitor: str,
    prompt_id: str = "",
    log_cache: bool = False,
) -> Optional[Dict]:
    """
    Claude 로 응답을 ParseResult 스키마에 맞춰 구조화.

    System prompt 는 매 호출에서 동일 (cache_control 적용).
    User message 만 가변 (target_competitor + response_text).
    """
    user_content = (
        f"타깃 경쟁사: {target_competitor or '없음'}\n\n"
        f"응답:\n---\n{response_text[:8000]}\n---"
    )

    last_error = None
    for attempt in range(2):
        try:
            result = client.messages.parse(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                system=[{
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": user_content}],
                output_format=ParseResult,
            )
            if log_cache:
                u = result.usage
                print(
                    f"    [cache] write={u.cache_creation_input_tokens} "
                    f"read={u.cache_read_input_tokens} "
                    f"input={u.input_tokens} out={u.output_tokens}"
                )
            parsed: ParseResult = result.parsed_output
            return parsed.model_dump()
        except Exception as e:
            last_error = f"Claude error (attempt {attempt + 1}): {str(e)[:120]}"
            time.sleep(0.5)

    print(f"  ⚠️  LLM 파싱 실패 [{prompt_id}]: {last_error}")
    return None


def parse_all(responses: List[Dict], brand: Dict, use_llm: bool = True) -> List[Dict]:
    has_key = bool(ANTHROPIC_API_KEY) and not ANTHROPIC_API_KEY.startswith("sk-ant-...")
    client = Anthropic(api_key=ANTHROPIC_API_KEY) if use_llm and has_key else None
    competitors = get_competitors(brand)
    # 자동 변형 파생을 한 번만 수행
    brand_keywords_expanded = brand_match_keywords(brand)
    # System prompt 한 번만 빌드 (1000회 호출에서 캐시 적중)
    system_prompt = build_parse_system(brand, competitors) if client else ""
    parsed = []
    parse_fail_count = 0
    downgrade_counts: Dict[str, int] = defaultdict(int)
    evasion_count = 0

    for i, resp in enumerate(responses):
        text = resp.get("response") or ""
        target_competitor = (resp.get("target_competitor") or "").strip()
        citations = resp.get("citations") or []
        cited_domains = [domain_from_url(c.get("url", "")) for c in citations if isinstance(c, dict)]
        cited_domains = [d for d in cited_domains if d]
        print(
            f"[{i + 1}/{len(responses)}] {resp['prompt_id']} run{resp['run_number']}...",
            end=" ",
            flush=True,
        )

        mention = quick_mention_check(text, brand_keywords_expanded)
        competitor_mentions = quick_competitor_check(text, competitors)
        target_mentioned = "Y" if target_competitor and target_competitor in competitor_mentions else "N"
        evidence_from_urls = infer_evidence_type_from_domains(cited_domains)

        row = {
            "prompt_id": resp["prompt_id"],
            "run_number": resp["run_number"],
            "category_code": resp.get("category_code", ""),
            "category": resp["category"],
            "subcategory": resp.get("subcategory", ""),
            "target_competitor": target_competitor,
            "mention_brand": "Y" if mention else "N",
            "our_brand_recommended": "N",
            "our_brand_rank": None,
            "our_brand_top1": "N",
            "our_brand_top3": "N",
            "sentiment_to_brand": None,
            "evidence_type": evidence_from_urls,
            "competitor_mentioned": ", ".join(competitor_mentions),
            "recommended_competitors": "",
            "top1_brand": "",
            "final_recommendation": "",
            "target_competitor_mentioned": target_mentioned,
            "target_competitor_recommended": "N",
            "target_competitor_rank": None,
            "target_competitor_top1": "N",
            "win_loss_draw": "",
            "surfacing_outcome": "",
            "response_preview": text[:800].replace("\n", " "),
            "cited_domains": ", ".join(sorted(set(cited_domains))[:8]),
            "parse_failed": "N",
            "evasion": "N",
            "clarification_request": "N",
            "off_topic": "N",
        }

        llm_result = None
        if client:
            # 첫 5호출에서 cache stats 출력해 캐시 적중 검증
            log_cache = i < 5
            llm_result = parse_with_llm(
                client,
                system_prompt,
                text,
                target_competitor,
                prompt_id=resp["prompt_id"],
                log_cache=log_cache,
            )
            time.sleep(0.3)

        if llm_result:
            top_exposed = [str(x).strip() for x in llm_result.get("top_exposed_brands", []) if str(x).strip()]
            mentioned_competitors = [
                str(x).strip() for x in llm_result.get("mentioned_competitors", []) if str(x).strip()
            ]
            recommended_competitors = [
                str(x).strip() for x in llm_result.get("recommended_competitors", []) if str(x).strip()
            ]

            row["mention_brand"] = llm_result.get("our_brand_mentioned", row["mention_brand"])
            row["our_brand_recommended"] = llm_result.get("our_brand_recommended", row["our_brand_recommended"])
            row["our_brand_rank"] = llm_result.get("our_brand_rank")
            row["our_brand_top1"] = llm_result.get("our_brand_top1", row["our_brand_top1"])
            row["our_brand_top3"] = llm_result.get("our_brand_top3", row["our_brand_top3"])
            row["sentiment_to_brand"] = llm_result.get("our_brand_sentiment")
            llm_evidence = llm_result.get("evidence_type")
            if llm_evidence and llm_evidence not in {"unknown", "null", None}:
                row["evidence_type"] = llm_evidence
            row["competitor_mentioned"] = ", ".join(mentioned_competitors or competitor_mentions)
            row["recommended_competitors"] = ", ".join(recommended_competitors)
            row["top1_brand"] = llm_result.get("top1_brand") or (top_exposed[0] if top_exposed else "")
            row["final_recommendation"] = llm_result.get("final_recommendation", "")
            row["target_competitor_mentioned"] = llm_result.get(
                "target_competitor_mentioned", row["target_competitor_mentioned"]
            )
            row["target_competitor_recommended"] = llm_result.get(
                "target_competitor_recommended", row["target_competitor_recommended"]
            )
            row["target_competitor_rank"] = llm_result.get("target_competitor_rank")
            row["target_competitor_top1"] = llm_result.get(
                "target_competitor_top1", row["target_competitor_top1"]
            )
            row["clarification_request"] = llm_result.get(
                "clarification_request", "N"
            )
            row["off_topic"] = llm_result.get("off_topic", "N")

            if row["our_brand_rank"] is None:
                row["our_brand_rank"] = infer_rank_from_list(brand["brand_name"], top_exposed)
            if row["target_competitor_rank"] is None:
                row["target_competitor_rank"] = infer_rank_from_list(target_competitor, top_exposed)
            if row["our_brand_rank"] == 1:
                row["our_brand_top1"] = "Y"
            if isinstance(row["our_brand_rank"], int) and row["our_brand_rank"] <= 3:
                row["our_brand_top3"] = "Y"
            if row["target_competitor_rank"] == 1:
                row["target_competitor_top1"] = "Y"
        elif client:
            row["parse_failed"] = "Y"
            parse_fail_count += 1

        # 응답 본문 시그널과 교차 검증해 LLM over-claim 다운그레이드
        downgrades = post_validate(row, text)
        for d in downgrades:
            downgrade_counts[d] += 1
        if row["evasion"] == "Y":
            evasion_count += 1

        row["win_loss_draw"] = determine_win_loss_draw(row, brand)
        row["surfacing_outcome"] = determine_surfacing_outcome(row)
        parsed.append(row)
        print("OK" if not (client and not llm_result) else "FALLBACK")

    if parse_fail_count > 0:
        print(
            f"\n⚠️  LLM 파싱이 {parse_fail_count}/{len(responses)}건 실패. "
            f"text-match 결과만 사용 (mention 정확도는 유지, recommendation/rank는 부정확할 수 있음).",
        )

    # Post-validation 다운그레이드 리포트
    if downgrade_counts or evasion_count:
        print("\n" + "=" * 60)
        print("Post-validation 다운그레이드 (LLM over-claim 보정)")
        print("=" * 60)
        print(f"회피 답변(evasion=Y) 감지: {evasion_count}/{len(responses)}건 ({evasion_count/max(len(responses),1)*100:.1f}%)")
        if downgrade_counts:
            print("다운그레이드 내역:")
            for reason, cnt in sorted(downgrade_counts.items(), key=lambda x: -x[1]):
                print(f"  - {reason}: {cnt}건")
        print("=" * 60)

    return parsed


def save_parsed(parsed: List[Dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = [
        "prompt_id",
        "run_number",
        "category_code",
        "category",
        "subcategory",
        "target_competitor",
        "mention_brand",
        "our_brand_recommended",
        "our_brand_rank",
        "our_brand_top1",
        "our_brand_top3",
        "sentiment_to_brand",
        "evidence_type",
        "competitor_mentioned",
        "recommended_competitors",
        "top1_brand",
        "final_recommendation",
        "target_competitor_mentioned",
        "target_competitor_recommended",
        "target_competitor_rank",
        "target_competitor_top1",
        "win_loss_draw",
        "surfacing_outcome",
        "response_preview",
        "cited_domains",
        "parse_failed",
        "evasion",
        "clarification_request",
        "off_topic",
    ]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed)


def print_summary(parsed: List[Dict], brand: Dict) -> None:
    print("\n" + "=" * 60)
    print(f"GEO 감사 결과 요약 — {brand['brand_name']}")
    print("=" * 60)

    neutral_rows = [r for r in parsed if r.get("category_code") == "NEUTRAL"]
    if neutral_rows:
        mentioned = sum(1 for r in neutral_rows if r["mention_brand"] == "Y")
        print(f"NEUTRAL(중립): 언급률 {mentioned / len(neutral_rows) * 100:.1f}% ({mentioned}/{len(neutral_rows)})")

    brand_only_rows = [r for r in parsed if r.get("category_code") == "BRAND_ONLY" and r.get("mention_brand") == "Y"]
    if brand_only_rows:
        pos = sum(1 for r in brand_only_rows if (r.get("sentiment_to_brand") or "") == "positive")
        neu = sum(1 for r in brand_only_rows if (r.get("sentiment_to_brand") or "") == "neutral")
        neg = sum(1 for r in brand_only_rows if (r.get("sentiment_to_brand") or "") == "negative")
        total_bo = len(brand_only_rows)
        print(
            f"BRAND_ONLY(브랜드 지명): 긍정 {pos / total_bo * 100:.1f}% | "
            f"중립 {neu / total_bo * 100:.1f}% | 부정 {neg / total_bo * 100:.1f}%"
        )

    comp_only_rows = [r for r in parsed if r.get("category_code") == "COMP_ONLY"]
    if comp_only_rows:
        surfaced = sum(1 for r in comp_only_rows if r["surfacing_outcome"] == "surfaced")
        co_mentioned = sum(1 for r in comp_only_rows if r["surfacing_outcome"] == "co_mentioned")
        not_surfaced = sum(1 for r in comp_only_rows if r["surfacing_outcome"] == "not_surfaced")
        ranked_our = [r["our_brand_rank"] for r in comp_only_rows if isinstance(r.get("our_brand_rank"), int)]
        avg_rank = round(sum(ranked_our) / len(ranked_our), 2) if ranked_our else None
        print(
            f"COMP_ONLY(경쟁사 대안): 대안 소환 {surfaced / len(comp_only_rows) * 100:.1f}% | "
            f"공동 언급 {co_mentioned / len(comp_only_rows) * 100:.1f}% | "
            f"미노출 {not_surfaced / len(comp_only_rows) * 100:.1f}%"
            + (f" | 평균 순위 {avg_rank}" if avg_rank is not None else "")
        )

    h2h_rows = [r for r in parsed if r.get("category_code") == "H2H"]
    if h2h_rows:
        wins = sum(1 for r in h2h_rows if r["win_loss_draw"] == "win")
        losses = sum(1 for r in h2h_rows if r["win_loss_draw"] == "loss")
        draws = sum(1 for r in h2h_rows if r["win_loss_draw"] == "draw")
        total_h2h = wins + losses + draws
        if total_h2h:
            print(
                f"H2H(직접 비교): 승률 {wins / total_h2h * 100:.1f}% | "
                f"무 {draws / total_h2h * 100:.1f}% | 패 {losses / total_h2h * 100:.1f}%"
            )

    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="GEO Response Parser")
    parser.add_argument(
        "--brand",
        required=True,
        help="brand_config.json 경로 (예: brands/bodydoctor/brand_config.json)",
    )
    args = parser.parse_args()

    brand = load_brand_config(args.brand)
    brand_dir = os.path.dirname(args.brand)
    raw_responses_file = os.path.join(brand_dir, "results", "raw_responses.json")
    parsed_results_file = os.path.join(brand_dir, "results", "parsed_results.csv")

    if not os.path.exists(raw_responses_file):
        print(f"{raw_responses_file} 파일이 없습니다. 03_run_audit.py를 먼저 실행하세요.")
        return

    responses = load_responses(raw_responses_file)
    print(f"응답 {len(responses)}건 로드 완료")

    use_llm = bool(ANTHROPIC_API_KEY) and not ANTHROPIC_API_KEY.startswith("sk-ant-...")
    if not use_llm:
        print("ANTHROPIC_API_KEY 미설정 → 텍스트 매칭만 사용 (추천률/순위 일부 정확도 낮음)")
    else:
        print(f"파싱 모델: {CLAUDE_MODEL} (prompt caching 적용)")

    parsed = parse_all(responses, brand, use_llm=use_llm)
    save_parsed(parsed, parsed_results_file)
    print(f"\n파싱 결과 저장 → {parsed_results_file}")

    # 분류기 스펙 공개 — 외부 감사/재현 가능성을 위해 실제 사용 중인
    # 시스템 프롬프트와 스키마를 JSON으로 덤프한다.
    competitors = get_competitors(brand)
    spec_file = os.path.join(brand_dir, "results", "classifier_spec.json")
    spec = {
        "classifier_model": CLAUDE_MODEL if use_llm else None,
        "classifier_mode": "llm_structured_output" if use_llm else "text_matching_only",
        "sentiment_classes": {
            "positive": "명시적 긍정 표현 (탁월한, 효과 좋다, 강력 추천 등)",
            "neutral": "단순 정보 제공, 중립 비교, 사용법 안내",
            "negative": "단점/권장하지 않음/주의 경고/효과 미미",
            "null": "우리 브랜드가 응답에 미언급",
        },
        "known_biases": [
            "보수적 기본값 — 애매한 언급은 neutral로 분류(긍정·부정 모두 강한 시그널 필요)",
            "권위 인용('리스테린은 FDA 승인')을 positive가 아니라 neutral로 취급",
            "confidence 점수 없음 — 분류기 불확실성 노출 불가",
        ],
        "output_schema": ParseResult.model_json_schema(),
        "system_prompt": build_parse_system(brand, competitors),
    }
    with open(spec_file, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    print(f"분류기 스펙 저장 → {spec_file}")

    print_summary(parsed, brand)


if __name__ == "__main__":
    main()
