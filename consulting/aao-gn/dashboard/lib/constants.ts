export const CATEGORY_LABELS: Record<string, string> = {
  NEUTRAL: "중립 질문",
  BRAND_ONLY: "브랜드 직접 질문",
  COMP_ONLY: "경쟁사 대안 질문",
  H2H: "직접 비교",
};

export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  NEUTRAL: "브랜드를 모르는 상태에서 카테고리·상황·고민을 묻는 질문",
  BRAND_ONLY: "우리 브랜드 이름을 직접 지목한 질문",
  COMP_ONLY: "경쟁사 이름을 지목해 대안/대체재를 찾는 질문",
  H2H: "우리 브랜드와 특정 경쟁사를 직접 비교하는 질문",
};

export const CATEGORY_ORDER = ["NEUTRAL", "BRAND_ONLY", "COMP_ONLY", "H2H"] as const;

export const LABELS: Record<string, string> = {
  mention_rate: "언급률",
  recommendation_rate: "추천률",
  top1_rate: "1순위 추천 비율",
  top3_rate: "상위 추천 진입률",
  win_rate: "승률",
  loss_rate: "패배율",
  draw_rate: "무승부율",
  surfaced_rate: "대안 소환율",
  co_mentioned_rate: "공동 언급률",
  not_surfaced_rate: "미노출률",
  positive_rate: "긍정 비율",
  neutral_rate: "중립 비율",
  negative_rate: "부정 비율",
  avg_our_rank_when_ranked: "소환 시 평균 순위",
  surfaced: "대안으로 등장",
  co_mentioned: "공동 언급",
  not_surfaced: "대안으로 안 나옴",
  win: "승리",
  loss: "패배",
  draw: "무승부",
  wins: "승리",
  losses: "패배",
  draws: "무승부",
  positive: "긍정",
  neutral: "중립",
  negative: "부정",
};

export const SECTIONS = [
  { id: "core-cards", label: "핵심 진단" },
  { id: "neutral", label: "중립 질문 성과" },
  { id: "brand-only", label: "브랜드 직접 질문" },
  { id: "comp-only", label: "경쟁사 대안 질문" },
  { id: "h2h", label: "직접 비교 성과" },
  { id: "action-items", label: "우선 개선 과제" },
  { id: "reference", label: "참고 자료" },
] as const;

export const SENTIMENT_COLORS = {
  positive: "#10b981",
  neutral: "#a1a1aa",
  negative: "#f43f5e",
  null: "#e4e4e7",
} as const;

export const CATEGORY_COLORS: Record<string, string> = {
  NEUTRAL: "#3b82f6",
  BRAND_ONLY: "#8b5cf6",
  COMP_ONLY: "#f59e0b",
  H2H: "#ef4444",
};
