import { createHash } from 'crypto';

export interface NormalizedResult {
  rawHash: string;
  normalizedHash: string;
  cleanTitle: string;
  cleanContent: string;
  extractedClaims: string[];
}

export function generateHash(text: string): string {
  return createHash('sha256').update(text.trim()).digest('hex');
}

export function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^\w\s]/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function extractClaimsFromText(title: string, content: string): string[] {
  const claims: string[] = [];
  const fullText = `${title}. ${content}`;

  // Simple rule-based claim extraction heuristics
  const sentences = fullText.split(/(?<=[.?!])\s+/);

  for (const sentence of sentences) {
    const trimmed = sentence.trim();
    // Claim detection triggers: numbers, percentages, price drops, surges, reports
    if (
      /\b(\d+%|\$\d+|\bprice\b|\bcut\b|\bsurge\b|\bdrop\b|\blaunch\b|\bmarket\b|\bdeal\b|\bsale\b)\b/i.test(trimmed) &&
      trimmed.length > 25 &&
      trimmed.length < 250
    ) {
      claims.push(trimmed);
    }
  }

  if (claims.length === 0) {
    claims.push(title.trim());
  }

  return claims.slice(0, 3); // Top 3 claims
}

export function processArticle(title: string, content: string, url: string): NormalizedResult {
  const cleanTitle = title.trim();
  const cleanContent = content.trim();
  const rawHash = generateHash(`${url}-${cleanTitle}`);
  const normalizedTitle = normalizeTitle(cleanTitle);
  const normalizedHash = generateHash(normalizedTitle);
  const extractedClaims = extractClaimsFromText(cleanTitle, cleanContent);

  return {
    rawHash,
    normalizedHash,
    cleanTitle,
    cleanContent,
    extractedClaims,
  };
}
