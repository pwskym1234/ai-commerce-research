---
brand: 애플힙 (Apple Hip)
brand_slug: applehip
vertical: medical_device      # 카테고리 분류상. 실제는 비의료기기일 가능성 高
last_updated: 2026-04-23
data_sources: [GSshop 검색, 다나와 케겔운동기구 카테고리]
official_url_candidate: 미확인 — GSshop/홈쇼핑 채널 중심
distribution_channels: [GS홈쇼핑, GSshop]
f1_html_format: unknown
f2_jsonld: unknown
f3_numeric: ambiguous            # "2026년형 자동 케겔" 같은 마케팅 카피 중심
f4_cert_position: unknown
f5_cert_detail: none_likely      # 의료기기 등급 표기 미확인 (공산품 가능성)
f6_evidence: user_reviews
status: candidate_low_priority
priority: low_or_noise           # 본실험 포함 여부 Wayne 결정
---

# 애플힙 (Apple Hip)

## 핵심 사실
- **카테고리**: "2026년형 케겔자동운동기구" 마케팅. 방석 형태로 추정
- **유통**: GS홈쇼핑/GSshop 중심
- **의료기기 여부**: 공식 표기 미확인. **다나와 카테고리 노이즈와 동일선상에 있을 가능성** (만~수만원대 비의료기기 운동 도구)
- 다나와 "케겔운동기구" 카테고리 상위 1~10위는 모두 4,410원~19,800원 가격대의 **비의료기기 운동 도구** — 의료기기 EMS 케겔과 다른 시장

## 본실험에서의 역할
**카테고리 노이즈 대표 케이스**로 1개만 포함 검토. AI에게 "케겔운동기 추천"을 묻는 일반 사용자 쿼리에서 의료기기 EMS와 비의료기기 운동도구가 동시에 노출됨을 시연 가능. → **AiEO H 후보**: AI가 의료기기 vs 비의료기기를 구분해서 추천하는가?

## 미확인 / 다음 액션
- [ ] GSshop 외 자사몰 존재 여부
- [ ] 의료기기 인증 표기 검증
- [ ] Wayne: 본실험 포함 여부 결정 (포함 시 의료기기 카테고리에서 빼고 "범용 운동기구"로 별도 분류 권장)

## 참고 링크
- [GSshop 검색](https://m.gsshop.com/search/searchSect.gs?tq=%EC%BC%80%EA%B1%B8%EC%9A%B4%EB%8F%99&mseq=406355)
- [다나와 케겔운동기구 카테고리](https://prod.danawa.com/list/?cate=13337699)
