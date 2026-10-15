import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    await initSchema();
    const [sources, items, findings, drafts, jobs, approvals] = await Promise.all([
      sql`SELECT COUNT(*) as cnt FROM bb_research_sources WHERE enabled = true`,
      sql`SELECT COUNT(*) as cnt FROM bb_research_items`,
      sql`SELECT COUNT(*) as cnt FROM bb_intelligence_findings WHERE status = 'active'`,
      sql`SELECT COUNT(*) as cnt FROM bb_content_drafts`,
      sql`SELECT COUNT(*) as cnt FROM bb_research_jobs WHERE status = 'completed'`,
      sql`SELECT COUNT(*) as cnt FROM bb_content_drafts WHERE content_status = 'READY_FOR_REVIEW'`,
    ]);

    const recentItems = await sql`
      SELECT id, title, source_name, relevance_score, processing_status, collected_at
      FROM bb_research_items
      ORDER BY collected_at DESC
      LIMIT 5
    `;

    const recentFindings = await sql`
      SELECT id, title, total_score, time_sensitivity, created_at
      FROM bb_intelligence_findings
      ORDER BY total_score DESC, created_at DESC
      LIMIT 5
    `;

    return NextResponse.json({
      stats: {
        active_sources: Number(sources[0]?.cnt || 0),
        total_items: Number(items[0]?.cnt || 0),
        active_findings: Number(findings[0]?.cnt || 0),
        total_drafts: Number(drafts[0]?.cnt || 0),
        completed_jobs: Number(jobs[0]?.cnt || 0),
        pending_approvals: Number(approvals[0]?.cnt || 0),
      },
      recent_items: recentItems,
      recent_findings: recentFindings,
    });
  } catch (err) {
    console.error('[overview]', err);
    return NextResponse.json({ error: 'Failed to load overview.' }, { status: 500 });
  }
}
