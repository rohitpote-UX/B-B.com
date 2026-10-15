import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { generateXPost, generateInstagramCaption, generateOpportunityBrief } from '@/lib/llm';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const { searchParams } = new URL(req.url);
  const status = searchParams.get('status');
  const page = Math.max(1, Number(searchParams.get('page') || 1));
  const limit = Math.min(50, Number(searchParams.get('limit') || 20));
  const offset = (page - 1) * limit;

  const drafts = await sql`
    SELECT * FROM bb_content_drafts
    WHERE (${ status ? sql`content_status = ${status}` : sql`1=1` })
    ORDER BY created_at DESC
    LIMIT ${limit} OFFSET ${offset}
  `;
  const total = await sql`SELECT COUNT(*) as cnt FROM bb_content_drafts WHERE (${ status ? sql`content_status = ${status}` : sql`1=1` })`;
  return NextResponse.json({ drafts, total: Number(total[0]?.cnt || 0), page, limit });
}

export async function POST(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const body = await req.json();
  const { finding_id, content_type, platform } = body;
  if (!finding_id || !content_type) return NextResponse.json({ error: 'finding_id and content_type are required.' }, { status: 400 });

  const findingRows = await sql`SELECT * FROM bb_intelligence_findings WHERE id = ${finding_id}`;
  if (!findingRows.length) return NextResponse.json({ error: 'Finding not found.' }, { status: 404 });
  const finding = findingRows[0];

  const evidenceSummary = `${finding.what_happened || ''} ${finding.why_it_matters || ''} ${finding.summary || ''}`.trim();

  let generated;
  if (content_type === 'x_post') {
    generated = await generateXPost(String(finding.title), evidenceSummary, 'Visit brandbattle.in to compare before you buy.');
  } else if (content_type === 'instagram_caption') {
    generated = await generateInstagramCaption(String(finding.title), evidenceSummary, 'deal intelligence');
  } else {
    generated = await generateOpportunityBrief({ title: String(finding.title), what_happened: String(finding.what_happened || ''), why_it_matters: String(finding.why_it_matters || '') }, evidenceSummary);
  }

  const verificationStatus = (finding.verification_status as string) || 'UNVERIFIED';
  const draftStatus = verificationStatus === 'VERIFIED' ? 'DRAFT' : 'NEEDS_VERIFICATION';

  const rows = await sql`
    INSERT INTO bb_content_drafts (
      finding_id, content_type, platform, main_copy,
      evidence_summary, verification_status, content_status,
      generated_by, llm_provider, llm_model, evidence_refs
    ) VALUES (
      ${finding_id}, ${content_type}, ${platform || content_type},
      ${generated.text || '[Generation failed]'},
      ${evidenceSummary.slice(0, 1000)}, ${verificationStatus},
      ${draftStatus}, 'bb_intelligence', ${generated.provider}, ${generated.model},
      ${JSON.stringify(finding.evidence_record_ids || [])}
    ) RETURNING *
  `;

  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, details) VALUES ('draft_created', 'bb_content_drafts', ${rows[0].id}, ${JSON.stringify({ finding_id, content_type })})` ;
  return NextResponse.json({ draft: rows[0] }, { status: 201 });
}
