import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { validateOutboundUrl } from '@/lib/security';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();
  const sources = await sql`SELECT * FROM bb_research_sources ORDER BY created_at DESC`;
  return NextResponse.json({ sources });
}

export async function POST(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const body = await req.json();
  const { name, category, source_type, url, enabled, frequency_hours, reliability_notes } = body;

  if (!name || !url) return NextResponse.json({ error: 'name and url are required.' }, { status: 400 });

  const urlCheck = validateOutboundUrl(url);
  if (!urlCheck.ok) return NextResponse.json({ error: urlCheck.error }, { status: 400 });

  const result = await sql`
    INSERT INTO bb_research_sources (name, category, source_type, url, enabled, frequency_hours, reliability_notes)
    VALUES (${name}, ${category || 'general'}, ${source_type || 'rss_feed'}, ${url}, ${enabled !== false}, ${frequency_hours || 6}, ${reliability_notes || null})
    RETURNING *
  `;

  await sql`INSERT INTO bb_audit_logs (action, entity_type, details) VALUES ('source_created', 'bb_research_sources', ${JSON.stringify({ name, url })})` ;
  return NextResponse.json({ source: result[0] }, { status: 201 });
}
