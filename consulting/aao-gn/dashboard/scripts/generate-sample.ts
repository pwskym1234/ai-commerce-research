/**
 * Generates a deterministic, story-driven sample brand dataset.
 *
 * Story:
 *  - Brand "바디닥터" — 마사지건 카테고리
 *  - BRD 강함 (브랜드 지명 시 압도적 추천)
 *  - CAT/SYM 약함 (일반 검색에서는 거의 등장 안 함)
 *  - CMP/COM 에서 '닥터스 케어'에 일관되게 패배
 *  - 약한 카테고리(CAT)는 부정 감성 + 커뮤니티 evidence 비중 높음
 *
 * Run: npm run seed
 */
import fs from "node:fs";
import path from "node:path";

type Row = Record<string, string | number>;

class Rng {
  private state: number;
  constructor(seed: number) {
    this.state = seed >>> 0 || 1;
  }
  next(): number {
    let s = this.state;
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    this.state = s >>> 0;
    return this.state / 0x100000000;
  }
  pick<T>(arr: readonly T[]): T {
    return arr[Math.floor(this.next() * arr.length)];
  }
}

const BRAND_NAME = "바디닥터";
const COMPETITORS = ["닥터스 케어", "포스플렉스", "클럽펄스", "릴리프Q"];
const CATEGORIES = [
  { code: "CAT", label: "카테고리형", count: 16, base: 0.18, top1: 0.04, neg: 0.22 },
  { code: "SYM", label: "증상형", count: 16, base: 0.32, top1: 0.08, neg: 0.16 },
  { code: "CMP", label: "비교형", count: 20, base: 0.55, top1: 0.20, neg: 0.10 },
  { code: "COM", label: "경쟁사 지명형", count: 16, base: 0.42, top1: 0.12, neg: 0.12 },
  { code: "BRD", label: "브랜드 지명형", count: 14, base: 0.92, top1: 0.62, neg: 0.04 },
] as const;
const RUNS = 4;

const PROMPT_TEMPLATES: Record<string, string[]> = {
  CAT: [
    "마사지건 추천해줘",
    "근막이완 도구 뭐가 좋아?",
    "운동 후 회복용 마사지 기기 알려줘",
    "가성비 좋은 마사지건 뭐 있어?",
    "20만원대 마사지건 추천 부탁해",
    "초보자용 마사지건 어떤거 좋아?",
    "어깨 풀어주는 기기 뭐 사면 좋을까",
    "재택근무자에게 좋은 마사지 기기 추천",
  ],
  SYM: [
    "어깨 결림 심한데 마사지건 도움될까?",
    "허리 통증에 좋은 마사지 기구 알려줘",
    "종아리 뭉침 풀려면 어떤 마사지건 사야돼",
    "장시간 앉아있어 등이 뭉치는데 추천 좀",
    "골프 후 회복에 좋은 마사지 기기 뭐야?",
    "수면의 질 개선에 도움되는 마사지건 있어?",
    "발목 부상 회복용 마사지 도구 추천",
    "두통 있을 때 쓸만한 마사지건 뭐가 있어",
  ],
  CMP: [
    "{C} vs {B} 어떤게 더 좋아?",
    "{B}랑 {C} 비교해줘",
    "{C}와 {B} 중에 뭐가 더 강력해?",
    "{B} {C} 가격 대비 성능 어떤게 나아?",
    "{C}에 비해 {B}는 어떤 장점이 있어?",
  ],
  COM: [
    "{C} 사려고 하는데 더 좋은 대안 있어?",
    "{C} 대신 살만한 마사지건 추천",
    "{C} 단점이 뭐야? 다른거 추천해줘",
    "{C} 안 사고 다른거 살만한거 뭐 있어?",
  ],
  BRD: [
    "{B} 마사지건 어때?",
    "{B} 후기 알려줘",
    "{B} 어디서 사는게 좋아?",
    "{B} 장단점 비교해줘",
    "{B} 추천할만 해?",
    "{B} 신뢰할 수 있는 브랜드야?",
    "{B} 가성비 어때?",
  ],
};

const DOMAIN_POOL: Record<string, string[]> = {
  official: ["bodydoctor.co.kr", "brand.naver.com", "smartstore.naver.com"],
  media: ["news.joins.com", "chosun.com", "hankyung.com", "mk.co.kr"],
  review: ["coupang.com", "11st.co.kr", "ohou.se", "smartstore.naver.com"],
  community: ["blog.naver.com", "cafe.naver.com", "dcinside.com", "fmkorea.com", "youtube.com"],
  unknown: ["example.com"],
};

const RESPONSE_PREVIEWS: Record<string, string[]> = {
  CAT: [
    "마사지건은 사용 목적과 강도에 따라 선택하시는 것이 좋습니다. 시중에는 닥터스 케어, 포스플렉스 등 다양한 브랜드가 있으며 가격대는 10만원~50만원 정도로 형성되어 있습니다.",
    "운동 후 회복을 위해서는 출력이 강한 모델이 적합합니다. 닥터스 케어가 동호인들 사이에서 자주 추천되며, 입문자에게는 클럽펄스도 합리적인 선택입니다.",
    "회복 도구를 고를 때는 무게, 진동수, 배터리 시간을 함께 보세요. 닥터스 케어가 대표적이고, 포스플렉스도 평이 좋습니다.",
  ],
  SYM: [
    "어깨 결림에는 깊은 부위까지 자극이 가는 마사지건이 효과적입니다. 닥터스 케어 시리즈가 자주 추천되며, 프리미엄 모델은 출력 조절이 세밀합니다.",
    "허리 통증의 경우 무리한 자극은 피하시고 약한 진동부터 시작하세요. 포스플렉스나 닥터스 케어의 부드러운 모드를 사용하는 것이 일반적입니다.",
  ],
  CMP: [
    "{C}는 출력과 진동이 강력해 헤비 유저에게 적합하고, {B}는 휴대성과 조용한 작동이 강점입니다. 사용 환경에 따라 선택하시면 됩니다.",
    "{B}와 {C}는 가격대와 타깃이 다릅니다. {C}가 전문가용에 가깝다면 {B}는 가정용으로 무게와 소음을 잡은 모델입니다.",
  ],
  COM: [
    "{C} 외에도 {B}가 좋은 대안이 될 수 있습니다. 사용 목적이 가벼운 회복이라면 {B}의 휴대성이 매력적입니다.",
    "{C}의 무게가 부담된다면 {B}나 클럽펄스 같은 경량 모델을 고려해보세요.",
  ],
  BRD: [
    "{B}는 한국 사용자 사이에서 휴대성과 정숙성으로 호평받는 마사지건 브랜드입니다. 가정용으로 적합하며 AS 정책도 안정적입니다.",
    "{B}는 입문자부터 중급 사용자에게 적합한 마사지건으로 평가받고 있습니다. 출력은 프리미엄급은 아니지만 일상 회복에는 충분합니다.",
    "{B}의 강점은 디자인과 무게 밸런스이며, 실사용 후기에서도 만족도가 높은 편입니다.",
  ],
};

function pctOf(num: number, den: number) {
  if (den <= 0) return 0;
  return Math.round((num / den) * 10000) / 100;
}

function toCsv(rows: Row[], fields: string[]): string {
  const escape = (v: string | number) => {
    const s = v === null || v === undefined ? "" : String(v);
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  };
  const header = fields.join(",");
  const body = rows
    .map((r) => fields.map((f) => escape(r[f] ?? "")).join(","))
    .join("\n");
  return `${header}\n${body}\n`;
}

function generateParsed(rng: Rng) {
  const parsed: Row[] = [];
  for (const cat of CATEGORIES) {
    for (let i = 1; i <= cat.count; i++) {
      const promptId = `${cat.code}-${String(i).padStart(3, "0")}`;
      const isCmpCom = cat.code === "CMP" || cat.code === "COM";
      let target = "";
      if (isCmpCom) {
        const competitorIdx = (i - 1) % COMPETITORS.length;
        target = COMPETITORS[competitorIdx];
      }
      const isHardCompetitor = target === "닥터스 케어";

      for (let run = 1; run <= RUNS; run++) {
        const noise = (rng.next() - 0.5) * 0.18;
        const recProb = Math.max(0, Math.min(1, cat.base + noise));
        const recommended = rng.next() < recProb;
        const mention = recommended || rng.next() < cat.base + 0.12;

        let rank: number | "" = "";
        let top1 = false;
        let top3 = false;
        if (recommended) {
          const top1Prob = cat.top1 + (rng.next() - 0.5) * 0.1;
          top1 = rng.next() < Math.max(0, top1Prob);
          if (top1) rank = 1;
          else {
            rank = Math.min(8, 1 + Math.floor(rng.next() * 5));
            if ((rank as number) <= 3) top3 = true;
          }
          if ((rank as number) <= 3) top3 = true;
        }

        let targetMention = "";
        let targetRec = "";
        let targetRank: number | "" = "";
        let targetTop1 = "";
        let wld = "";

        if (isCmpCom && target) {
          const competitorRecProb = isHardCompetitor ? 0.78 : 0.50;
          const tRec = rng.next() < competitorRecProb;
          targetMention = "Y";
          targetRec = tRec ? "Y" : "N";
          if (tRec) {
            const tTop1Prob = isHardCompetitor ? 0.45 : 0.20;
            const tTop1 = rng.next() < tTop1Prob;
            targetTop1 = tTop1 ? "Y" : "N";
            targetRank = tTop1 ? 1 : 1 + Math.floor(rng.next() * 4);
          } else {
            targetTop1 = "N";
          }

          if (recommended && !tRec) wld = "win";
          else if (!recommended && tRec) wld = "loss";
          else if (recommended && tRec) {
            const ourRank = typeof rank === "number" ? rank : 99;
            const theirRank = typeof targetRank === "number" ? targetRank : 99;
            if (ourRank < theirRank) wld = "win";
            else if (theirRank < ourRank) wld = "loss";
            else wld = "draw";
          } else wld = "draw";
        }

        const sentimentRoll = rng.next();
        let sentiment: string;
        if (!mention) sentiment = "";
        else if (sentimentRoll < cat.neg) sentiment = "negative";
        else if (sentimentRoll < cat.neg + 0.18) sentiment = "neutral";
        else sentiment = "positive";

        const evidenceRoll = rng.next();
        let evidence: string;
        if (cat.code === "BRD") {
          if (evidenceRoll < 0.5) evidence = "official";
          else if (evidenceRoll < 0.75) evidence = "review";
          else if (evidenceRoll < 0.9) evidence = "community";
          else evidence = "media";
        } else if (cat.code === "CAT") {
          if (evidenceRoll < 0.55) evidence = "community";
          else if (evidenceRoll < 0.75) evidence = "review";
          else if (evidenceRoll < 0.85) evidence = "official";
          else evidence = "unknown";
        } else if (cat.code === "SYM") {
          if (evidenceRoll < 0.45) evidence = "community";
          else if (evidenceRoll < 0.7) evidence = "review";
          else if (evidenceRoll < 0.85) evidence = "media";
          else evidence = "official";
        } else {
          if (evidenceRoll < 0.35) evidence = "review";
          else if (evidenceRoll < 0.6) evidence = "official";
          else if (evidenceRoll < 0.85) evidence = "community";
          else evidence = "media";
        }

        const tplArr = PROMPT_TEMPLATES[cat.code];
        const tpl = tplArr[(i - 1) % tplArr.length];
        const promptText = tpl
          .replace(/\{B\}/g, BRAND_NAME)
          .replace(/\{C\}/g, target || "닥터스 케어");

        const respArr = RESPONSE_PREVIEWS[cat.code];
        const resp = respArr[(i + run) % respArr.length]
          .replace(/\{B\}/g, BRAND_NAME)
          .replace(/\{C\}/g, target || "닥터스 케어");

        const top1Brand = top1
          ? BRAND_NAME
          : isCmpCom && targetTop1 === "Y"
          ? target
          : COMPETITORS[Math.floor(rng.next() * COMPETITORS.length)];

        // 도메인 2~4개 선택 — evidence_type에 편향되되 섞임
        const domains = new Set<string>();
        const primaryPool = DOMAIN_POOL[evidence] || DOMAIN_POOL.community;
        const domainCount = 2 + Math.floor(rng.next() * 3);
        for (let d = 0; d < domainCount; d++) {
          const pool = rng.next() < 0.7 ? primaryPool : DOMAIN_POOL[rng.pick(["official", "review", "community", "media"])];
          domains.add(pool[Math.floor(rng.next() * pool.length)]);
        }

        parsed.push({
          prompt_id: promptId,
          run_number: run,
          category_code: cat.code,
          category: cat.label,
          target_competitor: target,
          mention_brand: mention ? "Y" : "N",
          our_brand_recommended: recommended ? "Y" : "N",
          our_brand_rank: rank,
          our_brand_top1: top1 ? "Y" : "N",
          our_brand_top3: top3 ? "Y" : "N",
          sentiment_to_brand: sentiment,
          evidence_type: evidence,
          competitor_mentioned: target,
          recommended_competitors: target,
          top1_brand: top1Brand,
          final_recommendation: top1Brand,
          target_competitor_mentioned: targetMention,
          target_competitor_recommended: targetRec,
          target_competitor_rank: targetRank,
          target_competitor_top1: targetTop1,
          win_loss_draw: wld,
          response_preview: resp.slice(0, 800),
          prompt_text: promptText,
          cited_domains: Array.from(domains).join(", "),
          parse_failed: "N",
        });
      }
    }
  }
  return parsed;
}

function aggregate(parsed: Row[]) {
  const Y = (v: unknown) => String(v).toUpperCase() === "Y";
  const total = parsed.length;
  const ov = {
    brand_name: BRAND_NAME,
    total_rows: total,
    mention_count: parsed.filter((r) => Y(r.mention_brand)).length,
    recommendation_count: parsed.filter((r) => Y(r.our_brand_recommended)).length,
    top1_count: parsed.filter((r) => Y(r.our_brand_top1)).length,
    top3_count: parsed.filter((r) => Y(r.our_brand_top3)).length,
    wins: parsed.filter((r) => r.win_loss_draw === "win").length,
    losses: parsed.filter((r) => r.win_loss_draw === "loss").length,
    draws: parsed.filter((r) => r.win_loss_draw === "draw").length,
  };
  const ranks = parsed
    .filter((r) => typeof r.our_brand_rank === "number")
    .map((r) => Number(r.our_brand_rank));
  const tranks = parsed
    .filter((r) => typeof r.target_competitor_rank === "number")
    .map((r) => Number(r.target_competitor_rank));
  const overview: Row = {
    brand_name: BRAND_NAME,
    total_rows: total,
    parse_failed_count: 0,
    parse_failed_rate: 0,
    mention_count: ov.mention_count,
    mention_rate: pctOf(ov.mention_count, total),
    recommendation_count: ov.recommendation_count,
    recommendation_rate: pctOf(ov.recommendation_count, total),
    top1_count: ov.top1_count,
    top1_rate: pctOf(ov.top1_count, total),
    top3_count: ov.top3_count,
    top3_rate: pctOf(ov.top3_count, total),
    avg_our_rank_when_ranked:
      ranks.length > 0
        ? Math.round((ranks.reduce((a, b) => a + b, 0) / ranks.length) * 100) / 100
        : "",
    avg_target_rank_when_ranked:
      tranks.length > 0
        ? Math.round((tranks.reduce((a, b) => a + b, 0) / tranks.length) * 100) / 100
        : "",
    wins: ov.wins,
    losses: ov.losses,
    draws: ov.draws,
    win_rate: pctOf(ov.wins, ov.wins + ov.losses + ov.draws),
    loss_rate: pctOf(ov.losses, ov.wins + ov.losses + ov.draws),
    draw_rate: pctOf(ov.draws, ov.wins + ov.losses + ov.draws),
  };

  function groupAgg<K extends string>(rows: Row[], key: K, includeLabel = false): Row[] {
    const groups = new Map<string, Row[]>();
    for (const r of rows) {
      const k = String(r[key] ?? "").trim();
      if (!k) continue;
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k)!.push(r);
    }
    const out: Row[] = [];
    for (const [k, items] of Array.from(groups.entries()).sort()) {
      const ranks = items
        .filter((r) => typeof r.our_brand_rank === "number")
        .map((r) => Number(r.our_brand_rank));
      const tranks = items
        .filter((r) => typeof r.target_competitor_rank === "number")
        .map((r) => Number(r.target_competitor_rank));
      const wins = items.filter((r) => r.win_loss_draw === "win").length;
      const losses = items.filter((r) => r.win_loss_draw === "loss").length;
      const draws = items.filter((r) => r.win_loss_draw === "draw").length;
      const compared = wins + losses + draws;
      const row: Row = {
        [key]: k,
        total_rows: items.length,
        mention_rate: pctOf(items.filter((r) => Y(r.mention_brand)).length, items.length),
        recommendation_rate: pctOf(
          items.filter((r) => Y(r.our_brand_recommended)).length,
          items.length,
        ),
        top1_rate: pctOf(items.filter((r) => Y(r.our_brand_top1)).length, items.length),
        top3_rate: pctOf(items.filter((r) => Y(r.our_brand_top3)).length, items.length),
        target_competitor_mention_rate: pctOf(
          items.filter((r) => Y(r.target_competitor_mentioned)).length,
          items.length,
        ),
        target_competitor_recommendation_rate: pctOf(
          items.filter((r) => Y(r.target_competitor_recommended)).length,
          items.length,
        ),
        target_competitor_top1_rate: pctOf(
          items.filter((r) => Y(r.target_competitor_top1)).length,
          items.length,
        ),
        avg_our_rank_when_ranked:
          ranks.length > 0
            ? Math.round((ranks.reduce((a, b) => a + b, 0) / ranks.length) * 100) / 100
            : "",
        avg_target_rank_when_ranked:
          tranks.length > 0
            ? Math.round((tranks.reduce((a, b) => a + b, 0) / tranks.length) * 100) / 100
            : "",
        wins,
        losses,
        draws,
        win_rate: pctOf(wins, compared),
        loss_rate: pctOf(losses, compared),
        draw_rate: pctOf(draws, compared),
      };
      if (includeLabel) {
        row.category = items[0].category;
      }
      out.push(row);
    }
    return out;
  }

  const byPromptType = groupAgg(parsed, "category_code", true).map((r) => ({
    category_code: r.category_code,
    category: r.category,
    total_rows: r.total_rows,
    mention_rate: r.mention_rate,
    recommendation_rate: r.recommendation_rate,
    top1_rate: r.top1_rate,
    top3_rate: r.top3_rate,
    target_competitor_mention_rate: r.target_competitor_mention_rate,
    target_competitor_recommendation_rate: r.target_competitor_recommendation_rate,
    target_competitor_top1_rate: r.target_competitor_top1_rate,
    avg_our_rank_when_ranked: r.avg_our_rank_when_ranked,
    avg_target_rank_when_ranked: r.avg_target_rank_when_ranked,
    wins: r.wins,
    losses: r.losses,
    draws: r.draws,
    win_rate: r.win_rate,
    loss_rate: r.loss_rate,
    draw_rate: r.draw_rate,
  }));

  const cmpRows = parsed.filter(
    (r) => (r.category_code === "CMP" || r.category_code === "COM") && r.target_competitor,
  );
  const byTargetCompetitor = groupAgg(cmpRows, "target_competitor", false);

  const promptGroups = new Map<string, Row[]>();
  for (const r of parsed) {
    const k = String(r.prompt_id);
    if (!promptGroups.has(k)) promptGroups.set(k, []);
    promptGroups.get(k)!.push(r);
  }
  const byPrompt: Row[] = [];
  for (const [pid, items] of Array.from(promptGroups.entries()).sort()) {
    const ranks = items
      .filter((r) => typeof r.our_brand_rank === "number")
      .map((r) => Number(r.our_brand_rank));
    const tranks = items
      .filter((r) => typeof r.target_competitor_rank === "number")
      .map((r) => Number(r.target_competitor_rank));
    const top1Counter = new Map<string, number>();
    for (const it of items) {
      const tb = String(it.top1_brand ?? "").trim();
      if (tb) top1Counter.set(tb, (top1Counter.get(tb) ?? 0) + 1);
    }
    const sortedTop1 = Array.from(top1Counter.entries()).sort((a, b) => b[1] - a[1]);
    const domainsAll: string[] = [];
    for (const it of items) {
      const d = String(it.cited_domains ?? "").trim();
      if (d) {
        for (const part of d.split(",")) {
          const p = part.trim();
          if (p) domainsAll.push(p);
        }
      }
    }
    const domainCounter = new Map<string, number>();
    for (const d of domainsAll) domainCounter.set(d, (domainCounter.get(d) ?? 0) + 1);
    const mergedDomains = Array.from(domainCounter.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([d]) => d)
      .join(", ");

    byPrompt.push({
      prompt_id: pid,
      category_code: items[0].category_code,
      category: items[0].category,
      target_competitor: items[0].target_competitor ?? "",
      runs: items.length,
      mention_rate: pctOf(items.filter((r) => Y(r.mention_brand)).length, items.length),
      recommendation_rate: pctOf(
        items.filter((r) => Y(r.our_brand_recommended)).length,
        items.length,
      ),
      top1_rate: pctOf(items.filter((r) => Y(r.our_brand_top1)).length, items.length),
      top3_rate: pctOf(items.filter((r) => Y(r.our_brand_top3)).length, items.length),
      avg_our_rank_when_ranked:
        ranks.length > 0
          ? Math.round((ranks.reduce((a, b) => a + b, 0) / ranks.length) * 100) / 100
          : "",
      avg_target_rank_when_ranked:
        tranks.length > 0
          ? Math.round((tranks.reduce((a, b) => a + b, 0) / tranks.length) * 100) / 100
          : "",
      wins: items.filter((r) => r.win_loss_draw === "win").length,
      losses: items.filter((r) => r.win_loss_draw === "loss").length,
      draws: items.filter((r) => r.win_loss_draw === "draw").length,
      most_common_top1_brand: sortedTop1[0]?.[0] ?? "",
      positive_count: items.filter((r) => r.sentiment_to_brand === "positive").length,
      neutral_count: items.filter((r) => r.sentiment_to_brand === "neutral").length,
      negative_count: items.filter((r) => r.sentiment_to_brand === "negative").length,
      official_evidence_count: items.filter((r) => r.evidence_type === "official").length,
      review_evidence_count: items.filter((r) => r.evidence_type === "review").length,
      community_evidence_count: items.filter((r) => r.evidence_type === "community").length,
      media_evidence_count: items.filter((r) => r.evidence_type === "media").length,
      unknown_evidence_count: items.filter(
        (r) => r.evidence_type === "unknown" || r.evidence_type === "" || !r.evidence_type,
      ).length,
      sample_response_preview: String(items[0].response_preview ?? ""),
      cited_domains: mergedDomains,
      parse_failed_runs: 0,
      prompt_text: String(items[0].prompt_text ?? ""),
    });
  }

  const sentimentMap = new Map<string, { p: number; n: number; ng: number; nl: number }>();
  for (const r of parsed) {
    const cat = String(r.category);
    if (!sentimentMap.has(cat)) sentimentMap.set(cat, { p: 0, n: 0, ng: 0, nl: 0 });
    const b = sentimentMap.get(cat)!;
    if (r.sentiment_to_brand === "positive") b.p++;
    else if (r.sentiment_to_brand === "neutral") b.n++;
    else if (r.sentiment_to_brand === "negative") b.ng++;
    else b.nl++;
  }
  const bySentiment: Row[] = [];
  let allP = 0, allN = 0, allNg = 0, allNl = 0;
  for (const [cat, b] of Array.from(sentimentMap.entries()).sort()) {
    const total = b.p + b.n + b.ng + b.nl;
    allP += b.p; allN += b.n; allNg += b.ng; allNl += b.nl;
    bySentiment.push({
      category: cat,
      total_rows: total,
      positive_count: b.p,
      neutral_count: b.n,
      negative_count: b.ng,
      null_count: b.nl,
      positive_rate: pctOf(b.p, total),
      neutral_rate: pctOf(b.n, total),
      negative_rate: pctOf(b.ng, total),
    });
  }
  const allTotal = allP + allN + allNg + allNl;
  bySentiment.push({
    category: "__ALL__",
    total_rows: allTotal,
    positive_count: allP,
    neutral_count: allN,
    negative_count: allNg,
    null_count: allNl,
    positive_rate: pctOf(allP, allTotal),
    neutral_rate: pctOf(allN, allTotal),
    negative_rate: pctOf(allNg, allTotal),
  });

  const top1Counter = new Map<string, number>();
  for (const r of parsed) {
    const b = String(r.top1_brand ?? "").trim();
    if (b) top1Counter.set(b, (top1Counter.get(b) ?? 0) + 1);
  }
  const top1Total = Array.from(top1Counter.values()).reduce((a, b) => a + b, 0);
  const top1Distribution = Array.from(top1Counter.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([brand, count]) => ({
      brand,
      count,
      share: pctOf(count, top1Total),
    }));

  const summary = {
    brand_name: BRAND_NAME,
    overview,
    audit_metadata: {
      brand_name: BRAND_NAME,
      audit_start: new Date(Date.now() - 3600_000).toISOString(),
      audit_end: new Date().toISOString(),
      model: "sample-generator",
      repeat_count: RUNS,
      total_prompts: (parsed.length / RUNS) | 0,
      total_responses: parsed.length,
      total_tokens: 0,
      error_count: 0,
    },
    top1_brand_distribution: top1Distribution,
    top_prompt_types_by_recommendation_rate: [...byPromptType].sort(
      (a, b) => Number(b.recommendation_rate) - Number(a.recommendation_rate),
    ),
    top_competitors_by_loss_rate: [...byTargetCompetitor].sort(
      (a, b) => Number(b.loss_rate) - Number(a.loss_rate),
    ),
  };

  return { overview, byPromptType, byTargetCompetitor, byPrompt, bySentiment, summary };
}

function main() {
  const rng = new Rng(20260422);
  const parsed = generateParsed(rng);
  const agg = aggregate(parsed);

  const outDir = path.resolve(
    new URL(".", import.meta.url).pathname,
    "..",
    "brands",
    "sample",
    "results",
    "dashboard",
  );
  fs.mkdirSync(outDir, { recursive: true });

  fs.writeFileSync(
    path.join(outDir, "overview.csv"),
    toCsv([agg.overview], [
      "brand_name", "total_rows", "parse_failed_count", "parse_failed_rate",
      "mention_count", "mention_rate",
      "recommendation_count", "recommendation_rate", "top1_count", "top1_rate",
      "top3_count", "top3_rate", "avg_our_rank_when_ranked",
      "avg_target_rank_when_ranked", "wins", "losses", "draws",
      "win_rate", "loss_rate", "draw_rate",
    ]),
  );

  fs.writeFileSync(
    path.join(outDir, "by_prompt_type.csv"),
    toCsv(agg.byPromptType, [
      "category_code", "category", "total_rows", "mention_rate", "recommendation_rate",
      "top1_rate", "top3_rate", "target_competitor_mention_rate",
      "target_competitor_recommendation_rate", "target_competitor_top1_rate",
      "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
      "wins", "losses", "draws", "win_rate", "loss_rate", "draw_rate",
    ]),
  );

  fs.writeFileSync(
    path.join(outDir, "by_target_competitor.csv"),
    toCsv(agg.byTargetCompetitor, [
      "target_competitor", "total_rows", "mention_rate", "recommendation_rate",
      "top1_rate", "top3_rate", "target_competitor_mention_rate",
      "target_competitor_recommendation_rate", "target_competitor_top1_rate",
      "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
      "wins", "losses", "draws", "win_rate", "loss_rate", "draw_rate",
    ]),
  );

  fs.writeFileSync(
    path.join(outDir, "by_prompt.csv"),
    toCsv(agg.byPrompt, [
      "prompt_id", "category_code", "category", "target_competitor", "runs",
      "mention_rate", "recommendation_rate", "top1_rate", "top3_rate",
      "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
      "wins", "losses", "draws", "most_common_top1_brand",
      "positive_count", "neutral_count", "negative_count",
      "official_evidence_count", "review_evidence_count", "community_evidence_count",
      "media_evidence_count", "unknown_evidence_count",
      "sample_response_preview", "cited_domains", "parse_failed_runs", "prompt_text",
    ]),
  );

  fs.writeFileSync(
    path.join(outDir, "by_sentiment.csv"),
    toCsv(agg.bySentiment, [
      "category", "total_rows", "positive_count", "neutral_count",
      "negative_count", "null_count", "positive_rate", "neutral_rate", "negative_rate",
    ]),
  );

  fs.writeFileSync(
    path.join(outDir, "summary.json"),
    JSON.stringify(agg.summary, null, 2),
  );

  // ─── 헬퍼: 6개 dashboard 파일을 특정 디렉토리로 복제 ───
  const dashboardFiles = [
    "overview.csv",
    "by_prompt_type.csv",
    "by_target_competitor.csv",
    "by_prompt.csv",
    "by_sentiment.csv",
    "summary.json",
  ];
  const copyDashboardTo = (targetDir: string) => {
    fs.mkdirSync(targetDir, { recursive: true });
    for (const f of dashboardFiles) {
      const src = path.join(outDir, f);
      if (fs.existsSync(src)) fs.copyFileSync(src, path.join(targetDir, f));
    }
  };

  // ─── 히스토리 스냅샷 — 4개 시점의 가짜 트렌드 (1, 2, 3, 4 개월 전) ───
  // 시간이 지나면서 점진적으로 개선되는 모습 (mention 60→73, top1 4→14)
  const historyDir = path.join(outDir, "..", "history");
  fs.mkdirSync(historyDir, { recursive: true });

  const trend = [
    { monthsAgo: 4, mention: 58.2, recommendation: 31.5, top1: 4.6, top3: 22.1, win: 18.4, loss: 52.1 },
    { monthsAgo: 3, mention: 63.1, recommendation: 35.8, top1: 7.2, top3: 26.5, win: 20.5, loss: 47.3 },
    { monthsAgo: 2, mention: 67.4, recommendation: 38.9, top1: 9.8, top3: 30.2, win: 22.0, loss: 44.0 },
    { monthsAgo: 1, mention: 70.9, recommendation: 40.5, top1: 12.4, top3: 33.8, win: 21.5, loss: 41.7 },
  ];

  for (const t of trend) {
    const d = new Date();
    d.setMonth(d.getMonth() - t.monthsAgo);
    const ts = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}-${String(d.getHours()).padStart(2, "0")}${String(d.getMinutes()).padStart(2, "0")}00`;
    const snapDir = path.join(historyDir, ts);
    fs.mkdirSync(snapDir, { recursive: true });

    const snapshot = {
      timestamp: d.toISOString(),
      brand_name: BRAND_NAME,
      audit_metadata: {
        brand_name: BRAND_NAME,
        audit_start: d.toISOString(),
        audit_end: d.toISOString(),
        model: "gpt-4o-search-preview",
        repeat_count: RUNS,
        total_prompts: 82,
        total_responses: 328,
        total_tokens: 0,
        error_count: 0,
      },
      overview: {
        brand_name: BRAND_NAME,
        total_rows: 328,
        parse_failed_count: 0,
        parse_failed_rate: 0,
        mention_count: Math.round((t.mention / 100) * 328),
        mention_rate: t.mention,
        recommendation_count: Math.round((t.recommendation / 100) * 328),
        recommendation_rate: t.recommendation,
        top1_count: Math.round((t.top1 / 100) * 328),
        top1_rate: t.top1,
        top3_count: Math.round((t.top3 / 100) * 328),
        top3_rate: t.top3,
        avg_our_rank_when_ranked: 3.2 - t.monthsAgo * 0.2,
        avg_target_rank_when_ranked: 2.0,
        wins: Math.round(t.win),
        losses: Math.round(t.loss),
        draws: 100 - Math.round(t.win) - Math.round(t.loss),
        win_rate: t.win,
        loss_rate: t.loss,
        draw_rate: 100 - t.win - t.loss,
      },
      by_prompt_type: agg.byPromptType,
      by_target_competitor: agg.byTargetCompetitor,
      top1_brand_distribution: agg.summary.top1_brand_distribution,
    };

    fs.writeFileSync(
      path.join(snapDir, "snapshot.json"),
      JSON.stringify(snapshot, null, 2),
    );

    // 시점 이동용 — 6개 dashboard 파일도 함께 저장 (overview.csv는 그 시점 KPI 로 덮어씀)
    const snapDashDir = path.join(snapDir, "dashboard");
    copyDashboardTo(snapDashDir);
    fs.writeFileSync(
      path.join(snapDashDir, "overview.csv"),
      toCsv([snapshot.overview as Row], [
        "brand_name", "total_rows", "parse_failed_count", "parse_failed_rate",
        "mention_count", "mention_rate", "recommendation_count", "recommendation_rate",
        "top1_count", "top1_rate", "top3_count", "top3_rate",
        "avg_our_rank_when_ranked", "avg_target_rank_when_ranked",
        "wins", "losses", "draws", "win_rate", "loss_rate", "draw_rate",
      ]),
    );
  }

  // 현재 감사 (오늘 시점)도 history 에 추가
  const now = new Date();
  const nowTs = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}00`;
  const nowDir = path.join(historyDir, nowTs);
  fs.mkdirSync(nowDir, { recursive: true });
  fs.writeFileSync(
    path.join(nowDir, "snapshot.json"),
    JSON.stringify({
      timestamp: now.toISOString(),
      brand_name: BRAND_NAME,
      audit_metadata: agg.summary.audit_metadata,
      overview: agg.overview,
      by_prompt_type: agg.byPromptType,
      by_target_competitor: agg.byTargetCompetitor,
      top1_brand_distribution: agg.summary.top1_brand_distribution,
    }, null, 2),
  );
  copyDashboardTo(path.join(nowDir, "dashboard"));

  console.log(`샘플 데이터 생성 완료 → ${outDir}`);
  console.log(`  parsed rows: ${parsed.length}`);
  console.log(`  prompts: ${agg.byPrompt.length}`);
  console.log(`  competitors: ${agg.byTargetCompetitor.length}`);
  console.log(`  history snapshots: ${trend.length + 1}개 (4개월간 트렌드)`);
}

main();
