"""
본실험 API 러너 — gpt-5.4 (OpenAI).

재현성 룰 (CLAUDE.md §4 R1~R10) 강제 적용:
- R1: 반복 20회 (조합 × 쿼리당)
- R2: temperature default (None 전달 → API 기본값)
- R3: 모델 버전 .env에서 핀 (OPENAI_MODEL_VERSION)
- R4: 매 반복마다 상품 제시 순서 랜덤 셔플 (seed = seed_base + repeat_idx)
- R5: seed 모든 jsonl 라인에 기록
- R6: Y 변수 중 Y2a는 binary + continuous 이중 산출 (분석 단계에서)
- R7: Wilson 95% CI — 분석 단계
- R8: raw 응답 원문 jsonl 저장 (캐시와 별도)
- R9: 파일럿 우선 권장 (이 스크립트의 --mode pilot)
- R10: 버티컬 분리 — 이 스크립트는 medical_device만 (gargle은 별도 호출)

응답 캐싱:
  key = sha256(model_version + system + user + seed + temperature_repr)
  hit → API 호출 안 함. 재실행 무료.

사용법:
    # 파일럿 (L27 × 8쿼리 × 5회 = 1,080 호출, ~$14)
    python experiments/runner.py --mode pilot

    # 본실험 (L54 × 8쿼리 × 20회 = 8,640 호출, ~$108)
    python experiments/runner.py --mode main
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")


# ========== 설정 ==========
MODEL_VERSION = os.environ.get("OPENAI_MODEL_VERSION", "gpt-5.4")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
SEED_BASE = int(os.environ.get("SEED_BASE", "42"))

EXP_DIR = REPO_ROOT / "experiments"
PAGES_DIR = EXP_DIR / "synthetic_pages"
CACHE_DIR = EXP_DIR / "api_runs" / "_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ========== 쿼리 로드 (YAML, 페르소나 stratified 32개 = 8유형 × 4) ==========
QUERIES_YAML = Path(__file__).resolve().parent / "prompts" / "queries_medical_최종.yaml"

def load_queries() -> list[tuple[str, str, str]]:
    """Returns list of (query_id, query_type, query_text).
       query_id 예: BRD-1, BRD-2, BRD-3, CAT-1, ...
    """
    with QUERIES_YAML.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = []
    for qtype, qlist in data.items():
        for i, text in enumerate(qlist, start=1):
            items.append((f"{qtype}-{i}", qtype, text))
    return items


# ========== 경쟁군 N=13 (2026-04-24 v4 — elvie 제외, 의료기기 버티컬 한정) ==========
# 식약처 등록 여부는 메타 라벨이지 경쟁군 포함 기준 아님.
# AI가 실제 추천에서 섞어 언급하는 모든 국내 브랜드 포함.
# 해외 Elvie는 Wayne 결정(2026-04-24)으로 제외 — 한국 AI 추천에 등장 빈도 낮을 것.
COMPETITORS = [
    # 우리 anchor
    {"id": "bodydoctor", "name": "바디닥터 요실금치료기", "brand": "GN그룹", "category": "medical_device"},
    # 의료기기 (식약처 3등급 등록)
    {"id": "easyk", "name": "이지케이 EASY-K", "brand": "알파메딕", "category": "medical_device"},
    {"id": "coway_therasol", "name": "코웨이 테라솔 U", "brand": "코웨이", "category": "medical_device"},
    {"id": "ceragem", "name": "세라젬 요실금치료기", "brand": "세라젬", "category": "medical_device"},
    {"id": "furenhealth", "name": "퓨런헬스케어 요실금치료기", "brand": "퓨런헬스케어", "category": "medical_device"},
    # 공산품 (식약처 미등록, 동일 키워드로 경쟁)
    {"id": "peronian", "name": "페로니언 케겔 훈련기", "brand": "페로니언", "category": "consumer_product"},
    {"id": "hools", "name": "훌스 음파방석", "brand": "HOOL'S", "category": "consumer_product"},
    {"id": "wavecare", "name": "웨이브케어 V8 포 맨/우먼", "brand": "웨이브케어", "category": "consumer_product"},
    {"id": "stopyo", "name": "스탑요 자동 케겔 운동기구", "brand": "스탑요", "category": "consumer_product"},
    {"id": "ems_vital", "name": "EMS케겔휘트니스 비틀", "brand": "EMS케겔휘트니스", "category": "consumer_product"},
    {"id": "kegel_magic", "name": "케겔매직", "brand": "케겔매직", "category": "consumer_product"},
    {"id": "huonsen", "name": "휴온센 EMS 레깅스", "brand": "휴온센", "category": "consumer_product"},
    {"id": "applehip", "name": "애플힙 2026년형 케겔자동운동기구", "brand": "애플힙", "category": "consumer_product"},
    # 식약처 등록 의료기기 (Phase A+에서 검증 통과 추가)
    {"id": "mblab", "name": "엠비랩 ReTens", "brand": "엠비랩(MBLab)", "category": "medical_device"},
]

# ========== 바디닥터 K (케겔 힙머신) anchor 경쟁군 N=8 (2026-04-26 신규) ==========
# K = 의료기기 아닌 일반 건강보조 운동기구. 마케팅 제한 X.
# 경쟁군: 닥터케이 + 기존 공산품 케겔 7종 (페로니언/애플힙/휴온센/케겔매직/훌스/웨이브케어/ems_vital)
COMPETITORS_K = [
    {"id": "bodydoctor_k", "name": "바디닥터 K 케겔 힙머신", "brand": "GN그룹/제너럴네트", "category": "kegel_exerciser"},
    {"id": "drk", "name": "닥터케이 저주파 EMS 케겔운동기", "brand": "닥터케이", "category": "kegel_exerciser"},
    {"id": "peronian", "name": "페로니언 케겔 훈련기", "brand": "페로니언", "category": "kegel_exerciser"},
    {"id": "applehip", "name": "애플힙 2026년형 케겔자동운동기구", "brand": "애플힙", "category": "kegel_exerciser"},
    {"id": "huonsen", "name": "휴온센 EMS 레깅스", "brand": "휴온센", "category": "kegel_exerciser"},
    {"id": "kegel_magic", "name": "케겔매직", "brand": "케겔매직", "category": "kegel_exerciser"},
    {"id": "hools", "name": "훌스 음파방석", "brand": "HOOL'S", "category": "kegel_exerciser"},
    {"id": "wavecare", "name": "웨이브케어 V8 포 맨/우먼", "brand": "웨이브케어", "category": "kegel_exerciser"},
]

# ========== 가글 경쟁군 N=12 (2026-04-24 Wayne 결정: 풀 확장) ==========
# 친구 대시보드 NER 발견 반영. 어썸쿨(프로폴리스 직접경쟁) 반드시 포함.
COMPETITORS_GARGLE = [
    # 우리 anchor
    {"id": "propolinse", "name": "프로폴린스 가글", "brand": "지앤코스/GN그룹", "category": "gargle"},
    # 국내 대표
    {"id": "listerine", "name": "리스테린 쿨민트 가글", "brand": "존슨앤존슨", "category": "gargle"},
    {"id": "garglin", "name": "가그린 제로", "brand": "동아제약", "category": "gargle"},
    {"id": "perio", "name": "페리오 가글", "brand": "LG생활건강", "category": "gargle"},
    {"id": "gargle_2080", "name": "2080 구강청결제", "brand": "애경산업", "category": "gargle"},
    # 친구 대시보드 NER 발견 — 풀 확장
    {"id": "awesomecool", "name": "어썸쿨 프로폴리스 가글 600ml", "brand": "어썸쿨", "category": "gargle"},
    {"id": "therabreath", "name": "테라브레스 오랄린스", "brand": "TheraBreath", "category": "gargle"},
    {"id": "usimol", "name": "유시몰 가글", "brand": "유시몰", "category": "gargle"},
    {"id": "colgate", "name": "콜게이트 플락스", "brand": "Colgate", "category": "gargle"},
    {"id": "oralb", "name": "오랄비 가글", "brand": "Oral-B/P&G", "category": "gargle"},
    {"id": "sensodyne", "name": "센소다인 가글", "brand": "Sensodyne", "category": "gargle"},
    {"id": "kwangdong", "name": "광동 인후엔 가글", "brand": "광동제약", "category": "gargle"},
]


SYSTEM_PROMPT_BASE = (
    "당신은 제품 비교·추천을 도와주는 쇼핑 어시스턴트입니다. "
    "사용자 질문에 성실하게 답하되, 경쟁 제품 중에서만 비교하고 그 외 제품은 언급하지 마세요. "
    "추천 이유는 간결하게 1~2문장으로 설명하세요."
)

# ========== 페르소나 (Wayne 요청 2026-04-24, 1차 발표 피드백 반영) ==========
# "주로 자기 제품을 사는 사람들의 페르소나를 대입한 버전 vs 안 한 버전"
# 두 버전을 비교해서 페르소나 컨디셔닝이 추천 순위에 미치는 영향 확인.
PERSONAS = {
    "none": None,  # baseline — 페르소나 주입 없음
    "gn_buyer": (
        # TODO(2026-04-24): GN그룹 실제 구매 데이터 받으면 교체
        # 현재는 요실금치료기 카테고리 일반 페르소나 placeholder
        "당신의 사용자는 35~55세 여성이며, 출산 경험이 있고 현재 경미한 요실금 증상을 겪고 있습니다. "
        "가정용 의료기기 구매를 고려 중이며, 의사·약사의 권장을 신뢰하고, "
        "임상 근거와 식약처 인증을 중요시합니다. 가격보다 효과와 안전성을 우선합니다."
    ),
}


def build_system_prompt(persona_id: str) -> str:
    """persona_id ∈ {'none', 'gn_buyer'} → 조합된 시스템 프롬프트."""
    persona = PERSONAS.get(persona_id)
    if persona is None:
        return SYSTEM_PROMPT_BASE
    return SYSTEM_PROMPT_BASE + "\n\n[사용자 페르소나]\n" + persona


# ========== 자료구조 ==========
@dataclass
class RunConfig:
    mode: str                              # pilot | main
    model_version: str
    n_repeat: int
    temperature: Optional[float] = None    # None → API 기본
    seed_base: int = SEED_BASE
    use_cache: bool = True
    vertical: str = "medical_device"
    persona_id: str = "none"               # none | gn_buyer


@dataclass
class CallResult:
    response_id: str        # UUID — 스프레드시트 ↔ jsonl 역참조 키 (D2)
    run_id: str
    page_id: str
    query_id: str           # 예: "BRD-1", "CAT-2"
    query_type: str         # 예: "BRD", "CAT"
    query_text: str         # 쿼리 원문 (검수 시 ID 재조회 불필요)
    repeat_idx: int
    seed: int
    model_version: str
    temperature: Optional[float]
    persona_id: str         # none | gn_buyer
    system_hash: str
    system_prompt_excerpt: str   # 첫 300자 (페르소나 적용 여부 한눈에)
    user_prompt_hash: str
    page_text_excerpt: str       # 페이지 본문 첫 300자 (어떤 콘텍스트였는지)
    products_order: list[str]
    raw_response: str
    response_length: int         # 짧은 응답·회피만 빠르게 필터
    # ── Y2a 5분화 (친구 대시보드 교훈 반영) ────
    y2a_mentioned_brand_ids: list[str]        # 사전 정의 N=6 중 언급
    y2a_our_selected: bool                    # 공통: 우리 언급 여부
    y2a_mention: bool                          # = our_selected 별명
    y2a_positive: Optional[str]               # BRD: "positive"/"neutral"/"negative"
    y2a_alternative: Optional[bool]           # COM: 대안으로 소환됐는지
    y2a_no_show: Optional[bool]               # COM: 미노출
    y2a_wintieloss: Optional[str]             # CMP: "win"/"tie"/"loss"/"solo"
    y2a_singleselect: Optional[bool]          # DEC: 최종 선택 받았는지
    # ── 미인지 경쟁사 자동 발굴 ────
    other_brands_detected: list[str]          # 친구 대시보드의 NER 교훈
    # ── 기타 Y ────
    y4_safety_avoidance: bool
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: str
    from_cache: bool

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


# ========== 캐시 ==========
def cache_key(model: str, system: str, user: str, seed: int, temp: Optional[float]) -> str:
    h = hashlib.sha256()
    h.update(f"{model}||{system}||{user}||{seed}||{temp!r}".encode("utf-8"))
    return h.hexdigest()[:24]


def load_cache(key: str) -> Optional[dict]:
    p = CACHE_DIR / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_cache(key: str, data: dict, *, meta: Optional[dict] = None) -> None:
    """
    캐시 저장. data는 raw_response/tokens_in/tokens_out 핵심,
    meta는 추적용 메타(model_version/query_id/page_id/seed/cached_at).
    메타 없으면 raw_response만 저장됨 — 호출 추적 불가능 (legacy 호환).
    """
    p = CACHE_DIR / f"{key}.json"
    payload = dict(data)
    if meta:
        payload["_meta"] = meta
    p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


# ========== 재현성 가드 ==========
def assert_reproducibility(cfg: RunConfig) -> None:
    assert cfg.model_version, "R3: 모델 버전 명시 필수"
    if cfg.mode == "main":
        assert cfg.n_repeat >= 15, f"R1: 본실험 반복 ≥15 필수 (pilot 제외), got {cfg.n_repeat}"
    if cfg.temperature is not None:
        assert 0.5 <= cfg.temperature <= 1.0, "R2: temperature 0 고정 금지 ([0.5, 1.0] 또는 None)"


# ========== 응답 파싱 ==========

# 사전 정의 경쟁사 키워드 매칭 (의료기기 N=13 + 가글 N=12, 2026-04-24 v5)
COMPETITOR_KEYWORDS = {
    # 의료기기 (N=13)
    "bodydoctor": ["바디닥터"],
    "easyk": ["이지케이", "EASY-K", "EASY K", "easyk"],
    "coway_therasol": ["코웨이 테라솔", "테라솔 U", "테라솔U", "Coway Therasol"],
    "ceragem": ["세라젬"],
    "furenhealth": ["퓨런", "furenhealth", "furun"],
    "peronian": ["페로니언", "Peronian"],
    "hools": ["훌스", "HOOL", "hool"],
    "wavecare": ["웨이브케어"],
    "stopyo": ["스탑요"],
    "ems_vital": ["EMS케겔휘트니스", "비틀"],
    "kegel_magic": ["케겔매직"],
    "huonsen": ["휴온센"],
    "applehip": ["애플힙"],
    "mblab": ["엠비랩", "MBLab", "ReTens", "Retens"],
    "bodydoctor_k": ["바디닥터 K", "바디닥터K", "Body Doctor K", "BodyDoctor K", "케겔 힙머신", "케겔힙머신"],
    "drk": ["닥터케이", "닥터 케이", "Doctor K", "DR.K", "Dr.K"],
    # 가글 (N=12)
    "propolinse": ["프로폴린스", "Propolinse"],
    "listerine": ["리스테린", "Listerine"],
    "garglin": ["가그린", "Garglin"],
    "perio": ["페리오"],
    "gargle_2080": ["2080"],
    "awesomecool": ["어썸쿨"],
    "therabreath": ["테라브레스", "TheraBreath"],
    "usimol": ["유시몰", "Usimol"],
    "colgate": ["콜게이트", "Colgate"],
    "oralb": ["오랄비", "오랄B", "Oral-B", "OralB"],
    "sensodyne": ["센소다인", "Sensodyne"],
    "kwangdong": ["광동 인후엔", "광동인후엔", "인후엔"],
}

# 한국 의료기기/케겔/가글 카테고리에서 AI가 언급할 가능성 있는 브랜드 사전 (친구 대시보드 NER 교훈 반영)
# 응답에서 이 키워드들도 검출해서 "other_brands_detected" 로 기록 → H14 외부 증거 변수 보강
KNOWN_OTHER_BRANDS = [
    # 의료기기
    ("알파메딕", "alphamedic"),
    ("썬텍메디칼", "suntek"),
    ("청우메디칼", "chungwoo"),
    ("비엠씨", "bmc"),
    ("퓨런헬스케어", "furenhealth"),
    ("쉬엔비", "sheinbi"),
    ("유진플러스", "yujin"),
    ("리모트솔루션", "remote_solution"),
    ("엠비랩", "mblab"),
    ("애플힙", "applehip"),
    ("이고진", "egojin"),
    ("메디펄스", "medipulse"),
    ("펠비케어", "pelvicare"),
    # 가글은 2026-04-24 풀 확장으로 모두 COMPETITORS_GARGLE 로 편입됨.
    # 여기선 아직 안 잡힌 기타 가글 브랜드(있으면 추후 추가)만 유지.
    # 현재 비어 있음 — 필요 시 "스타버스트"·"스마일" 등 새 브랜드 등장하면 추가.
]


def parse_mentioned_predefined(response_text: str) -> list[str]:
    """사전 정의 경쟁군 N=6 중 언급된 id."""
    out = []
    text_lower = response_text.lower()
    for brand_id, kws in COMPETITOR_KEYWORDS.items():
        if any(kw in response_text or kw.lower() in text_lower for kw in kws):
            out.append(brand_id)
    return out


def parse_other_brands(response_text: str, exclude_ids: list[str]) -> list[str]:
    """사전 정의 외 다른 브랜드 검출 (H14 외부 증거, 친구 대시보드 교훈)."""
    text_lower = response_text.lower()
    out = set()
    for kw, slug in KNOWN_OTHER_BRANDS:
        if slug in exclude_ids:
            continue
        if kw in response_text or kw.lower() in text_lower:
            out.add(kw)
    return sorted(out)


# ========== Y2a 5분화 (쿼리 유형별 특화) ==========
# 친구 대시보드 교훈: 쿼리 유형마다 측정 지표가 달라야 함

POSITIVE_TONE = ["추천", "좋다", "좋습니다", "우수", "뛰어", "best", "훌륭", "믿을 수 있", "신뢰"]
NEGATIVE_TONE = ["추천하지 않", "권하지 않", "별로", "실망", "피하", "문제", "단점이 많"]


def parse_y2a_by_type(response_text: str, query_id: str, our_brand_id: str,
                     mentioned: list[str]) -> dict:
    """
    쿼리 유형별로 Y2a 특화 지표 산출.
    query_id 형식: "BRD-1", "CAT-2", "COM-3" ...
    """
    qtype = query_id.split("-")[0]
    our_in = our_brand_id in mentioned

    result = {
        "y2a_mention": our_in,  # 공통: 단순 언급 여부
        "y2a_positive": None,
        "y2a_alternative": None,
        "y2a_no_show": None,
        "y2a_wintieloss": None,
        "y2a_singleselect": None,
    }

    if qtype == "BRD":
        # 브랜드 지명 → 감성 톤
        has_pos = any(k in response_text for k in POSITIVE_TONE)
        has_neg = any(k in response_text for k in NEGATIVE_TONE)
        if has_pos and not has_neg:
            result["y2a_positive"] = "positive"
        elif has_neg and not has_pos:
            result["y2a_positive"] = "negative"
        else:
            result["y2a_positive"] = "neutral"

    elif qtype == "COM":
        # 경쟁사 대안 → 대안으로 소환됐는지 + 미노출
        result["y2a_alternative"] = our_in
        result["y2a_no_show"] = not our_in

    elif qtype == "CMP":
        # 직접 비교 → win/tie/loss
        # 단순 규칙: 응답 첫 부분에서 우리 브랜드가 더 긍정적으로 묘사되면 win
        # 정밀 분류는 별도 LLM 분류기 필요 (향후 개선)
        competitors_mentioned = [m for m in mentioned if m != our_brand_id]
        if not competitors_mentioned:
            result["y2a_wintieloss"] = "solo"  # 경쟁사 언급 없음
        elif our_in and not any(neg in response_text for neg in NEGATIVE_TONE):
            # 긍정 톤 + 우리 언급
            first_200 = response_text[:200]
            bd_pos = any(kw in first_200 for kw in COMPETITOR_KEYWORDS.get(our_brand_id, []))
            if bd_pos:
                result["y2a_wintieloss"] = "win"
            else:
                result["y2a_wintieloss"] = "tie"
        else:
            result["y2a_wintieloss"] = "loss" if not our_in else "tie"

    elif qtype == "DEC":
        # 구매 의도 (단일 선택) → 우리 브랜드가 최종 선택 받았는지
        # 응답 마지막 200자에서 우리 브랜드 언급 + 단호한 톤
        last_segment = response_text[-200:]
        result["y2a_singleselect"] = any(kw in last_segment for kw in COMPETITOR_KEYWORDS.get(our_brand_id, []))

    # CAT/SYM/PRC/USE: y2a_mention 으로 이미 커버됨

    return result


SAFETY_AVOID_PATTERNS = ["전문가와 상담", "의사와 상담", "의료진 상담", "병원 방문", "진료를 받으"]


def parse_y4(response_text: str) -> bool:
    return any(p in response_text for p in SAFETY_AVOID_PATTERNS)


# ========== 단일 호출 ==========
def make_user_prompt(page_html: str, query: str, products_order: list[str]) -> str:
    product_list = "\n".join(
        f"{i+1}. {next(c['name'] for c in COMPETITORS if c['id'] == pid)}"
        for i, pid in enumerate(products_order)
    )
    # 가상 페이지 HTML을 압축해서 prompt에 주입 (텍스트만)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    page_text = soup.get_text(separator=" ", strip=True)[:3000]

    return (
        f"다음 제품들을 비교해 주세요:\n{product_list}\n\n"
        f"첫 번째 제품(바디닥터)의 상세 페이지 내용:\n{page_text}\n\n"
        f"사용자 질문: {query}\n\n"
        f"위 제품들만 고려해서 답변해 주세요. 추천 이유도 같이."
    )


def call_one(cfg: RunConfig, client: OpenAI, page_html: str, page_id: str,
             query_id: str, query: str, repeat_idx: int, run_id: str) -> CallResult:
    # R4: 매 반복 상품 순서 셔플
    seed = cfg.seed_base + repeat_idx
    rng = random.Random(seed)
    order = [c["id"] for c in COMPETITORS]
    rng.shuffle(order)

    user_prompt = make_user_prompt(page_html, query, order)

    # 페이지 본문 발췌 (검수용)
    from bs4 import BeautifulSoup
    _soup = BeautifulSoup(page_html, "html.parser")
    for _t in _soup(["script", "style"]):
        _t.decompose()
    page_text_excerpt = _soup.get_text(separator=" ", strip=True)[:300]

    system_prompt = build_system_prompt(cfg.persona_id)
    sys_hash = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:12]
    usr_hash = hashlib.sha256(user_prompt.encode("utf-8")).hexdigest()[:12]
    key = cache_key(cfg.model_version, system_prompt, user_prompt, seed, cfg.temperature)

    cached = load_cache(key) if cfg.use_cache else None
    from_cache = cached is not None

    if cached:
        raw = cached["raw_response"]
        tokens_in = cached.get("tokens_in", 0)
        tokens_out = cached.get("tokens_out", 0)
    else:
        # OpenAI 호출
        params = {
            "model": cfg.model_version,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if cfg.temperature is not None:
            params["temperature"] = cfg.temperature

        r = client.chat.completions.create(**params)
        raw = r.choices[0].message.content or ""
        tokens_in = r.usage.prompt_tokens if r.usage else 0
        tokens_out = r.usage.completion_tokens if r.usage else 0
        save_cache(
            key,
            {"raw_response": raw, "tokens_in": tokens_in, "tokens_out": tokens_out},
            meta={
                "model_version": cfg.model_version,
                "query_id": query_id,
                "page_id": page_id,
                "seed": seed,
                "persona_id": cfg.persona_id,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    # Y 변수 추출 (v2.1 — 5분화 + NER)
    mentioned = parse_mentioned_predefined(raw)
    our_selected = "bodydoctor" in mentioned
    y2a_sub = parse_y2a_by_type(raw, query_id, "bodydoctor", mentioned)
    other_brands = parse_other_brands(raw, exclude_ids=mentioned)
    y4 = parse_y4(raw)

    # 모델별 단가 (per 1M tokens)
    # gpt-5.4: $2.50 / $15
    # gpt-5.4-mini: $0.75 / $4.50
    # gpt-5.4-nano: $0.20 / $1.25
    model_prices = {
        "gpt-5.4": (2.5, 15.0),
        "gpt-5.4-mini": (0.75, 4.5),
        "gpt-5.4-nano": (0.2, 1.25),
    }
    in_rate, out_rate = model_prices.get(cfg.model_version, (2.5, 15.0))
    cost = tokens_in * in_rate / 1_000_000 + tokens_out * out_rate / 1_000_000

    return CallResult(
        response_id=str(uuid.uuid4()),
        run_id=run_id,
        page_id=page_id,
        query_id=query_id,
        query_type=query_id.split("-")[0],
        query_text=query,
        repeat_idx=repeat_idx,
        seed=seed,
        model_version=cfg.model_version,
        temperature=cfg.temperature,
        persona_id=cfg.persona_id,
        system_hash=sys_hash,
        system_prompt_excerpt=system_prompt[:300],
        user_prompt_hash=usr_hash,
        page_text_excerpt=page_text_excerpt,
        products_order=order,
        raw_response=raw,
        response_length=len(raw),
        y2a_mentioned_brand_ids=mentioned,
        y2a_our_selected=our_selected,
        y2a_mention=y2a_sub["y2a_mention"],
        y2a_positive=y2a_sub["y2a_positive"],
        y2a_alternative=y2a_sub["y2a_alternative"],
        y2a_no_show=y2a_sub["y2a_no_show"],
        y2a_wintieloss=y2a_sub["y2a_wintieloss"],
        y2a_singleselect=y2a_sub["y2a_singleselect"],
        other_brands_detected=other_brands,
        y4_safety_avoidance=y4,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost,
        timestamp=datetime.now(timezone.utc).isoformat(),
        from_cache=from_cache,
    )


# ========== 실험 본체 ==========
def run_experiment(cfg: RunConfig) -> dict:
    assert_reproducibility(cfg)
    if not API_KEY:
        sys.exit("OPENAI_API_KEY 미설정")

    client = OpenAI(api_key=API_KEY)
    run_id = f"{cfg.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = EXP_DIR / "api_runs" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # config snapshot
    (out_dir / "config.json").write_text(
        json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 설계 매트릭스 로드
    matrix_path = PAGES_DIR / "design_matrix.csv"
    with matrix_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 쿼리 8유형 × 3개 = 24개 (YAML 로드)
    all_queries = load_queries()  # [(qid, qtype, text), ...]
    if cfg.mode == "pilot":
        rows = rows[:27]
        # 파일럿: BRD-1, CAT-1, SYM-1 (유형당 1개만)
        query_items = [q for q in all_queries if q[0].endswith("-1")][:3]
    else:
        query_items = all_queries  # 전체 24개

    jsonl_path = out_dir / "responses.jsonl"
    total = len(rows) * len(query_items) * cfg.n_repeat
    print(f"🎬 run_id={run_id}, 총 호출: {total}")
    print(f"   페이지={len(rows)}, 쿼리={len(query_items)}, 반복={cfg.n_repeat}, 모델={cfg.model_version}")

    done = 0
    total_cost = 0.0
    cache_hits = 0
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            page_id = row["page_id"]
            page_html = (PAGES_DIR / f"{page_id}.html").read_text(encoding="utf-8")
            for qid, qtype, query in query_items:
                for rep in range(cfg.n_repeat):
                    result = call_one(cfg, client, page_html, page_id, qid, query, rep, run_id)
                    f.write(result.to_jsonl() + "\n")
                    f.flush()
                    done += 1
                    total_cost += result.cost_usd
                    if result.from_cache:
                        cache_hits += 1
                    if done % 50 == 0:
                        print(f"  [{done}/{total}] 누적 비용 ${total_cost:.2f}, 캐시 히트 {cache_hits}")

    summary = {
        "run_id": run_id,
        "total_calls": total,
        "cache_hits": cache_hits,
        "total_cost_usd": round(total_cost, 4),
        "n_pages": len(rows),
        "n_queries": len(query_items),
        "n_repeat": cfg.n_repeat,
        "model_version": cfg.model_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ── 자동 후처리 (D4): responses.csv + SUMMARY.md + ANOMALIES.md ──
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from _postprocess import postprocess_run
        postprocess_run(out_dir)
        print(f"   responses.csv / SUMMARY.md / ANOMALIES.md 생성됨")
    except Exception as e:
        print(f"   ⚠️ 후처리 실패: {e}")

    print(f"\n✅ 실험 완료")
    print(f"   responses.jsonl: {jsonl_path}")
    print(f"   총 비용: ${total_cost:.2f}")
    print(f"   캐시 히트: {cache_hits} / {total}")
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pilot", "main"], default="pilot")
    p.add_argument("--n-repeat", type=int, default=None)
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--persona", choices=list(PERSONAS.keys()), default="none",
                   help="시스템 페르소나. 'none' = baseline, 'gn_buyer' = GN그룹 구매자 페르소나")
    p.add_argument("--dry-run", action="store_true", help="설정만 출력")
    args = p.parse_args()

    n_repeat = args.n_repeat if args.n_repeat is not None else (5 if args.mode == "pilot" else 20)
    cfg = RunConfig(
        mode=args.mode,
        model_version=MODEL_VERSION,
        n_repeat=n_repeat,
        temperature=args.temperature,
        use_cache=not args.no_cache,
        persona_id=args.persona,
    )

    if args.dry_run:
        print(json.dumps(asdict(cfg), ensure_ascii=False, indent=2))
        n_queries = 3 if args.mode == "pilot" else 24  # pilot: 3개, main: 8유형×3=24개
        n_pages = 27 if args.mode == "pilot" else 54
        est_calls = n_pages * n_queries * n_repeat
        # 평균 토큰 2,000 input + 500 output 기준 호출당 비용
        prices = {"gpt-5.4": 0.0125, "gpt-5.4-mini": 0.00375, "gpt-5.4-nano": 0.001025}
        per_call = prices.get(cfg.model_version, 0.0125)
        print(f"예상 호출: {est_calls}")
        print(f"예상 비용 ({cfg.model_version}): ${est_calls * per_call:.2f}")
        return

    run_experiment(cfg)


if __name__ == "__main__":
    main()
