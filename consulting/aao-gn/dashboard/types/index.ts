import { z } from "zod";

const numOrNull = z.preprocess((v) => {
  if (v === "" || v === null || v === undefined) return null;
  if (typeof v === "string" && v.trim() === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
}, z.number().nullable());

const num = z.preprocess((v) => {
  if (v === "" || v === null || v === undefined) return 0;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : 0;
}, z.number());

const str = z.preprocess((v) => {
  if (v === null || v === undefined) return "";
  return String(v);
}, z.string());

export const CategoryCode = z.enum(["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"]);
export type CategoryCode = z.infer<typeof CategoryCode>;

const categoryCodeLoose = z.preprocess(
  (v) => (typeof v === "string" ? v.toUpperCase().trim() : v),
  z.string(),
);

export const CategoryCardSchema = z.object({
  category_code: categoryCodeLoose,
  category: str,
  total_rows: num,
  primary_metric_label: str,
  primary_metric_value: num,
  primary_metric_count: num.optional().default(0),
  primary_metric_denom: num.optional().default(0),
  secondary_metric_label: str.optional().default(""),
  secondary_metric_value: num.optional().default(0),
  secondary_metric_count: num.optional().default(0),
  secondary_metric_denom: num.optional().default(0),
  extra_metric_label: str.optional().default(""),
  extra_metric_value: z
    .preprocess((v) => (v === null || v === undefined ? "" : String(v)), z.string())
    .optional()
    .default(""),
  // 보정 분모 — clarification_request / off_topic 케이스를 분모/분자에서 제외한 "유효 응답" 기준
  clarification_count: num.optional().default(0),
  off_topic_count: num.optional().default(0),
  effective_denom: num.optional().default(0),
  effective_primary_count: num.optional().default(0),
  effective_primary_value: num.optional().default(0),
  effective_secondary_count: num.optional().default(0),
  effective_secondary_value: num.optional().default(0),
  explain: str,
});
export type CategoryCard = z.infer<typeof CategoryCardSchema>;

export const H2HByCompetitorSchema = z.object({
  target_competitor: str,
  total_rows: num,
  wins: num,
  losses: num,
  draws: num,
  win_rate: num,
  loss_rate: num,
  draw_rate: num,
  avg_our_rank_when_ranked: numOrNull,
  avg_target_rank_when_ranked: numOrNull,
});
export type H2HByCompetitor = z.infer<typeof H2HByCompetitorSchema>;

export const CompOnlyByCompetitorSchema = z.object({
  target_competitor: str,
  total_rows: num,
  surfaced_count: num,
  co_mentioned_count: num,
  not_surfaced_count: num,
  surfaced_rate: num,
  co_mentioned_rate: num,
  not_surfaced_rate: num,
  avg_our_rank_when_ranked: numOrNull,
  avg_target_rank_when_ranked: numOrNull,
});
export type CompOnlyByCompetitor = z.infer<typeof CompOnlyByCompetitorSchema>;

export const ByPromptSchema = z.object({
  prompt_id: str,
  category_code: categoryCodeLoose,
  category: str,
  subcategory: str.optional().default(""),
  target_competitor: str.optional().default(""),
  runs: num,
  mention_count: num.optional().default(0),
  mention_rate: num,
  recommendation_count: num.optional().default(0),
  recommendation_rate: num,
  top1_count: num.optional().default(0),
  top1_rate: num,
  top3_count: num.optional().default(0),
  top3_rate: num,
  clarification_count: num.optional().default(0),
  off_topic_count: num.optional().default(0),
  evasion_count: num.optional().default(0),
  positive_count: num,
  neutral_count: num,
  negative_count: num,
  wins: num,
  losses: num,
  draws: num,
  surfaced_count: num,
  co_mentioned_count: num,
  not_surfaced_count: num,
  prompt_text: str.optional().default(""),
  sample_response_preview: str.optional().default(""),
});
export type ByPrompt = z.infer<typeof ByPromptSchema>;

export const ActionItemSchema = z.object({
  problem: str,
  hypothesis: str,
  actions: z.array(str).default([]),
});
export type ActionItem = z.infer<typeof ActionItemSchema>;

export const SpotlightEntrySchema = z.object({
  prompt_id: str,
  category_code: str,
  target_competitor: str.optional().default(""),
  prompt_text: str.optional().default(""),
  mention_rate: num.optional().default(0),
  recommendation_rate: num.optional().default(0),
  wins: num.optional().default(0),
  losses: num.optional().default(0),
  draws: num.optional().default(0),
  surfaced_count: num.optional().default(0),
  not_surfaced_count: num.optional().default(0),
  positive_count: num.optional().default(0),
  negative_count: num.optional().default(0),
});
export type SpotlightEntry = z.infer<typeof SpotlightEntrySchema>;

export const SpotlightsSchema = z.object({
  neutral_strong: z.array(SpotlightEntrySchema).default([]),
  neutral_weak: z.array(SpotlightEntrySchema).default([]),
  h2h_win: z.array(SpotlightEntrySchema).default([]),
  h2h_loss: z.array(SpotlightEntrySchema).default([]),
  comp_only_surfaced: z.array(SpotlightEntrySchema).default([]),
  comp_only_not_surfaced: z.array(SpotlightEntrySchema).default([]),
  brand_only_negative: z.array(SpotlightEntrySchema).default([]),
});
export type Spotlights = z.infer<typeof SpotlightsSchema>;

export const AuditMetadataSchema = z.object({
  brand_name: str.optional().default(""),
  audit_start: str.optional().default(""),
  audit_end: str.optional().default(""),
  model: str.optional().default(""),
  temperature: numOrNull.optional().default(null),
  seed_base: numOrNull.optional().default(null),
  seed_min: numOrNull.optional().default(null),
  seed_max: numOrNull.optional().default(null),
  repeat_count: num.optional().default(0),
  total_prompts: num.optional().default(0),
  total_calls: num.optional().default(0),
  total_responses: num.optional().default(0),
  total_tokens: num.optional().default(0),
  error_count: num.optional().default(0),
  max_workers: num.optional().default(0),
});
export type AuditMetadata = z.infer<typeof AuditMetadataSchema>;

export const NeutralBrandRowSchema = z.object({
  rank: num,
  brand: str,
  hit_count: num,
  share: num,
  is_ours: z.boolean().optional().default(false),
  is_known_competitor: z.boolean().optional().default(false),
  aliases: z.array(str).optional().default([]),
});
export type NeutralBrandRow = z.infer<typeof NeutralBrandRowSchema>;

export const NeutralBrandRankingSchema = z.object({
  brand_name: str,
  total_runs: num,
  distinct_prompts: num,
  our_brand_rank: numOrNull,
  our_brand_share: num,
  our_brand_hit_count: num,
  total_brands_detected: num,
  rows: z.array(NeutralBrandRowSchema).default([]),
});
export type NeutralBrandRanking = z.infer<typeof NeutralBrandRankingSchema>;

// Per-run 분류 결과 (parsed_results.csv 한 행)
export const ParsedRunSchema = z.object({
  prompt_id: str,
  run_number: num,
  category_code: str.optional().default(""),
  category: str.optional().default(""),
  subcategory: str.optional().default(""),
  target_competitor: str.optional().default(""),
  mention_brand: str.optional().default("N"),
  our_brand_recommended: str.optional().default("N"),
  our_brand_rank: numOrNull.optional().default(null),
  our_brand_top1: str.optional().default("N"),
  our_brand_top3: str.optional().default("N"),
  sentiment_to_brand: str.optional().default(""),
  competitor_mentioned: str.optional().default(""),
  recommended_competitors: str.optional().default(""),
  top1_brand: str.optional().default(""),
  final_recommendation: str.optional().default(""),
  target_competitor_mentioned: str.optional().default("N"),
  target_competitor_recommended: str.optional().default("N"),
  target_competitor_rank: numOrNull.optional().default(null),
  win_loss_draw: str.optional().default(""),
  surfacing_outcome: str.optional().default(""),
  cited_domains: str.optional().default(""),
  evasion: str.optional().default("N"),
  clarification_request: str.optional().default("N"),
  off_topic: str.optional().default("N"),
});
export type ParsedRun = z.infer<typeof ParsedRunSchema>;

// raw_responses.json 한 항목 (full text + citations)
export const RawResponseSchema = z.object({
  prompt_id: str,
  run_number: num,
  response: str.optional().default(""),
  citations: z
    .array(z.object({ url: str, title: str.optional().default("") }))
    .optional()
    .default([]),
});
export type RawResponse = z.infer<typeof RawResponseSchema>;

export const NeutralSubcategoryRowSchema = z.object({
  subcategory: str,
  subcategory_label: str.optional().default(""),
  total_rows: num,
  mention_count: num.optional().default(0),
  mention_rate: num,
  recommendation_count: num.optional().default(0),
  recommendation_rate: num,
  top1_count: num.optional().default(0),
  top1_rate: num,
});
export type NeutralSubcategoryRow = z.infer<typeof NeutralSubcategoryRowSchema>;

export const SummarySchema = z.object({
  brand_name: str,
  dashboard_mode: str.optional().default(""),
  category_cards: z.array(CategoryCardSchema).default([]),
  h2h_by_competitor: z.array(H2HByCompetitorSchema).default([]),
  comp_only_by_competitor: z.array(CompOnlyByCompetitorSchema).default([]),
  diagnostics: z.array(str).default([]),
  action_items: z.array(ActionItemSchema).default([]),
  spotlights: SpotlightsSchema.optional().default({
    neutral_strong: [],
    neutral_weak: [],
    h2h_win: [],
    h2h_loss: [],
    comp_only_surfaced: [],
    comp_only_not_surfaced: [],
    brand_only_negative: [],
  }),
  audit_metadata: AuditMetadataSchema.optional(),
  neutral_by_subcategory: z.array(NeutralSubcategoryRowSchema).optional().default([]),
});
export type Summary = z.infer<typeof SummarySchema>;
