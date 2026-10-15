import { neon } from '@neondatabase/serverless';

// In-memory database fallback when DATABASE_URL is not set
class LocalMemoryDb {
  private tables: Record<string, any[]> = {
    bb_research_sources: [
      {
        id: 1,
        name: 'BrandBattle Market Watch',
        category: 'competitor',
        source_type: 'rss_feed',
        url: 'https://news.google.com/rss/search?q=ecommerce+india+brand+battle',
        enabled: true,
        frequency_hours: 6,
        reliability_notes: 'Automated news aggregation feed',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: 'D2C & Retail Tech Pulse',
        category: 'industry',
        source_type: 'rss_feed',
        url: 'https://news.google.com/rss/search?q=d2c+brands+india+price+comparison',
        enabled: true,
        frequency_hours: 4,
        reliability_notes: 'Retail industry trend feed',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: 'Consumer Tech Insights',
        category: 'consumer',
        source_type: 'rss_feed',
        url: 'https://news.google.com/rss/search?q=gadget+reviews+india+price+war',
        enabled: true,
        frequency_hours: 12,
        reliability_notes: 'Consumer tech reviews',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ],
    bb_research_items: [
      {
        id: 1,
        source_id: 1,
        source_name: 'BrandBattle Market Watch',
        title: 'Price wars intensify between top Indian e-commerce electronics sellers',
        link: 'https://example.com/news/price-wars-electronics',
        pub_date: new Date().toISOString(),
        content: 'Major e-commerce platforms have launched surprise price cuts on smartphones and audio products ahead of the festive shopping window. Analysts suggest margins may shrink by 4% to 7%.',
        raw_hash: 'hash_sample_1',
        normalized_hash: 'norm_sample_1',
        category: 'competitor',
        relevance_score: 88,
        reasoning_json: JSON.stringify({ brand_relevance: 90, urgency: 85, evidence: 89 }),
        evidence_strength: 'STRONG',
        processing_status: 'PROCESSED',
        collected_at: new Date().toISOString()
      },
      {
        id: 2,
        source_id: 2,
        source_name: 'D2C & Retail Tech Pulse',
        title: 'Comparison shopping usage surges 34% among Gen Z consumers in tier-2 cities',
        link: 'https://example.com/news/comparison-shopping-genz',
        pub_date: new Date().toISOString(),
        content: 'Recent consumer analytics indicate that young shoppers in tier-2 Indian cities are increasingly relying on real-time price comparison bots and platforms before completing high-value purchases.',
        raw_hash: 'hash_sample_2',
        normalized_hash: 'norm_sample_2',
        category: 'consumer',
        relevance_score: 94,
        reasoning_json: JSON.stringify({ brand_relevance: 96, urgency: 90, evidence: 95 }),
        evidence_strength: 'VERIFIED',
        processing_status: 'PROCESSED',
        collected_at: new Date().toISOString()
      }
    ],
    bb_normalized_claims: [
      {
        id: 1,
        research_item_id: 1,
        claim_text: 'Top Indian e-commerce platforms slashed smartphone prices by up to 15% this week.',
        source_entity: 'E-commerce Market Watch',
        entity_type: 'platform',
        confidence_score: 0.92,
        extraction_method: 'llm_nlp',
        created_at: new Date().toISOString()
      }
    ],
    bb_evidence_records: [
      {
        id: 1,
        claim_id: 1,
        primary_source_url: 'https://example.com/news/price-wars-electronics',
        secondary_source_urls: ['https://example.com/news/archive-price-cuts'],
        source_type: 'news_report',
        excerpt: 'Surprise price cuts on smartphones and audio products observed across major marketplaces.',
        direct_quote: 'Margins may shrink by 4% to 7% as retail platforms lock horns.',
        full_article_html_url: null,
        snapshot_storage_url: null,
        archive_url: null,
        timestamp_provenance: new Date().toISOString(),
        author_attribution: 'Market Intelligence Bureau',
        corroboration_score: 85,
        contradiction_flag: false,
        verified_by: 'B&B Evidence Engine',
        verification_status: 'VERIFIED',
        created_at: new Date().toISOString()
      }
    ],
    bb_claim_cross_references: [],
    bb_intelligence_findings: [
      {
        id: 1,
        title: 'Tier-2 Gen Z Shift Toward Real-Time Price Verification',
        summary: 'Gen Z shoppers in tier-2 hubs are increasingly adopting price comparison tools before purchasing high-value electronics.',
        topic_category: 'consumer_trend',
        brand_impact_score: 95,
        market_reach_score: 90,
        customer_relevance_score: 96,
        strategic_urgency_score: 92,
        score_breakdown: JSON.stringify({ reach: 90, relevance: 96, impact: 95, urgency: 92 }),
        total_score: 93,
        verification_status: 'VERIFIED',
        evidence_count: 2,
        time_sensitivity: 'HIGH',
        what_happened: 'Surge of 34% in comparison shopping tool adoption among young shoppers in tier-2 cities.',
        why_it_matters: 'BrandBattle is uniquely positioned to capture this demand by highlighting verified price comparisons.',
        recommended_action: 'Launch targeted Social campaign highlighting BrandBattle verified comparison feature for smartphones.',
        risk_warning: 'Unverified claims could degrade trust if discount claims are outdated.',
        evidence_record_ids: [1],
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ],
    bb_content_drafts: [
      {
        id: 1,
        finding_id: 1,
        content_type: 'x_post',
        platform: 'x',
        target_audience: 'Smart Shoppers & Tech Buyers',
        hook: 'Stop overpaying for your next phone 📱⚡',
        main_copy: 'Gen Z shoppers aren\'t trusting single-store price tags anymore. Over 34% are using verified price comparison before hitting buy. Check the real signal on BrandBattle before you checkout!',
        call_to_action: 'Compare prices live on brandbattle.in',
        hashtags: '#BrandBattle #SmartShopping #PriceComparison #TechDeals',
        suggested_visual_prompt: 'Sleek dark mode graphic comparing retail prices with verified checkmarks.',
        evidence_summary: 'Verified 34% surge in comparison tool usage across tier-2 urban centers.',
        verification_status: 'VERIFIED',
        content_status: 'READY_FOR_REVIEW',
        safety_checks: JSON.stringify({ verification_pass: true, safety_pass: true, notes: 'Fully verified with source record #1' }),
        generated_by: 'B&B Intelligence Agent',
        llm_provider: 'mock_llm',
        llm_model: 'gemini-3.5-flash',
        evidence_refs: [1],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ],
    bb_content_approvals: [],
    bb_marketing_campaigns: [],
    bb_campaign_draft_links: [],
    bb_research_jobs: [],
    bb_audit_logs: []
  };

  query(sqlText: string, params: any[] = []): any[] {
    const text = sqlText.trim().toLowerCase();
    
    if (text.startsWith('select count(*)')) {
      const match = text.match(/from\s+([a_z0_9_]+)/i);
      const tableName = match ? match[1].toLowerCase() : '';
      const list = this.tables[tableName] || [];
      return [{ cnt: list.length }];
    }

    if (text.startsWith('select')) {
      const match = text.match(/from\s+([a_z0_9_]+)/i);
      const tableName = match ? match[1].toLowerCase() : '';
      const list = [...(this.tables[tableName] || [])];
      return list;
    }

    if (text.startsWith('insert into')) {
      const match = text.match(/insert into\s+([a_z0_9_]+)/i);
      const tableName = match ? match[1].toLowerCase() : '';
      if (!this.tables[tableName]) this.tables[tableName] = [];
      const newId = this.tables[tableName].length + 1;
      const newItem = { id: newId, created_at: new Date().toISOString(), ...params[0] };
      this.tables[tableName].push(newItem);
      return [newItem];
    }

    if (text.startsWith('update')) {
      const match = text.match(/update\s+([a_z0_9_]+)/i);
      const tableName = match ? match[1].toLowerCase() : '';
      return this.tables[tableName] || [];
    }

    if (text.startsWith('delete')) {
      return [];
    }

    return [];
  }
}

const memoryDb = new LocalMemoryDb();

// Helper tagged template wrapper that seamlessly operates on Neon DB or fallback memory DB
export async function sql(strings: TemplateStringsArray | string, ...values: any[]): Promise<any[]> {
  const dbUrl = process.env.DATABASE_URL;
  
  if (dbUrl && dbUrl.startsWith('postgres')) {
    try {
      const neonSql = neon(dbUrl);
      if (typeof strings === 'string') {
        return (await (neonSql as any)(strings, ...values)) as any[];
      }
      return (await (neonSql as any)(strings, ...values)) as any[];
    } catch (err) {
      console.warn('[DB] Neon query error, falling back to local memory DB:', err);
    }
  }

  // Fallback memory DB handler
  let sqlText = '';
  if (typeof strings === 'string') {
    sqlText = strings;
  } else {
    sqlText = strings.reduce((acc, str, i) => acc + str + (i < values.length ? `$${i + 1}` : ''), '');
  }

  return memoryDb.query(sqlText, values);
}

export async function initSchema(): Promise<void> {
  const dbUrl = process.env.DATABASE_URL;
  if (!dbUrl || !dbUrl.startsWith('postgres')) {
    return; // Using local memory DB
  }

  try {
    const neonSql = neon(dbUrl);
    await neonSql`
      CREATE TABLE IF NOT EXISTS bb_research_sources (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100) DEFAULT 'general',
        source_type VARCHAR(100) DEFAULT 'rss_feed',
        url TEXT NOT NULL,
        enabled BOOLEAN DEFAULT TRUE,
        frequency_hours INT DEFAULT 6,
        reliability_notes TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_research_items (
        id SERIAL PRIMARY KEY,
        source_id INT REFERENCES bb_research_sources(id) ON DELETE SET NULL,
        source_name VARCHAR(255),
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        pub_date TIMESTAMPTZ,
        content TEXT,
        raw_hash VARCHAR(64),
        normalized_hash VARCHAR(64),
        category VARCHAR(100),
        relevance_score INT DEFAULT 0,
        reasoning_json JSONB,
        evidence_strength VARCHAR(50) DEFAULT 'UNVERIFIED',
        processing_status VARCHAR(50) DEFAULT 'NEW',
        collected_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_normalized_claims (
        id SERIAL PRIMARY KEY,
        research_item_id INT REFERENCES bb_research_items(id) ON DELETE CASCADE,
        claim_text TEXT NOT NULL,
        source_entity VARCHAR(255),
        entity_type VARCHAR(100),
        confidence_score NUMERIC(4,3) DEFAULT 0.500,
        extraction_method VARCHAR(100) DEFAULT 'heuristic',
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_evidence_records (
        id SERIAL PRIMARY KEY,
        claim_id INT REFERENCES bb_normalized_claims(id) ON DELETE CASCADE,
        primary_source_url TEXT NOT NULL,
        secondary_source_urls JSONB DEFAULT '[]'::jsonb,
        source_type VARCHAR(100),
        excerpt TEXT,
        direct_quote TEXT,
        full_article_html_url TEXT,
        snapshot_storage_url TEXT,
        archive_url TEXT,
        timestamp_provenance TIMESTAMPTZ DEFAULT NOW(),
        author_attribution VARCHAR(255),
        corroboration_score INT DEFAULT 50,
        contradiction_flag BOOLEAN DEFAULT FALSE,
        verified_by VARCHAR(100) DEFAULT 'system',
        verification_status VARCHAR(50) DEFAULT 'UNVERIFIED',
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_claim_cross_references (
        id SERIAL PRIMARY KEY,
        claim_id_a INT REFERENCES bb_normalized_claims(id) ON DELETE CASCADE,
        claim_id_b INT REFERENCES bb_normalized_claims(id) ON DELETE CASCADE,
        relationship VARCHAR(50) NOT NULL,
        confidence NUMERIC(4,3) DEFAULT 0.500,
        notes TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_intelligence_findings (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT,
        topic_category VARCHAR(100),
        brand_impact_score INT DEFAULT 50,
        market_reach_score INT DEFAULT 50,
        customer_relevance_score INT DEFAULT 50,
        strategic_urgency_score INT DEFAULT 50,
        score_breakdown JSONB,
        total_score INT DEFAULT 50,
        verification_status VARCHAR(50) DEFAULT 'UNVERIFIED',
        evidence_count INT DEFAULT 0,
        time_sensitivity VARCHAR(50) DEFAULT 'MEDIUM',
        what_happened TEXT,
        why_it_matters TEXT,
        recommended_action TEXT,
        risk_warning TEXT,
        evidence_record_ids JSONB DEFAULT '[]'::jsonb,
        status VARCHAR(50) DEFAULT 'active',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_content_drafts (
        id SERIAL PRIMARY KEY,
        finding_id INT REFERENCES bb_intelligence_findings(id) ON DELETE CASCADE,
        content_type VARCHAR(50) NOT NULL,
        platform VARCHAR(50) NOT NULL,
        target_audience VARCHAR(255),
        hook TEXT,
        main_copy TEXT NOT NULL,
        call_to_action TEXT,
        hashtags TEXT,
        suggested_visual_prompt TEXT,
        evidence_summary TEXT,
        verification_status VARCHAR(50) DEFAULT 'UNVERIFIED',
        content_status VARCHAR(50) DEFAULT 'DRAFT',
        safety_checks JSONB,
        generated_by VARCHAR(100) DEFAULT 'B&B Intelligence Agent',
        llm_provider VARCHAR(100),
        llm_model VARCHAR(100),
        evidence_refs JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_content_approvals (
        id SERIAL PRIMARY KEY,
        draft_id INT REFERENCES bb_content_drafts(id) ON DELETE CASCADE,
        approved_by VARCHAR(100) NOT NULL,
        decision VARCHAR(50) NOT NULL,
        reviewer_notes TEXT,
        edited_copy TEXT,
        content_status VARCHAR(50) NOT NULL,
        decided_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_marketing_campaigns (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        objective TEXT,
        status VARCHAR(50) DEFAULT 'planning',
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_campaign_draft_links (
        id SERIAL PRIMARY KEY,
        campaign_id INT REFERENCES bb_marketing_campaigns(id) ON DELETE CASCADE,
        draft_id INT REFERENCES bb_content_drafts(id) ON DELETE CASCADE,
        performance_notes TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_research_jobs (
        id SERIAL PRIMARY KEY,
        source_id INT REFERENCES bb_research_sources(id) ON DELETE SET NULL,
        source_name VARCHAR(255),
        job_type VARCHAR(100) DEFAULT 'rss_collect',
        status VARCHAR(50) DEFAULT 'pending',
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        items_collected INT DEFAULT 0,
        items_new INT DEFAULT 0,
        items_duplicate INT DEFAULT 0,
        findings_created INT DEFAULT 0,
        error_summary JSONB,
        triggered_by VARCHAR(100) DEFAULT 'system',
        created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS bb_audit_logs (
        id SERIAL PRIMARY KEY,
        action VARCHAR(100) NOT NULL,
        actor VARCHAR(100) DEFAULT 'system',
        entity_type VARCHAR(100),
        entity_id INT,
        details JSONB DEFAULT '{}'::jsonb,
        ip_address VARCHAR(45),
        created_at TIMESTAMPTZ DEFAULT NOW()
      );
    `;
  } catch (err) {
    console.error('[DB] Failed to initialize Postgres schema:', err);
  }
}
