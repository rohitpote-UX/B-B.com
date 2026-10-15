import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql } from '@/lib/db';
import { validateOutboundUrl } from '@/lib/security';

export async function PUT(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { id } = await params;
  const body = await req.json();
  if (body.url) {
    const check = validateOutboundUrl(body.url);
    if (!check.ok) return NextResponse.json({ error: check.error }, { status: 400 });
  }
  const result = await sql`
    UPDATE bb_research_sources
    SET name = COALESCE(${body.name || null}, name),
        url = COALESCE(${body.url || null}, url),
        category = COALESCE(${body.category || null}, category),
        enabled = COALESCE(${body.enabled ?? null}, enabled),
        frequency_hours = COALESCE(${body.frequency_hours || null}, frequency_hours),
        reliability_notes = COALESCE(${body.reliability_notes || null}, reliability_notes),
        updated_at = NOW()
    WHERE id = ${id}
    RETURNING *
  `;
  if (!result.length) return NextResponse.json({ error: 'Source not found.' }, { status: 404 });
  return NextResponse.json({ source: result[0] });
}

export async function DELETE(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { id } = await params;
  await sql`DELETE FROM bb_research_sources WHERE id = ${id}`;
  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, details) VALUES ('source_deleted', 'bb_research_sources', ${id}, '{}')` ;
  return NextResponse.json({ ok: true });
}
