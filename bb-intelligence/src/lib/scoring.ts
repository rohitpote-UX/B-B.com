/**
 * B&B Intelligence — Relevance Scoring Engine
 *
 * Scores research items against BrandBattle's relevance taxonomy.
 * Uses an explainable, configurable scoring model.
 *
 * Weights (configurable via env):
 *   BB relevance:      30%
 *   Evidence quality:  25%
 *   Business impact:   20%
 *   Timeliness:        15%
 *   Actionability:     10%
 *
 * IMPORTANT: This is a heuristic, not a factual verification system.
 * A high score does not mean a claim is verified.
 */

// ─── BrandBattle keyword taxonomy ────────────────────────────────────────────

const BB_KEYWORDS = {
  product_compare: [
    "vs", "versus", "comparison", "compare", "better", "which is better",
    "alternative", "difference between", "worth it", "should i buy",
  ],
  deal_intelligence: [
    "deal", "discount", "offer", "sale", "coupon", "cashback", "price drop",
    "cheapest", "lowest price", "best price", "festive offer",
  ],
  consumer_doubt: [
    "is it worth", "fake discount", "original price", "mrp", "genuine",
    "verified", "trust", "authentic", "reliable", "scam",
  ],
  ecommerce_platforms: [
    "amazon", "flipkart", "myntra", "ajio", "croma", "reliance digital",
    "tata cliq", "snapdeal", "meesho",
  ],
  product_categories: [
    "smartphone", "phone", "laptop", "earphone", "headphone", "smartwatch",
    "tablet", "camera", "tv", "television", "speaker", "charger", "power bank",
    "sneaker", "shoe", "watch", "bag", "clothing",
  ],
  consumer_electronics: [
    "iphone", "samsung", "oneplus", "redmi", "xiaomi", "realme", "oppo",
    "vivo", "nothing", "pixel", "macbook", "dell", "hp", "lenovo", "asus",
  ],
  indian_consumer: [
    "india", "indian", "rupee", "inr", "festive", "diwali", "big billion",
    "great indian", "monsoon sale", "exchange offer",
  ],
};

// ─── Scoring weights ──────────────────────────────────────────────────────────

type Weights = {
  relevance: number;
  evidence: number;
  impact: number;
  timeliness: number;
  actionability: number;
};

function getWeights(): Weights {
  return {
    relevance: 0.30,
    evidence: 0.25,
    impact: 0.20,
    timeliness: 0.15,
    actionability: 0.10,
  };
}

// ─── Main scoring function ────────────────────────────────────────────────────

export type ScoringResult = {
  total: number;
  breakdown: {
    relevance: number;
    evidence: number;
    impact: number;
    timeliness: number;
    actionability: number;
    matched_keywords: string[];
    category: string;
    explanation: string;
  };
};

export function scoreRelevance(
  text: string,
  sourceCategory = "general",
  publishedAt?: string
): ScoringResult {
  const lowerText = text.toLowerCase();
  const weights = getWeights();

  // ─── 1. BB Relevance Score ────────────────────────────────────────────────
  const matchedKeywords: string[] = [];
  let keywordMatchScore = 0;

  for (const [_group, keywords] of Object.entries(BB_KEYWORDS)) {
    for (const kw of keywords) {
      if (lowerText.includes(kw)) {
        matchedKeywords.push(kw);
        keywordMatchScore += 15;
      }
    }
  }

  // Category boost
  const categoryBoost: Record<string, number> = {
    product_launches: 15,
    consumer_tech: 10,
    deals: 20,
    ecommerce: 15,
    general: 0,
  };
  const catBoost = categoryBoost[sourceCategory] || 0;

  const relevanceScore = Math.min(100, keywordMatchScore + catBoost);

  // ─── 2. Evidence Quality Score ────────────────────────────────────────────
  // For RSS items, evidence quality is limited (text snippet only, no structured data)
  // Score is based on text length and source category
  const textLength = text.length;
  const evidenceScore = Math.min(100, (textLength / 500) * 40 + (sourceCategory !== "general" ? 20 : 0));

  // ─── 3. Business Impact Score ─────────────────────────────────────────────
  // Higher if it's about deals, comparisons, or popular product categories
  let impactScore = 30; // baseline
  if (matchedKeywords.some((k) => ["deal", "discount", "vs", "versus", "comparison"].includes(k))) {
    impactScore += 30;
  }
  if (matchedKeywords.some((k) => BB_KEYWORDS.consumer_electronics.includes(k))) {
    impactScore += 20;
  }
  impactScore = Math.min(100, impactScore);

  // ─── 4. Timeliness Score ─────────────────────────────────────────────────
  let timelinessScore = 50; // default if no date
  if (publishedAt) {
    const ageHours = (Date.now() - new Date(publishedAt).getTime()) / 3_600_000;
    if (ageHours < 6) timelinessScore = 100;
    else if (ageHours < 24) timelinessScore = 80;
    else if (ageHours < 72) timelinessScore = 60;
    else if (ageHours < 168) timelinessScore = 40;
    else timelinessScore = 20;
  }

  // ─── 5. Actionability Score ───────────────────────────────────────────────
  let actionabilityScore = 20;
  if (matchedKeywords.some((k) => ["deal", "discount", "vs", "comparison", "worth it"].includes(k))) {
    actionabilityScore = 80;
  } else if (matchedKeywords.some((k) => BB_KEYWORDS.product_categories.includes(k))) {
    actionabilityScore = 60;
  }

  // ─── Weighted total ───────────────────────────────────────────────────────
  const total = Math.round(
    relevanceScore * weights.relevance +
    evidenceScore * weights.evidence +
    impactScore * weights.impact +
    timelinessScore * weights.timeliness +
    actionabilityScore * weights.actionability
  );

  const explanation =
    matchedKeywords.length > 0
      ? `Matched ${matchedKeywords.length} BrandBattle-relevant keyword(s): ${matchedKeywords.slice(0, 5).join(", ")}${matchedKeywords.length > 5 ? "..." : ""}. Source category: ${sourceCategory}.`
      : `No strong BrandBattle keyword matches found. Source category: ${sourceCategory}.`;

  return {
    total,
    breakdown: {
      relevance: Math.round(relevanceScore),
      evidence: Math.round(evidenceScore),
      impact: Math.round(impactScore),
      timeliness: Math.round(timelinessScore),
      actionability: Math.round(actionabilityScore),
      matched_keywords: matchedKeywords.slice(0, 10),
      category: sourceCategory,
      explanation,
    },
  };
}

export function calculateRelevanceScore(title: string, content: string = '') {
  const res = scoreRelevance(`${title} ${content}`);
  return {
    totalScore: res.total,
    breakdown: res.breakdown
  };
}

// ─── Safety gates ─────────────────────────────────────────────────────────────
export type SafetyGateResult = {
  canPublish?: boolean;
  allowed?: boolean;
  reasons?: string[];
  reason?: string;
};

export function checkSafetyGates(
  paramsOrStatus: any,
  decision?: string,
  verificationPass?: boolean
): SafetyGateResult {
  if (typeof paramsOrStatus === 'string') {
    const status = paramsOrStatus;
    const isApproved = decision === 'APPROVED';
    const isVerified = status === 'VERIFIED';
    const allowed = isApproved && isVerified;
    return {
      allowed,
      canPublish: allowed,
      reason: allowed ? 'Passed all safety checks.' : 'Verification required before publishing approved content.'
    };
  }

  const params = paramsOrStatus || {};
  const reasons: string[] = [];

  if (params.verificationStatus === "UNVERIFIED" || params.verificationStatus === "NEEDS_REVIEW") {
    reasons.push("Content contains unverified claims. Verification required before publishing.");
  }

  if (!params.hasApproval) {
    reasons.push("No human approval on record. All content requires explicit approval before publishing.");
  }

  if (params.contentStatus === "REJECTED") {
    reasons.push("Content was rejected. Rejected content cannot be published.");
  }

  if (params.evidenceRefs && params.evidenceRefs.length === 0) {
    reasons.push("No evidence references attached. Factual content requires source citations.");
  }

  const canPublish = reasons.length === 0;
  return {
    canPublish,
    allowed: canPublish,
    reasons,
    reason: canPublish ? 'Passed safety gates.' : reasons.join(' ')
  };
}

