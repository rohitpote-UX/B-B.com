/**
 * B&B Intelligence — RSS Collector
 *
 * Fetches and parses RSS/Atom feeds from configured sources.
 * Performs fingerprinting and deduplication before storing.
 * Never pretends a source was accessed if it was not.
 */

import { safeFetch } from "./security";
import { sql } from "./db";
import { scoreRelevance } from "./scoring";

// ─── RSS item shape from rss-parser ──────────────────────────────────────────

type RawFeedItem = {
  title?: string;
  link?: string;
  pubDate?: string;
  creator?: string;
  content?: string;
  contentSnippet?: string;
  guid?: string;
};

type RawFeed = {
  title?: string;
  items: RawFeedItem[];
};

// ─── Simple XML/RSS parser (avoids Node-only feedparser dependency) ───────────

function parseRSS(xml: string): RawFeed {
  const items: RawFeedItem[] = [];

  // Extract channel title
  const channelTitleMatch = xml.match(/<channel[^>]*>[\s\S]*?<title[^>]*>([\s\S]*?)<\/title>/i);
  const channelTitle = stripCData(channelTitleMatch?.[1] || "");

  // Extract all <item> blocks
  const itemMatches = xml.match(/<item[^>]*>([\s\S]*?)<\/item>/gi) || [];

  for (const itemXml of itemMatches) {
    const title = stripCData(extractTag(itemXml, "title"));
    const link = stripCData(extractTag(itemXml, "link")).trim();
    const pubDate = stripCData(extractTag(itemXml, "pubDate"));
    const creator = stripCData(extractTag(itemXml, "dc:creator") || extractTag(itemXml, "author"));
    const description = stripCData(extractTag(itemXml, "description"));
    const guid = stripCData(extractTag(itemXml, "guid"));

    items.push({
      title: title || undefined,
      link: link || undefined,
      pubDate: pubDate || undefined,
      creator: creator || undefined,
      contentSnippet: description ? description.replace(/<[^>]+>/g, "").trim().slice(0, 500) : undefined,
      guid: guid || link || title || undefined,
    });
  }

  return { title: channelTitle || undefined, items };
}

function extractTag(xml: string, tag: string): string {
  const match = xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i"));
  return match?.[1] || "";
}

function stripCData(str: string): string {
  return str.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1").trim();
}

// ─── SHA-256 fingerprint for deduplication ────────────────────────────────────

async function fingerprint(text: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ─── Collect from a single RSS source ────────────────────────────────────────

export type CollectionResult = {
  sourceId: number;
  sourceName: string;
  itemsCollected: number;
  itemsNew: number;
  itemsDuplicate: number;
  findingsCreated: number;
  errors: string[];
  success: boolean;
};

export async function collectFromSource(
  sourceId: number,
  maxItems = 50
): Promise<CollectionResult> {
  const result: CollectionResult = {
    sourceId,
    sourceName: "",
    itemsCollected: 0,
    itemsNew: 0,
    itemsDuplicate: 0,
    findingsCreated: 0,
    errors: [],
    success: false,
  };

  // Load source
  const sources = await sql`
    SELECT * FROM bb_research_sources WHERE id = ${sourceId} AND enabled = true
  `;
  if (!sources.length) {
    result.errors.push(`Source ${sourceId} not found or disabled.`);
    return result;
  }
  const source = sources[0];
  result.sourceName = source.name as string;

  const fetchResult = await safeFetch(source.url as string);
  if (!fetchResult.ok) {
    const errorMsg = `HTTP ${fetchResult.status} ${fetchResult.statusText}`;
    await sql`
      UPDATE bb_research_sources
      SET last_failure_at = NOW(), last_error = ${errorMsg}, updated_at = NOW()
      WHERE id = ${sourceId}
    `;
    result.errors.push(`Fetch failed: ${errorMsg}`);
    return result;
  }

  // Parse RSS
  let feed: RawFeed;
  try {
    const xmlText = await fetchResult.text();
    feed = parseRSS(xmlText);
  } catch (err) {
    result.errors.push(`Parse failed: ${String(err)}`);
    return result;
  }

  const items = feed.items.slice(0, maxItems);
  result.itemsCollected = items.length;

  const minScore = Number(process.env.BB_MIN_RELEVANCE_SCORE || 40);

  for (const item of items) {
    // Build deduplication key
    const dedupKey = item.guid || item.link || `${item.title}-${source.name}`;
    const fp = await fingerprint(dedupKey);

    // Check for duplicate
    const existing = await sql`
      SELECT id FROM bb_research_items WHERE content_fingerprint = ${fp}
    `;
    if (existing.length > 0) {
      result.itemsDuplicate++;
      continue;
    }

    // Score relevance
    const textForScoring = `${item.title || ""} ${item.contentSnippet || ""}`;
    const scoring = scoreRelevance(textForScoring, source.category as string);

    // Store the item
    const publishedAt = item.pubDate ? new Date(item.pubDate).toISOString() : null;

    await sql`
      INSERT INTO bb_research_items (
        source_id, source_name, source_type, original_url, title, author,
        publisher, published_at, raw_text, content_fingerprint,
        retrieval_method, source_reliability, processing_status,
        relevance_score, relevance_breakdown, category
      ) VALUES (
        ${sourceId}, ${source.name}, ${source.source_type},
        ${item.link || null}, ${item.title || null},
        ${item.creator || null}, ${feed.title || source.name},
        ${publishedAt}, ${item.contentSnippet || null},
        ${fp}, 'rss', ${source.reliability_notes ? 0.7 : 0.5},
        'received', ${scoring.total}, ${JSON.stringify(scoring.breakdown)},
        ${source.category}
      )
    `;
    result.itemsNew++;

    // Promote high-relevance items to findings
    if (scoring.total >= minScore) {
      const inserts = await sql`
        INSERT INTO bb_intelligence_findings (
          title, summary, category, what_happened,
          why_it_matters, suggested_action, suggested_format,
          recommended_platform, time_sensitivity,
          source_item_ids, relevance_score, total_score,
          score_breakdown, status
        )
        SELECT
          ${item.title || "Untitled finding"},
          ${item.contentSnippet ? item.contentSnippet.slice(0, 500) : null},
          ${source.category},
          ${item.contentSnippet ? item.contentSnippet.slice(0, 300) : null},
          ${"Potential content opportunity for BrandBattle audience."},
          ${"Review and create relevant comparison or deal-check content."},
          ${"X post or Instagram caption"},
          ${"X, Instagram"},
          ${"medium"},
          ${JSON.stringify([])},
          ${scoring.total},
          ${scoring.total},
          ${JSON.stringify(scoring.breakdown)},
          ${"active"}
        WHERE NOT EXISTS (
          SELECT 1 FROM bb_intelligence_findings WHERE title = ${item.title || "Untitled finding"}
        )
        RETURNING id
      `;
      if (inserts.length > 0) {
        result.findingsCreated++;
        // Update the research item's finding_id linkage
        const newItemRows = await sql`
          SELECT id FROM bb_research_items WHERE content_fingerprint = ${fp}
        `;
        if (newItemRows.length > 0) {
          await sql`
            UPDATE bb_intelligence_findings
            SET source_item_ids = source_item_ids || ${JSON.stringify([newItemRows[0].id])}::jsonb
            WHERE id = ${inserts[0].id}
          `;
        }
      }
    }
  }

  // Update source success timestamp
  await sql`
    UPDATE bb_research_sources
    SET last_success_at = NOW(), last_error = NULL, updated_at = NOW()
    WHERE id = ${sourceId}
  `;

  result.success = true;
  return result;
}
