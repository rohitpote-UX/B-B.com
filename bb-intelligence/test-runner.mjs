import { processArticle, generateHash } from './src/lib/normalizer.ts';
import { evaluateEvidenceStatus } from './src/lib/evidence.ts';
import { validateOutboundUrl } from './src/lib/security.ts';
import { calculateRelevanceScore, checkSafetyGates } from './src/lib/scoring.ts';

console.log("==========================================");
console.log("   B&B INTELLIGENCE SUITE TEST HARNESS    ");
console.log("==========================================\n");

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`[PASS] ${message}`);
    passed++;
  } else {
    console.error(`[FAIL] ${message}`);
    failed++;
  }
}

// 1. Deduplication & Normalization Tests
console.log("--- 1. Testing Normalization & Deduplication ---");
const art1 = processArticle("Price drop on flagship smartphones!", "Sellers slash prices by 15% in festive sale.", "https://example.com/news1");
const art2 = processArticle("PRICE DROP ON FLAGSHIP SMARTPHONES!!!", "Sellers slash prices by 15% in festive sale.", "https://example.com/news2");

assert(art1.normalizedHash === art2.normalizedHash, "Normalized hashes match for identical titles with different casing & punctuation.");
assert(art1.rawHash !== art2.rawHash, "Raw hashes differ for different URLs.");
assert(art1.extractedClaims.length > 0, "Successfully extracted claims from article content.");

// 2. Evidence Verification State Machine Tests
console.log("\n--- 2. Testing Evidence Verification State Machine ---");
const ev1 = evaluateEvidenceStatus(2, true, false);
assert(ev1.status === "VERIFIED", "Official source + corroboration returns VERIFIED status.");
assert(ev1.corroborationScore >= 85, "Corroboration score is high for verified claims.");

const ev2 = evaluateEvidenceStatus(1, false, true);
assert(ev2.status === "CONTRADICTED", "Contradiction flag forces CONTRADICTED status.");
assert(ev2.contradictionFlag === true, "Contradiction flag set to true.");

// 3. Security & SSRF Protection Tests
console.log("\n--- 3. Testing SSRF & Security Filters ---");
const sec1 = validateOutboundUrl("http://169.254.169.254/latest/meta-data/");
assert(sec1.ok === false, "SSRF protection blocks AWS metadata IP.");

const sec2 = validateOutboundUrl("http://localhost:3000/admin");
assert(sec2.ok === false, "SSRF protection blocks localhost URL.");

const sec3 = validateOutboundUrl("https://news.google.com/rss");
assert(sec3.ok === true, "SSRF protection allows legitimate HTTPS RSS URL.");

// 4. Scoring Engine & Safety Gates Tests
console.log("\n--- 4. Testing Scoring Engine & Safety Gates ---");
const score = calculateRelevanceScore("Smartphone price comparison surge", "Consumers compare discounts on BrandBattle vs Amazon");
assert(score.totalScore >= 50, "Relevant title gets high relevance score.");

const gate1 = checkSafetyGates("VERIFIED", "APPROVED", true);
assert(gate1.allowed === true, "Safety gate approves verified content with human confirmation.");

const gate2 = checkSafetyGates("UNVERIFIED", "APPROVED", false);
assert(gate2.allowed === false, "Safety gate BLOCKS unverified content from publication.");

console.log("\n==========================================");
console.log(`TEST RESULTS: ${passed} PASSED, ${failed} FAILED.`);
console.log("==========================================");

if (failed > 0) process.exit(1);
