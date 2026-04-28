"""
GEO 진단셋 생성기 (rev 3 — 브랜드 공통 재사용형 최소 구조)

brand_config.json 만 읽어 다음 4개 카테고리로 프롬프트를 생성한다.

    NEUTRAL     75  (브랜드/경쟁사 모두 비언급)
    H2H         30  (자사 + 경쟁사 동시 지명 비교)
    COMP_ONLY   30  (경쟁사 단독 지명)
    BRAND_ONLY  15  (자사 단독 지명)
    ─────────────
    총         150

경쟁사 정보는 모두 brand_config.json에서 읽어오며 코드에 하드코딩하지 않는다.
sub_angle 개념 및 keywords.json 의존은 제거되었다. CSV의 `sub_angle` 컬럼은
하위 호환을 위해 남겨두되 항상 빈 문자열이다.

사용법:
  python 02_generate_prompts.py --brand brands/bodydoctor_k/brand_config.json
"""

import argparse
import csv
import json
import os
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

# ──────────────────────────────────────────────────────────────────────
# 카테고리 정의
# ──────────────────────────────────────────────────────────────────────

DEFAULT_CATEGORY_TARGETS = {
    "NEUTRAL":    93,  # 기존 75 + PRC/USE/DEC 서브카테고리 18개 신규
    "H2H":        30,
    "COMP_ONLY":  30,
    "BRAND_ONLY": 15,
}
DEFAULT_COMPETITOR_LIMIT = 5

CATEGORY_LABELS = {
    "NEUTRAL":    "중립",
    "H2H":        "직접 비교",
    "COMP_ONLY":  "경쟁사 대안",
    "BRAND_ONLY": "브랜드 지명",
}

# NEUTRAL 내부 서브분류 (코드, 라벨, 할당, 각도 설명)
# 코드는 prompts.csv의 subcategory 필드로 전파된다 — 대시보드에서 분리 집계.
# CAT: 카테고리 일반 / SYM: 증상·상황 / ALT: 솔루션 대안 비교
# PRC: 가격 / USE: 유스케이스 / DEC: 구매의도 단일 선택
NEUTRAL_ANGLES = [
    ("CAT", "카테고리 일반", 57,
     "소비자가 이 카테고리에서 '무엇을 살지' 판단을 구하는 질문. "
     "다음 축이 고르게 섞이도록: 입문자 선택, 가성비, 사용 편의성, 조용함, "
     "집에서 혼자 사용, **제품 설명에 명시된 핵심 효용·목적 축에 직결된 것만** "
     "(예: 해당 카테고리가 직접 해결하는 문제/목적만 다룰 것. "
     "카테고리와 거리 먼 주제 — 예: 이 제품이 케겔 힙머신이면 '뱃살·전신 다이어트', "
     "구강청결제면 '치과 치료·잇몸 시술' 등 — 은 금지), "
     "꾸준함/의지 부족 고민, 부모님·선물 상황, '내 상황에 맞는지' 탐색 맥락. "
     "'선물/어머니/시어머니/이모/생일' 같은 선물 맥락은 전체의 20% 이하로 제한할 것."),
    ("SYM", "증상/상황형", 8,
     "일상 불편·증상을 겪는 화자가 그 문제를 **집에서 어떻게 해결·완화할지** 묻는 "
     "해결 탐색형 질문. '이 증상이 뭐야?', '왜 이래?' 같은 의료 상담·진단형 금지. "
     "'집에서 해볼 만한 거', '도움 되는 거', '뭘 해야 하지' 같은 해결 지향 표현을 쓸 것."),
    ("ALT", "솔루션 대안 비교", 10,
     "해당 제품 카테고리와 다른 해결 방식(운동, 시술, 앱, PT 등) 사이에서 "
     "'결국 뭘 선택할지' 고민하는 질문. 'A 할까 B 할까', 'A가 나아 B가 나아' 프레임."),
    ("PRC", "가격 기반", 6,
     "예산·가격대·가성비 관점에서 제품을 고르려는 질문. "
     "'1만원대로', '5만원 이하', '비싼 거', '할인 자주 하는', '가성비 좋은' 같은 "
     "가격·예산 시그널을 반드시 포함할 것. 제품 자체 카테고리는 유지."),
    ("USE", "유스케이스", 6,
     "특정 상황·시간·장소·대상에서 쓸 용도로 제품을 찾는 질문. "
     "'출근 전에', '여행 갈 때', '사무실에서', '저녁에만', '아이도 쓸 수 있는', "
     "'휴대용으로' 같은 구체적 사용 맥락 시그널을 반드시 포함할 것."),
    ("DEC", "구매의도 단일선택", 6,
     "여러 후보 중 **딱 하나**만 꼽아달라는 결정형 질문. "
     "'하나만 추천', '단 하나만', '딱 한 개만', '베스트 1개', '지금 바로 살 거' 같은 "
     "단일 선택 시그널을 반드시 포함할 것. 복수 추천·비교·설명 요청 금지."),
]

# 범용 fallback 페르소나 — brand_config.json의 `personas` 가 없을 때만 사용.
# 도메인 특화 페르소나(예: "40대 산후 5년차")는 brand_config에 정의해야
# 페르소나 주입 효과가 정상적으로 나옴.
DEFAULT_PERSONAS = [
    {"id": "p1", "desc": "30대 직장인, 시간 부족, 가성비 중시"},
    {"id": "p2", "desc": "40대 가족 구성원, 가족과 함께 쓸 제품 고민"},
    {"id": "p3", "desc": "20대 입문자, 자극 적고 무난한 선택 선호"},
    {"id": "p4", "desc": "1인 가구 거주자, 집에서 혼자 사용, 사용 편의성 중시"},
    {"id": "p5", "desc": "50-60대 어른 선물 구매자, 사용 간편함 우선"},
]


def get_personas(brand: Dict) -> List[Dict]:
    """brand_config.personas 가 있으면 그것을, 없으면 DEFAULT_PERSONAS 사용."""
    bp = brand.get("personas")
    if isinstance(bp, list) and bp:
        out = []
        for p in bp:
            if isinstance(p, dict) and p.get("desc"):
                out.append({"id": str(p.get("id", "")), "desc": str(p["desc"])})
        if out:
            return out
    return DEFAULT_PERSONAS

# 품질 필터 파라미터 — 페르소나·조건 주입으로 길이가 늘어남 (v2.1 평균 ≈ 60자)
LENGTH_MIN = 20        # 공백 제외 최소
LENGTH_MAX = 130       # 공백 제외 최대
OVERSAMPLE_RATIO = 1.5 # 오버샘플링 배수 (필터 drop 대비)
MAX_RETRY = 1          # 목표 미달 시 추가 생성 횟수

ALLOWED_TAIL_TOKENS = [
    "지", "야", "까", "네", "어", "나", "해",
    "추천", "뭐", "뭐야", "어때", "있어", "있음",
    "됨", "가능", "궁금", "고민", "고민중",
]

FORMAL_TOKENS = ["습니다", "십시오", "바랍니다", "주세요", "주실", "알려주세요"]


# ──────────────────────────────────────────────────────────────────────
# 각도별 few-shot + anti-example (브랜드/경쟁사명 포함하지 않는 범용 예시)
# ──────────────────────────────────────────────────────────────────────

# NEUTRAL 서브분류별 few-shot (브랜드·경쟁사명 포함 금지 — NEUTRAL 규칙)
# 키는 subcategory 코드 (CAT/SYM/ALT/PRC/USE/DEC)
# 브랜드·도메인 무관 few-shot — 페르소나·조건 주입 패턴만 가르침.
# 도메인 단어는 "이런 거", "그 중에" 같은 지시대명사로 대체해 일반화.
NEUTRAL_FEW_SHOTS = {
    "CAT": [
        "40대 출산 경험 있는데 처음 써보려고. 너무 어렵지 않을까?",
        "30대 직장인인데 매일 운동할 시간이 없어. 사무실에서 앉아서만 하는 거 있어?",
        "아파트라 층간소음 신경 쓰여. 그 중에 소음 적은 거로 고를 만한 게 있나?",
        "30대 후반 1인 가구야. 집에서 혼자 조용히 쓸 만한 거 뭐 있어?",
        "40대인데 둘째 낳고 5년 됐어. 혼자 집에서 쓸 수 있는 거 뭐 없을까?",
        "50대 어머니 선물로 사려는데 사용 간편한 거 추천해줘.",
    ],
    "SYM": [
        "40대 여성인데 (증상)이 신경 쓰여. 집에서 해볼 만한 게 있어?",
        "30대 후반인데 (불편 증상)이 있어. 집에서 꾸준히 할 수 있는 게 뭐 있을까?",
        "50대인데 (생활 불편) 때문에 일상이 불편해. 집에서 개선해볼 수 있는 방법이 있어?",
        "둘째 낳고 6개월 됐는데 (산후 증상)이 안 돌아와. 운동 말고 도움 되는 거 있어?",
    ],
    "ALT": [
        "40대 산후 케어, 운동 따로 할지 기기 살지 고민 중이야.",
        "30대인데 PT 다닐지 집에서 기기 살지 고민 중. 비용 비슷해.",
        "병원 가서 시술 받을지 집에서 기기로 해결할지 결정 못 하겠어.",
        "앱이랑 기기 중에 효과 차이가 어느 정도야? 30대 직장인 기준으로.",
    ],
    "PRC": [
        "30대 직장인이고 예산 30만원 이내인데 가성비 좋은 거 뭐 있어?",
        "50만원 이상 비싼 게 진짜 그 값을 한다고 생각해? 가성비로 따지면 어때?",
        "20만원대로 살 만한 입문용 추천해줘. 매일 쓸 거야.",
        "40대 산후 케어용으로 가성비 따지면 어느 가격대 제품이 만족도 높아?",
    ],
    "USE": [
        "30대 직장인이고 출근 전 10분만 쓸 건데 적당한 거 있어?",
        "재택근무자라 집에서 하루 5시간 이상 쓸 건데 뭐 추천해?",
        "여행 갈 때도 챙기기 편한 휴대용 있을까? 30대 1인 가구야.",
        "퇴근 후 저녁에만 1시간 정도 쓸 건데 30대 여성에게 맞는 거 뭐 있어?",
    ],
    "DEC": [
        "40대 산후 5년차, 예산 50만원으로 딱 하나만 추천해줘.",
        "30대 직장인 기준 베스트 1개만 알려줘.",
        "고민할 시간 없는데 30대 여성한테 하나만 골라줘.",
        "지금 바로 살 거 하나만 뽑아줘. 50대 어머니 선물용으로.",
    ],
}

# 각 서브분류에서 피해야 할 다른 서브분류의 패턴 (침범 방지)
NEUTRAL_ANTI = {
    "CAT": [
        '"이 증상 왜 생겨?" (→ SYM 에서)',
        '"A 할까 B 할까" 솔루션 대안 (→ ALT 에서)',
        '"1만원대" / "예산 얼마" 등 가격 시그널 (→ PRC 에서)',
        '"출근 전" / "여행 갈 때" 등 구체 상황 (→ USE 에서)',
        '"딱 하나만" / "베스트 1개" (→ DEC 에서)',
        '"선물/어머니/시어머니"가 전체의 20% 넘게 나오지 말 것',
    ],
    "SYM": [
        '"OO 추천해줘" / "입문용 뭐가 좋아?" (→ CAT 에서)',
        '"이게 무슨 증상이야?" / "왜 이래?" 같은 진단·상담형 금지',
        '증상 자체를 묻는 것이 아니라 "그 문제를 집에서 어떻게 해결할지"를 물을 것',
    ],
    "ALT": [
        '"OO 추천해줘" (→ CAT 에서)',
        '증상 묘사 중심 질문 (→ SYM 에서)',
        '제품 내 선택 (→ CAT/DEC 에서). 여기선 제품 vs 비제품(운동/시술/앱) 프레임만',
    ],
    "PRC": [
        '가격·예산 언급 없는 일반 추천 (→ CAT 에서)',
        '"출근 전에" 같은 시간·상황 중심 (→ USE 에서)',
        '반드시 만원/할인/가성비/저렴/예산 같은 가격 시그널이 들어가야 함',
    ],
    "USE": [
        '"입문자", "가성비" 같은 일반 맥락 (→ CAT 에서)',
        '"1만원대" 같은 가격 중심 (→ PRC 에서)',
        '반드시 시간/장소/대상(아이/부모/출근/여행 등) 중 하나가 구체적으로 들어가야 함',
    ],
    "DEC": [
        '"뭐 있어?" / "추천해줘" 복수 추천 (→ CAT 에서)',
        '비교·설명을 요구하는 질문 금지',
        '반드시 "하나만"/"단 하나"/"딱 1개" 등 단일 선택 시그널이 들어가야 함',
    ],
}


def build_few_shot_block(examples: List[str]) -> str:
    """Few-shot 예시 블록 문자열 생성."""
    if not examples:
        return ""
    lines = ["=== 좋은 예시 (이번 각도의 톤) ==="] + [f'- "{e}"' for e in examples]
    return "\n".join(lines)


def build_anti_example_block(anti: List[str]) -> str:
    """다른 각도와의 혼동 방지용 anti-example 블록."""
    if not anti:
        return ""
    lines = ["=== 이번 각도에서 피할 것 (다른 배치에서 생성됨) ==="] + [f"- {e}" for e in anti]
    return "\n".join(lines)


def h2h_few_shots(brand_name: str, competitor: str, product_category: str = "") -> List[str]:
    """H2H — 페르소나 + 카테고리 단어 + 기간/조건이 박힌 v2.1 스타일.

    위치 편향(position bias) 방지: 자사-먼저 / 경쟁사-먼저 예시를 번갈아 배치.
    카테고리 단어는 product_category 또는 일반 표현으로 비교어 직전에 명시.
    """
    cat = product_category.strip() or "이 카테고리 제품"
    return [
        # 자사-먼저 (페르소나·기간·조건 주입)
        f"40대 산후 5년차, 예산 50만원 이내로 {cat} 사려는데 {brand_name}이랑 {competitor} 중 뭐 살지 진짜 고민 중이야",
        f"{cat} 처음 사는 30대 초보자가 사기엔 {brand_name}이랑 {competitor} 중에 어디가 낫지?",
        f"30대 재택근무자야. 집에서 하루 5시간 이상 쓸 거면 {brand_name}이랑 {competitor} 중 뭐가 더 편해?",
        f"민감성 피부에 알러지 있는 편인데 {brand_name}이랑 {competitor} 중에 어디가 자극이 덜해?",
        # 경쟁사-먼저
        f"{competitor} 1년 쓰다가 {brand_name}으로 바꾸려는데 적응 어렵지 않을까? 40대야",
        f"50대 어머니 선물용으로 {cat} 사려는데 {competitor}이랑 {brand_name} 중에 어디가 사용이 간편할까?",
        f"30대 직장인 기준 ml당/원당 가성비 따지면 {competitor}이랑 {brand_name} 중 어디가 나아?",
        f"{competitor} 6개월 이상 써본 사람이 {brand_name}으로 갈아탔다면 뭐가 더 좋다고 해?",
    ]


H2H_ANTI = [
    '"가격 차이 얼마나 나?" 단순 속성 조회형',
    '"사용법 어떻게 달라?" / "출력 세기 차이?" 속성 나열형',
    '"후기 비교해줘" 단순 정보 요약형',
    '속성 비교형은 전체의 30%까지만. 핵심은 "그래서 뭐 살 건데?"',
]


def comp_only_few_shots(competitor: str, product_category: str = "") -> List[str]:
    """COMP_ONLY — 페르소나 + 카테고리 단어 + 가격대/기간 박힌 v2.1 스타일."""
    cat = product_category.strip() or "이 카테고리"
    return [
        f"30대 직장인 여성인데 {competitor} 외에 홈트레이닝으로 쓸 만한 {cat} 뭐 있어?",
        f"{competitor} 30만원대인데 비슷한 가격대 다른 {cat} 또 있어?",
        f"40대 산후 케어용으로 {competitor} 말고 집에서 쓰기 좋은 {cat} 또 뭐 있어?",
        f"{competitor} 1년 쓰다가 효과 약해. 더 강력한 {cat}로 갈아탈 만한 거 뭐야?",
        f"{competitor} 사려다가 고민 중인 30대 여성인데 동급 {cat} 후기 신뢰할 만한 거 어디야?",
        f"{competitor} 후기 봤는데 가격이 비슷한 다른 {cat} 또 보고 싶어. 40대 기준으로.",
    ]


COMP_ONLY_ANTI = [
    '"단점이 뭐야?" / "안 좋은 점이 뭐가 있어?" 경쟁사 검증형',
    '"효과 진짜야?" / "리뷰 믿어도 돼?" 리뷰 진위 확인형',
    '검증형 질문은 전체의 20%까지만. 핵심은 "다른 선택지로 갈아탈지"',
    '자사 제품의 차별 기능을 전제로 한 유도형 금지: '
    '"자동으로 되는 거 또 있어?", "비침습 방식인 거 있어?", '
    '"특정 기술 방식이 있는 거" 처럼 답을 정해놓고 묻는 질문은 소수만.',
]


def brand_only_few_shots(brand_name: str) -> List[str]:
    """BRAND_ONLY — 시간/연령/가격 등 구체 차원이 박힌 v2.1 스타일."""
    return [
        f"{brand_name} 살 만해? 6개월 이상 써본 사람들 실제 반응이 어때?",
        f"{brand_name} 구매 후 3개월 안에 후회한 사람 있어? 솔직한 후기 좀 알려줘",
        f"{brand_name} 어떤 연령대, 어떤 목적의 사람들이 가장 만족하는 것 같아?",
        f"{brand_name} 가격이 비싼 편인데 효과 대비 만족도가 어때? 1년 이상 사용 기준으로",
        f"{brand_name} 30대 직장인이 매일 쓰기에 적합한 편이야?",
        f"{brand_name} 지금 사도 괜찮은 시기야? 신모델 출시 임박했다거나 그런 건 없어?",
        f"{brand_name} 구매 전에 체형, 사용 환경, 증상 중에 뭘 가장 먼저 확인해야 해?",
    ]


BRAND_ONLY_ANTI = [
    '"부작용 없어?" / "얼마나 써야 효과 있어?" 사용법·안전 FAQ형',
    '"세탁은 어떻게?" / "임산부도 써도 돼?" 단순 FAQ형',
    'FAQ형 질문은 전체의 20%까지만. 핵심은 "살 만한가/누구한테 맞나/후회 없는 선택인가"',
]


# ──────────────────────────────────────────────────────────────────────
# 프롬프트 생성 템플릿 (단일)
# ──────────────────────────────────────────────────────────────────────

GEN_TEMPLATE = """당신은 한국 소비자가 ChatGPT에 직접 입력할 법한 자연스러운 질문을 생성하는 작가다.

브랜드: {brand_name} ({product_category})
제품 설명: {product_description}

이번 배치 유형: {category_label}
{category_specific_rules}

=== 최우선 원칙 (모든 카테고리 공통) ===
1. 단순 **정보 조회형**(속성·원리·사용법·부작용·후기 진위 같은 "알려줘" 류)보다,
   **구매 판단형 질문**(무엇을 고를지/바꿀지/추천받을지/살지 말지 판단하려는 의도)을
   우선해서 생성해라. 정보만 묻는 질문은 전체의 소수에만 포함.
2. 질문은 실제 구매·선택·대안 탐색 상황을 반영할 것.
   **특정 기능/속성을 과도하게 유도하는 질문**은 전체의 **20%를 넘기지 말 것**:
   - 브랜드의 차별 기능(예: 자동/비침습/EMS/찌꺼기 응고 같은 구체 기술·메커니즘)을
     미리 안다는 듯 "~되는 거 또 있어?"라고 묻는 유도형
   - 제품 설명을 복붙한 것처럼 느껴지는 질문
   - 답(특정 브랜드)을 정해놓고 묻는 것처럼 보이는 질문
3. 각 카테고리에서 질문은 **구매 판단, 대안 탐색, 추천 요청**을 우선하고,
   **세부 사양·사용법·기능 문의**(사용 시간, 충전 방식, 타이머 같은 특정 기능,
   호환성, 적응 기간 등)는 전체의 **15%를 넘기지 말 것**.

{persona_section}이번 배치에서 다룰 각도: {angle_hint}

=== 페르소나·상황 강제 주입 (가장 중요) ===

각 질문은 **다음 3요소를 자연스럽게 포함**해야 한다. 단순 추천 요청만으로 끝나면 안 된다.

1. **화자 정체성 (페르소나)** — 위 페르소나 정보를 그대로 말하듯 노출
   ✓ 좋은 예: "30대 직장인인데", "40대 출산 5년차야", "1인 가구라", "60대 어머니 선물용으로"
   ✗ 나쁜 예: "초보자가" (너무 일반), 페르소나 정보 누락 (제일 흔한 실패)

2. **구체 조건** — 다음 중 **최소 1가지**를 명시 (모호한 추상화 금지)
   - 기간: "1년 썼는데", "6개월 이상 쓸 거면", "산후 5년차"
   - 예산/가격: "30만원대", "예산 50만원 이내", "ml당 가격"
   - 시간/장소: "출근 전 1분", "사무실에서", "집에서 5시간 이상", "아파트라"
   - 신체·생활 조건: "민감성 피부인데", "둘째 낳고", "가벼운 요실금"

3. **제품 카테고리 단어** — 제품 카테고리("{product_category}") 또는 그 핵심 단어
   - H2H/COMP_ONLY: 비교어/대상명 직전에 카테고리 단어 **반드시** 명시 (예: "골반저근 EMS 케겔 운동기 X랑 Y 중에...")
   - NEUTRAL: 자연스러우면 추가 (필수 아님 — 의도된 open-ended OK)
   - BRAND_ONLY: 브랜드명만으로 충분, 대신 시간/연령대/가격 차원을 추가

❌ 나쁜 예 (페르소나·조건 다 빠짐):
- "케겔 운동 기기 처음 사는데 뭐 봐야 해?"
- "바디닥터K랑 이지케이 중에 뭐가 더 나아?"

✅ 좋은 예 (페르소나 + 조건 + 카테고리 자연스럽게 박힘):
- "40대 출산 경험 있는데 케겔운동 기계 처음 써보려고. 너무 어렵지 않을까?"
- "40대 산후 5년차, 예산 50만원 이내로 골반저근 EMS 케겔 운동기 사려는데 바디닥터K이랑 이지케이 중 뭐 살지 진짜 고민 중이야"
- "30대 재택근무자야. 골반저근 EMS 케겔 운동기 사려는데 집에서 하루 5시간 이상 쓰려고 해."

{few_shot_block}
{anti_example_block}
=== 공통 나쁜 예시 (이런 톤 금지) ===
- "여성 건강 기기에 대해 알려주세요" (추상적, 교과서 톤)
- "기술의 원리는 무엇인가요?" (AI에 이렇게 안 물음)
- "효과적인 제품을 추천해 주시기 바랍니다" (격식체)

=== 절대 규칙 ===
- 각 질문은 25~120자 정도의 자연스러운 한국어 구어체일 것 (페르소나·조건 박으면 길어진다)
- 반말 또는 친근한 톤, 존댓말 금지
- 마케팅 작문체("효과적인", "혁신적인", "최고의") 금지
- 추상적/교과서식 표현 금지
- {mention_rules}

위 지침에 맞춰 질문을 정확히 {count}개 생성해라.
번호 없이 한 줄에 하나씩만 출력해라.
다른 설명은 절대 쓰지 마라."""


# ──────────────────────────────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────────────────────────────

def load_brand_config(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_audit_settings(brand: Dict) -> Dict:
    s = brand.get("audit_settings", {})
    return s if isinstance(s, dict) else {}


def get_category_targets(brand: Dict) -> Dict[str, int]:
    s = get_audit_settings(brand)
    configured = s.get("category_targets", {}) if isinstance(s.get("category_targets"), dict) else {}
    targets = DEFAULT_CATEGORY_TARGETS.copy()
    for k, v in configured.items():
        if k in targets:
            targets[k] = int(v)
    return targets


def get_competitors(brand: Dict) -> List[Dict]:
    """
    Returns list of competitor dicts with 'name', 'keywords', 'tokens' where
    tokens = [name] + keywords (dedupe preserved).
    """
    s = get_audit_settings(brand)
    limit = int(s.get("competitor_limit", DEFAULT_COMPETITOR_LIMIT) or DEFAULT_COMPETITOR_LIMIT)
    raw = brand.get("competitors", [])
    out = []
    for c in raw:
        if not isinstance(c, dict):
            continue
        name = c.get("name", "").strip()
        if not name:
            continue
        kws = [str(k).strip() for k in (c.get("keywords") or []) if str(k).strip()]
        tokens = [name] + [k for k in kws if k != name]
        out.append({"name": name, "keywords": kws, "tokens": tokens})
    return out[:limit]


def get_competitor_names(brand: Dict) -> List[str]:
    """Backward-compat helper — returns primary names only."""
    return [c["name"] for c in get_competitors(brand)]


def flatten_tokens(competitors: List[Dict]) -> List[str]:
    """모든 경쟁사의 모든 토큰(name + aliases)을 하나의 리스트로."""
    out = []
    for c in competitors:
        out.extend(c["tokens"])
    return out


def get_brand_name_tokens(brand: Dict) -> List[str]:
    tokens = [brand.get("brand_name", "") or "", brand.get("brand_name_en", "") or ""]
    tokens.extend(brand.get("brand_keywords") or [])
    return [t for t in tokens if t]


def normalize_prompt_line(line: str) -> str:
    """Strip number/bullet prefixes only if they form a list marker.

    절대로 본문 첫 단어의 숫자(예: '30대 직장인인데')를 잘라내지 말 것 — 페르소나
    주입 후 자주 발생하는 데이터 손상 원인. '1. ' / '- ' / '* ' 패턴만 제거한다.
    """
    s = line.strip()
    # 1) 숫자.닫는기호 형태의 번호 매김: "1.", "2)", "3 -" 만 제거
    s = re.sub(r'^\s*\d+\s*[\.\)]\s+', "", s)
    # 2) 따옴표 / 불릿 / 별표 / 닫는괄호 같은 leading 토큰만 제거 (digit 절대 포함 X)
    s = re.sub(r'^\s*["\'\-\*\)]+\s*', "", s)
    if s.endswith('"') or s.endswith("'"):
        s = s.rstrip('"\'')
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def split_lines(text: str) -> List[str]:
    out = []
    for raw in text.split("\n"):
        n = normalize_prompt_line(raw)
        if n:
            out.append(n)
    return out


def dedupe_keep_order(prompts: List[str]) -> List[str]:
    """표층 문자열 기준 중복 제거 (대소문자/공백 정규화). 먼저 들어온 게 우선."""
    seen = set()
    out = []
    for p in prompts:
        key = re.sub(r"\s+", "", p.lower())
        if key and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def contains_any(text: str, needles: List[str]) -> bool:
    t = normalize_for_match(text)
    for n in needles:
        if not n:
            continue
        if normalize_for_match(n) in t:
            return True
    return False


def allocate_targets_to(total: int, targets: List[str]) -> Dict[str, int]:
    """총합을 대상 리스트에 균등 분배. 나머지는 앞에서부터 +1."""
    if not targets:
        return {}
    base = total // len(targets)
    remainder = total % len(targets)
    out = {}
    for i, t in enumerate(targets):
        out[t] = base + (1 if i < remainder else 0)
    return out


# ──────────────────────────────────────────────────────────────────────
# LLM 호출
# ──────────────────────────────────────────────────────────────────────

def call_llm(client: Anthropic, prompt: str, max_retries: int = 2) -> str:
    last_err = None
    for _ in range(max_retries + 1):
        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = next((b.text for b in resp.content if b.type == "text"), "").strip()
            if text:
                return text
            last_err = RuntimeError("빈 응답")
        except Exception as e:
            last_err = e
    raise RuntimeError(f"LLM 호출 실패: {last_err}")


# ──────────────────────────────────────────────────────────────────────
# 품질 필터
# ──────────────────────────────────────────────────────────────────────

def ends_with_allowed_tail(text: str) -> bool:
    compact = re.sub(r"[\s!\.\?]+$", "", text).strip()
    for token in ALLOWED_TAIL_TOKENS:
        if compact.endswith(token):
            return True
    return False


def passes_length(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    return LENGTH_MIN <= len(compact) <= LENGTH_MAX


def passes_question_form(text: str) -> bool:
    if "?" in text:
        return True
    return ends_with_allowed_tail(text)


def passes_formality(text: str) -> bool:
    for token in FORMAL_TOKENS:
        if token in text:
            return False
    return True


def passes_brand_rule(
    text: str,
    category_code: str,
    brand_tokens: List[str],
    all_competitor_tokens: List[str],
    target_competitor_tokens: List[str],
) -> bool:
    has_brand = contains_any(text, brand_tokens)
    has_any_comp = contains_any(text, all_competitor_tokens)
    has_target = contains_any(text, target_competitor_tokens) if target_competitor_tokens else False

    if category_code == "NEUTRAL":
        return (not has_brand) and (not has_any_comp)
    if category_code == "H2H":
        return has_brand and has_target
    if category_code == "COMP_ONLY":
        return has_target and (not has_brand)
    if category_code == "BRAND_ONLY":
        return has_brand and (not has_any_comp)
    return True


def apply_filters(
    candidates: List[str],
    category_code: str,
    brand_tokens: List[str],
    all_competitor_tokens: List[str],
    target_competitor_tokens: List[str],
) -> Dict:
    """필터를 순서대로 적용하고 단계별 drop 카운트 + 통과 리스트 반환."""
    drops = {"length": 0, "formality": 0, "question_form": 0, "brand_rule": 0, "dup": 0}
    survivors: List[str] = []

    for c in candidates:
        if not passes_length(c):
            drops["length"] += 1
            continue
        if not passes_question_form(c):
            drops["question_form"] += 1
            continue
        if not passes_formality(c):
            drops["formality"] += 1
            continue
        if not passes_brand_rule(c, category_code, brand_tokens, all_competitor_tokens, target_competitor_tokens):
            drops["brand_rule"] += 1
            continue
        survivors.append(c)

    before_dedupe = len(survivors)
    survivors = dedupe_keep_order(survivors)
    drops["dup"] = before_dedupe - len(survivors)

    return {"survivors": survivors, "drops": drops}


# ──────────────────────────────────────────────────────────────────────
# 배치 생성 (단일 API 호출 단위)
# ──────────────────────────────────────────────────────────────────────

def build_prompt_message(
    *,
    brand: Dict,
    category_label: str,
    persona_desc: str,
    angle_hint: str,
    mention_rules: str,
    count: int,
    category_specific_rules: str,
    few_shot_block: str,
    anti_example_block: str,
) -> str:
    persona_section = (
        f"화자 페르소나: {persona_desc}\n" if persona_desc else ""
    )
    return GEN_TEMPLATE.format(
        brand_name=brand.get("brand_name", ""),
        product_category=brand.get("product_category", ""),
        product_description=brand.get("product_description", ""),
        category_label=category_label,
        category_specific_rules=category_specific_rules,
        persona_section=persona_section,
        angle_hint=angle_hint,
        mention_rules=mention_rules,
        count=count,
        few_shot_block=few_shot_block,
        anti_example_block=anti_example_block,
    )


def generate_batch(
    client: Anthropic,
    brand: Dict,
    *,
    category_code: str,
    target_count: int,
    angle_hint: str,
    mention_rules: str,
    persona_desc: str,
    target_competitor: str,
    category_specific_rules: str,
    label_for_log: str,
    brand_tokens: List[str],
    all_competitor_tokens: List[str],
    target_competitor_tokens: List[str],
    few_shot_examples: List[str],
    anti_examples: List[str],
) -> Dict:
    """오버샘플링 → LLM 호출 → 품질 필터 적용. 목표 미달 시 최대 MAX_RETRY 재시도."""
    collected: List[str] = []
    total_drops = {"length": 0, "formality": 0, "question_form": 0, "brand_rule": 0, "dup": 0}
    raw_generated = 0

    for attempt in range(MAX_RETRY + 1):
        needed = target_count - len(collected)
        if needed <= 0:
            break
        ask = max(1, int(round(needed * OVERSAMPLE_RATIO)))

        message = build_prompt_message(
            brand=brand,
            category_label=CATEGORY_LABELS[category_code],
            persona_desc=persona_desc,
            angle_hint=angle_hint,
            mention_rules=mention_rules,
            count=ask,
            category_specific_rules=category_specific_rules,
            few_shot_block=build_few_shot_block(few_shot_examples),
            anti_example_block=build_anti_example_block(anti_examples),
        )
        if attempt > 0 and collected:
            message += "\n\n[이미 만든 질문 — 중복·유사 금지]\n" + "\n".join(
                f"- {q}" for q in collected[-15:]
            )

        try:
            content = call_llm(client, message)
        except Exception as e:
            print(f"  [LLM retry failed: {str(e)[:60]}]", flush=True)
            continue

        candidates = split_lines(content)
        raw_generated += len(candidates)
        result = apply_filters(
            candidates,
            category_code=category_code,
            brand_tokens=brand_tokens,
            all_competitor_tokens=all_competitor_tokens,
            target_competitor_tokens=target_competitor_tokens,
        )
        for key in total_drops:
            total_drops[key] += result["drops"][key]

        # 이전 수집분과 중복 제거
        combined = dedupe_keep_order(collected + result["survivors"])
        added_this_round = len(combined) - len(collected)
        total_drops["dup"] += (len(result["survivors"]) - added_this_round)
        collected = combined

    # 목표 초과분은 앞에서부터 자름
    final = collected[:target_count]

    print(
        f"[{category_code}/{label_for_log}] requested={target_count}, "
        f"raw_generated={raw_generated}, "
        f"dropped(length)={total_drops['length']}, "
        f"dropped(question_form)={total_drops['question_form']}, "
        f"dropped(formality)={total_drops['formality']}, "
        f"dropped(brand_rule)={total_drops['brand_rule']}, "
        f"dropped(dup)={total_drops['dup']}, "
        f"final={len(final)}"
    )
    if len(final) < target_count:
        print(f"  ⚠️  목표 미달: {target_count - len(final)}개 부족")
    return {"prompts": final, "drops": total_drops}


# ──────────────────────────────────────────────────────────────────────
# 카테고리별 mention_rules / specific_rules
# ──────────────────────────────────────────────────────────────────────

def _alias_hint(aliases: List[str]) -> str:
    """별칭이 있으면 LLM에 짧게 써도 된다고 안내."""
    short = [a for a in aliases if a][:3]
    if not short:
        return ""
    return f" (짧게 '{short[0]}'" + (f" 또는 '{short[1]}'" if len(short) > 1 else "") + " 같은 형태로 써도 OK)"


def mention_rules_for(
    category_code: str,
    brand_name: str,
    target_competitor: str,
    target_aliases: List[str],
    all_competitor_names: List[str],
) -> str:
    if category_code == "NEUTRAL":
        comp_joined = ", ".join(all_competitor_names) if all_competitor_names else "(없음)"
        return (
            f"자사 브랜드명('{brand_name}')과 모든 경쟁사명({comp_joined}) "
            f"및 그 별칭/약칭을 절대 포함하지 말 것"
        )
    if category_code == "H2H":
        hint = _alias_hint(target_aliases)
        return (
            f"자사 브랜드명('{brand_name}')과 타깃 경쟁사('{target_competitor}'{hint})를 "
            f"반드시 모두 포함할 것"
        )
    if category_code == "COMP_ONLY":
        hint = _alias_hint(target_aliases)
        return (
            f"타깃 경쟁사('{target_competitor}'{hint})를 반드시 포함하고, "
            f"자사 브랜드명('{brand_name}')은 절대 포함하지 말 것"
        )
    if category_code == "BRAND_ONLY":
        comp_joined = ", ".join(all_competitor_names) if all_competitor_names else "(없음)"
        return (
            f"자사 브랜드명('{brand_name}')을 반드시 포함하고, "
            f"경쟁사명({comp_joined}) 및 그 별칭을 절대 포함하지 말 것"
        )
    return ""


def category_specific_rules_for(category_code: str, target_competitor: str) -> str:
    if category_code == "H2H":
        return f"타깃 경쟁사: {target_competitor}"
    if category_code == "COMP_ONLY":
        return f"타깃 경쟁사: {target_competitor}"
    return ""


# ──────────────────────────────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="GEO Diagnostic Prompt Generator (rev 3)")
    parser.add_argument("--brand", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY") or ANTHROPIC_API_KEY
    if not api_key or api_key.startswith("sk-ant-..."):
        print("ANTHROPIC_API_KEY 환경변수 또는 config.py를 설정해주세요.")
        return

    random.seed(args.seed)

    brand = load_brand_config(args.brand)
    brand_dir = Path(args.brand).parent
    prompts_file = brand_dir / "prompts.csv"

    competitors = get_competitors(brand)
    competitor_names = [c["name"] for c in competitors]
    competitor_tokens_by_name = {c["name"]: c["tokens"] for c in competitors}
    all_competitor_tokens = flatten_tokens(competitors)
    targets = get_category_targets(brand)
    brand_tokens = get_brand_name_tokens(brand)
    brand_name = brand.get("brand_name", "")

    if not competitors:
        print("경쟁사 목록이 비어 있음. brand_config.json의 competitors를 확인하세요.")
        return

    client = Anthropic(api_key=api_key)

    alias_summary = []
    for c in competitors:
        n_alias = len(c["keywords"])
        alias_summary.append(f"{c['name']} (+{n_alias} 별칭)" if n_alias else c["name"])
    print(
        f"[{brand_name}] 진단셋 생성 시작\n"
        f"  - 경쟁사 {len(competitors)}개: {', '.join(alias_summary)}\n"
        f"  - 목표 총 {sum(targets.values())}개 "
        f"(NEUTRAL {targets['NEUTRAL']} / H2H {targets['H2H']} / "
        f"COMP_ONLY {targets['COMP_ONLY']} / BRAND_ONLY {targets['BRAND_ONLY']})"
    )

    rows: List[Dict] = []
    counters: Dict[str, int] = defaultdict(int)
    persona_cursor = 0
    personas = get_personas(brand)
    product_category = brand.get("product_category", "")

    # ─── NEUTRAL (서브분류 CAT/SYM/ALT/PRC/USE/DEC, 페르소나 라운드로빈) ───
    print("\n[NEUTRAL] 중립 (브랜드/경쟁사 미언급)")
    neutral_target = targets["NEUTRAL"]
    base_total = sum(a[2] for a in NEUTRAL_ANGLES)
    # 기본 합계와 다르면 비율 유지 스케일링
    if neutral_target == base_total:
        neutral_alloc = [(code, label, n, angle) for (code, label, n, angle) in NEUTRAL_ANGLES]
    else:
        scale = neutral_target / base_total
        neutral_alloc = []
        allocated = 0
        for i, (code, label, n, angle) in enumerate(NEUTRAL_ANGLES):
            if i == len(NEUTRAL_ANGLES) - 1:
                alloc = neutral_target - allocated
            else:
                alloc = round(n * scale)
                allocated += alloc
            neutral_alloc.append((code, label, alloc, angle))

    mention_neutral = mention_rules_for("NEUTRAL", brand_name, "", [], competitor_names)
    for code, label, n, angle in neutral_alloc:
        if n <= 0:
            continue
        persona = personas[persona_cursor % len(personas)]
        persona_cursor += 1
        batch = generate_batch(
            client, brand,
            category_code="NEUTRAL",
            target_count=n,
            angle_hint=angle,
            mention_rules=mention_neutral,
            persona_desc=persona["desc"],
            target_competitor="",
            category_specific_rules="",
            label_for_log=f"{code}/{label}",
            brand_tokens=brand_tokens,
            all_competitor_tokens=all_competitor_tokens,
            target_competitor_tokens=[],
            few_shot_examples=NEUTRAL_FEW_SHOTS.get(code, []),
            anti_examples=NEUTRAL_ANTI.get(code, []),
        )
        for p in batch["prompts"]:
            counters["NEUTRAL"] += 1
            rows.append({
                "prompt_id": f"NEUTRAL-{counters['NEUTRAL']:03d}",
                "category_code": "NEUTRAL",
                "category": CATEGORY_LABELS["NEUTRAL"],
                "subcategory": code,
                "prompt_text": p,
                "target_competitor": "",
            })

    # ─── H2H (경쟁사별 균등) ──────────────────────────────────────────
    print("\n[H2H] 직접 비교 (자사 + 경쟁사 동시)")
    h2h_alloc = allocate_targets_to(targets["H2H"], competitor_names)
    for comp, n in h2h_alloc.items():
        if n <= 0:
            continue
        comp_tokens = competitor_tokens_by_name[comp]
        comp_aliases = [t for t in comp_tokens if t != comp]
        persona = personas[persona_cursor % len(personas)]
        persona_cursor += 1
        angle = (
            f"'{brand_name}'와 '{comp}'를 직접 비교하는 질문. "
            f"효과, 가격, 사용편의, 대상 사용자, 후기 신뢰감, 종합 추천 등 다양한 축을 섞을 것. "
            f"각 질문에 페르소나(나이/생애단계/직업)와 카테고리 단어('{product_category}')를 비교어 직전에 명시할 것"
        )
        batch = generate_batch(
            client, brand,
            category_code="H2H",
            target_count=n,
            angle_hint=angle,
            mention_rules=mention_rules_for("H2H", brand_name, comp, comp_aliases, competitor_names),
            persona_desc=persona["desc"],
            target_competitor=comp,
            category_specific_rules=category_specific_rules_for("H2H", comp),
            label_for_log=comp,
            brand_tokens=brand_tokens,
            all_competitor_tokens=all_competitor_tokens,
            target_competitor_tokens=comp_tokens,
            few_shot_examples=h2h_few_shots(brand_name, comp, product_category),
            anti_examples=H2H_ANTI,
        )
        for p in batch["prompts"]:
            counters["H2H"] += 1
            rows.append({
                "prompt_id": f"H2H-{counters['H2H']:03d}",
                "category_code": "H2H",
                "category": CATEGORY_LABELS["H2H"],
                "subcategory": "",
                "prompt_text": p,
                "target_competitor": comp,
            })

    # ─── COMP_ONLY (경쟁사별 균등) ────────────────────────────────────
    print("\n[COMP_ONLY] 경쟁사 단독 지명")
    comp_alloc = allocate_targets_to(targets["COMP_ONLY"], competitor_names)
    for comp, n in comp_alloc.items():
        if n <= 0:
            continue
        comp_tokens = competitor_tokens_by_name[comp]
        comp_aliases = [t for t in comp_tokens if t != comp]
        persona = personas[persona_cursor % len(personas)]
        persona_cursor += 1
        angle = (
            f"'{comp}'를 이미 알고 있는 소비자가 대안, 비교, 비슷한 제품을 묻는 질문. "
            f"각 질문에 페르소나(나이/생애단계/직업)와 카테고리 단어('{product_category}'), "
            f"가격대·기간 등 구체 조건을 자연스럽게 박을 것"
        )
        batch = generate_batch(
            client, brand,
            category_code="COMP_ONLY",
            target_count=n,
            angle_hint=angle,
            mention_rules=mention_rules_for("COMP_ONLY", brand_name, comp, comp_aliases, competitor_names),
            persona_desc=persona["desc"],
            target_competitor=comp,
            category_specific_rules=category_specific_rules_for("COMP_ONLY", comp),
            label_for_log=comp,
            brand_tokens=brand_tokens,
            all_competitor_tokens=all_competitor_tokens,
            target_competitor_tokens=comp_tokens,
            few_shot_examples=comp_only_few_shots(comp, product_category),
            anti_examples=COMP_ONLY_ANTI,
        )
        for p in batch["prompts"]:
            counters["COMP_ONLY"] += 1
            rows.append({
                "prompt_id": f"COMP_ONLY-{counters['COMP_ONLY']:03d}",
                "category_code": "COMP_ONLY",
                "category": CATEGORY_LABELS["COMP_ONLY"],
                "subcategory": "",
                "prompt_text": p,
                "target_competitor": comp,
            })

    # ─── BRAND_ONLY ──────────────────────────────────────────────────
    print("\n[BRAND_ONLY] 자사 단독 지명")
    brand_angle = (
        f"'{brand_name}'에 대해 직접 묻는 질문. "
        f"효과, 구매 판단, 신뢰성, 후기, 추천 대상 등. "
        f"각 질문에 시간(예: '6개월 이상', '3개월 안에'), 연령대(예: '30대 직장인'), "
        f"가격대(예: '30-50만원대') 같은 구체 차원을 자연스럽게 박을 것"
    )
    persona = personas[persona_cursor % len(personas)]
    persona_cursor += 1
    batch = generate_batch(
        client, brand,
        category_code="BRAND_ONLY",
        target_count=targets["BRAND_ONLY"],
        angle_hint=brand_angle,
        mention_rules=mention_rules_for("BRAND_ONLY", brand_name, "", [], competitor_names),
        persona_desc=persona["desc"],
        target_competitor="",
        category_specific_rules="",
        label_for_log="BRAND_ONLY",
        brand_tokens=brand_tokens,
        all_competitor_tokens=all_competitor_tokens,
        target_competitor_tokens=[],
        few_shot_examples=brand_only_few_shots(brand_name),
        anti_examples=BRAND_ONLY_ANTI,
    )
    for p in batch["prompts"]:
        counters["BRAND_ONLY"] += 1
        rows.append({
            "prompt_id": f"BRAND_ONLY-{counters['BRAND_ONLY']:03d}",
            "category_code": "BRAND_ONLY",
            "category": CATEGORY_LABELS["BRAND_ONLY"],
            "subcategory": "",
            "prompt_text": p,
            "target_competitor": "",
        })

    # ─── 저장 ────────────────────────────────────────────────────────
    fieldnames = [
        "prompt_id", "category_code", "category", "subcategory",
        "prompt_text", "target_competitor",
    ]
    os.makedirs(prompts_file.parent, exist_ok=True)
    with open(prompts_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    grand_total = sum(targets.values())
    print(
        f"\n[TOTAL] NEUTRAL={counters['NEUTRAL']}, H2H={counters['H2H']}, "
        f"COMP_ONLY={counters['COMP_ONLY']}, BRAND_ONLY={counters['BRAND_ONLY']}, "
        f"grand_total={len(rows)} / {grand_total}"
    )
    print(f"저장 → {prompts_file}")

    for code, target in targets.items():
        actual = counters.get(code, 0)
        marker = "✓" if actual >= target else "⚠️"
        print(f"  {marker} {code}: {actual}/{target}")


if __name__ == "__main__":
    main()
