import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const { searchParams } = new URL(req.url);
  const page = Math.max(1, Number(searchParams.get('page') || 1));
  const limit = Math.min(50, Number(searchParams.get('limit') || 20));
  const offset = (page - 1) * limit;
  const status = searchParams.get('status');
  const category = searchParams.get('category');
  const minScore = searchParams.get('min_score');

  const items = await sql`
    SELECT * FROM bb_research_items
    WHERE (${ status ? sql`processing_status = ${status}` : sql`1=1` })
    AND (${ category ? sql`category = ${category}` : sql`1=1` })
    AND (${ minScore ? sql`relevance_score >= ${Number(minScore)}` : sql`1=1` })
    ORDER BY collected_at DESC
    LIMIT ${limit} OFFSET ${offset}
  `;

  const total = await sql`
    SELECT COUNT(*) as cnt FROM bb_research_items
    WHERE (${ status ? sql`processing_status = ${status}` : sql`1=1` })
    AND (${ category ? sql`category = ${category}` : sql`1=1` })
    AND (${ minScore ? sql`relevance_score >= ${Number(minScore)}` : sql`1=1` })
  `;

  return NextResponse.json({ items, total: Number(total[0]?.cnt || 0), page, limit });
}
