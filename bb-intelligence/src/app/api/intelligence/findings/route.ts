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

  const findings = await sql`
    SELECT * FROM bb_intelligence_findings
    WHERE status = 'active'
    ORDER BY total_score DESC, created_at DESC
    LIMIT ${limit} OFFSET ${offset}
  `;

  const total = await sql`SELECT COUNT(*) as cnt FROM bb_intelligence_findings WHERE status = 'active'`;
  return NextResponse.json({ findings, total: Number(total[0]?.cnt || 0), page, limit });
}
