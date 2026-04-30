---
date: 2026-04-30
title: 어썸쿨(Awesome Cool) — "글로벌 가글" 검증 실패. 실재는 한국 도메스틱 브랜드
related_findings: []
contradicts: []
supports: [F2026-04-24_listerine_furen_status]   # URL verification discipline
vertical: gargle
phase: discovery
author: Claude
status: rejected_for_global_competitor_pool
---

# 어썸쿨(Awesome Cool) — 검증 실패 보고

## 1. 검증 의뢰 배경

Wayne으로부터 가글 vertical 글로벌 경쟁사 3개 리서치 의뢰:
1. TheraBreath (미국) — 검증 성공, [therabreath.md](../competitors/therabreath.md) 적층
2. Colgate Plax (글로벌) — 검증 성공, [colgate_plax.md](../competitors/colgate_plax.md) 적층
3. **Awesome Cool (어썸쿨)** — *실재성 검증 필수*, "일부 한국 자료에 글로벌 가글로 언급되나 의심스러움"

Wayne의 사전 경고: **퓨런 가짜 URL 사고 재발 방지**. 검증 안 되면 적층 금지.

## 2. 검증 절차

### 2.1 영문 검색
- 쿼리: `"Awesome Cool" mouthwash brand global manufacturer`
- 결과: **No links found** (영문 검색에서 글로벌 가글 브랜드로 매칭되는 결과 0건)

### 2.2 한국어 검색
- 쿼리: `"어썸쿨" OR "오썸쿨" OR "AwesomeCool" 가글 구강청결제 네이버`
- 결과: **awesomecool.co.kr** 자사몰 + **awesomelife.kr** 판매몰 + 대한리빙 등 한국 도메스틱 채널만 노출

### 2.3 회사 정보 검증 (awesomecool.co.kr/shopinfo/company.html fetch 완료)

| 항목 | 실제 정보 |
|------|---------|
| 운영 회사 | **주식회사 스터너즈 (Stunners Co., Ltd.)** |
| 대표 | 방지현, 방지철 |
| 사업자등록번호 | 730-87-02231 |
| 주소 | 서울 금천구 서부샛길 606 대성디폴리스지식산업센터 B동 1003호 |
| 통신판매업 | 제2021-서울금천-2353호 (2021년 등록) |
| 연락처 | 070-8285-8225 |
| 이메일 | stunner01@awesomewell.co.kr |
| 글로벌 진출 | ❌ 해외 운영 흔적 없음. 한국어 페이지만 존재 |

### 2.4 제품 라인업 (awesomecool.co.kr 자사몰)

- 어썸쿨 가글 600ml — 15,900원 (소비자가의 50% 할인 일관 적용)
- 어썸쿨 오라후레쉬 구강유산균 60정 — 29,800원
- 어썸쿨 버블치약 150ml — 15,900원
- 혀클리너, 칫솔, 인사밸런스 보조제 등

광고 카피: "30초면 구강관리 이걸로 끝!", "10,000개 초미세모". **임상 인용 부재**, **식약처 의약외품 표기 페이지 미노출**, **JSON-LD 미발견**, 검증 신호는 **고객 리뷰 6,478~7,243건** (기성품 인플루언서 마케팅 채널의 전형).

## 3. 결론

### 3.1 원래 전제 ("글로벌 가글 브랜드 어썸쿨") = **거짓**

- 어썸쿨은 **한국 도메스틱 D2C 브랜드**, 모회사는 **(주)스터너즈**(2021 통신판매업 등록한 신생 한국 e-commerce 운영사)
- 영문 검색 결과 0건, 글로벌 channel(Amazon US/UK, iHerb 글로벌 등) 진출 흔적 없음
- "일부 한국 자료에서 글로벌 가글로 언급" — 이는 **마케팅 카피의 과장 또는 정보 오류**일 가능성 높음 (영어 단어 "Awesome Cool"을 글로벌처럼 보이게 하는 작명 전략)

### 3.2 비슷한 이름 브랜드와의 혼동 매핑

| 이름 | 실재? | 정체 |
|------|------|------|
| 어썸쿨 (AwesomeCool) | ✅ | 한국 D2C, (주)스터너즈 운영 |
| 어썸가글 | 🔍 | 본 검색에서 별도 브랜드로 매칭 없음 |
| Awesome 가글 | 🔍 | 영문 글로벌 가글 브랜드로 매칭 없음 |
| 어썸코리아 | ✅ | 별도 회사 (나무위키 항목 존재). 어썸쿨과 다른 법인 — 혼동 주의 |
| 어썸라이프 (awesomelife.kr) | ✅ | 어썸쿨과 같은 법인((주)스터너즈)이 운영하는 다른 자사몰 |
| 어썸웰 (awesomewell.co.kr) | ✅ | 같은 법인 이메일 도메인. 형제 브랜드 |
| 어썸샷 | ✅ | 같은 법인의 운동용품 브랜드 |
| 쿨티아 (cooltia.com) | ✅ | 다른 한국 가글 브랜드. **어썸쿨과 혼동 금지** |

→ **(주)스터너즈는 "어썸X" 패밀리 브랜드를 다수 운영하는 한국 D2C 회사**. 글로벌 가글 브랜드 아님.

## 4. 적층 결정

- ❌ **글로벌 경쟁사 풀에 적층하지 않음** — 원래 전제(글로벌 브랜드)가 거짓이므로
- ❌ docs/knowledge/competitors/awesome_cool.md 파일 생성 안 함
- ⚠️ **만약 한국 도메스틱 D2C 가글 풀에 추가하고 싶다면 별도 의뢰** — 그땐 가그린/페리오/2080처럼 한국 도메스틱 카테고리에 분류 필요. 본 의뢰의 "글로벌 3강" 프레임에는 부적합

## 5. 교훈 (Wayne 메모리 적층용 후보)

기존 [feedback_url_verification.md](~/.claude/.../memory/feedback_url_verification.md) 원칙의 **확장**:

> 경쟁사 공식 URL은 검색·캐시 추정 금지, 1차 출처 확인 후 적층 (퓨런 furenhealth.com 오류 사례)

**확장**: 브랜드의 **카테고리 자체**(글로벌 vs 도메스틱)도 1차 출처 확인 필요. "일부 한국 자료에 글로벌로 언급"은 충분 조건 X. **영문 검색 결과 + 글로벌 채널 진출 흔적**까지 cross-reference 해야 "글로벌 브랜드"로 분류 가능.

본 사례에서 영문 검색 0건 + 회사 정보 한국 D2C로 명확 → 즉시 reject.

## 6. 후속 액션

- [ ] Wayne 의뢰에 회신: 어썸쿨은 글로벌 X, 한국 D2C. 글로벌 3번째 자리에 다른 브랜드(예: Crest Pro-Health, Sensodyne Mouthwash, Oral-B mouthwash) 후보 제안
- [ ] 만약 "한국 D2C 신생 가글 브랜드 풀"이라는 별도 트랙이 필요하면 어썸쿨 + 쿨티아 + 빠이러스 + 덴클 등 묶어서 별도 적층

## 참고 링크 (검증에 사용된 1차 출처)

- [어썸쿨 자사몰 회사 정보](https://awesomecool.co.kr/shopinfo/company.html) — (주)스터너즈 사업자 정보 1차 출처
- [어썸쿨 자사몰 메인](https://awesomecool.co.kr/) — 제품 라인업 + 광고 카피
- [어썸라이프 (자매 자사몰)](https://awesomelife.kr/category/%EC%96%B4%EC%8D%B8%EC%BF%A8/45/)
- [어썸코리아 나무위키](https://namu.wiki/w/%EC%96%B4%EC%8D%B8%EC%BD%94%EB%A6%AC%EC%95%84) — 동명이가 회사 (혼동 주의)
- [쿨티아](https://cooltia.com/) — 별개 한국 프로폴리스 가글 (혼동 주의)
