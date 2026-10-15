import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { evaluateEvidenceStatus } from '@/lib/evidence';
import { validateOutboundUrl } from '@/lib/security';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const records = await sql`
    SELECT e.*, c.claim_text, c.source_entity
    FROM bb_evidence_records e
    LEFT JOIN bb_normalized_claims c ON e.claim_id = c.id
    ORDER BY e.created_at DESC
    LIMIT 50
  `;

  return NextResponse.json({ records });
}

export async function POST(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const body = await req.json();
  const { claim_id, primary_source_url, secondary_source_urls, excerpt, direct_quote, author_attribution, source_type } = body;

  if (!primary_source_url) {
    return NextResponse.json({ error: 'primary_source_url is required.' }, { status: 400 });
  }

  const check = validateOutboundUrl(primary_source_url);
  if (!check.ok) return NextResponse.json({ error: check.error }, { status: 400 });

  const secondaryList = Array.isArray(secondary_source_urls) ? secondary_source_urls : [];
  const evalResult = evaluateEvidenceStatus(secondaryList.length + 1, primary_source_url.includes('official'), false);

  const result = await sql`
    INSERT INTO bb_evidence_records (
      claim_id, primary_source_url, secondary_source_urls, source_type,
      excerpt, direct_quote, author_attribution, corroboration_score,
      contradiction_flag, verified_by, verification_status
    ) VALUES (
      ${claim_id || null}, ${primary_source_url}, ${JSON.stringify(secondaryList)}, ${source_type || 'news_report'},
      ${excerpt || ''}, ${direct_quote || ''}, ${author_attribution || 'Unknown'}, ${evalResult.corroborationScore},
      ${evalResult.contradictionFlag}, ${session.sub}, ${evalResult.status}
    ) RETURNING *
  `;

  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, details) VALUES ('evidence_added', 'bb_evidence_records', ${result[0].id}, ${JSON.stringify({ primary_source_url })})` ;

  return NextResponse.json({ record: result[0] }, { status: 201 });
}
