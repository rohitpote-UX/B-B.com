import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { checkSafetyGates } from '@/lib/scoring';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const approvals = await sql`
    SELECT a.*, d.main_copy, d.platform, d.content_type, d.verification_status as draft_verification
    FROM bb_content_approvals a
    JOIN bb_content_drafts d ON a.draft_id = d.id
    ORDER BY a.decided_at DESC
    LIMIT 50
  `;

  return NextResponse.json({ approvals });
}

export async function POST(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const body = await req.json();
  const { draft_id, decision, reviewer_notes, edited_copy } = body;

  if (!draft_id || !decision || !['APPROVED', 'REJECTED', 'NEEDS_EDITS'].includes(decision)) {
    return NextResponse.json({ error: 'draft_id and valid decision (APPROVED | REJECTED | NEEDS_EDITS) are required.' }, { status: 400 });
  }

  // Fetch draft
  const draftRows = await sql`SELECT * FROM bb_content_drafts WHERE id = ${draft_id}`;
  if (!draftRows.length) return NextResponse.json({ error: 'Draft not found.' }, { status: 404 });
  const draft = draftRows[0];

  // Enforce safety gates
  const safety = checkSafetyGates(
    draft.verification_status || 'UNVERIFIED',
    decision,
    Boolean(draft.safety_checks?.verification_pass)
  );

  if (!safety.allowed) {
    return NextResponse.json({ error: safety.reason, safety_pass: false }, { status: 422 });
  }

  let finalContentStatus = 'APPROVED';
  if (decision === 'REJECTED') finalContentStatus = 'REJECTED';
  if (decision === 'NEEDS_EDITS') finalContentStatus = 'NEEDS_REVISION';

  // Record approval entry
  const appResult = await sql`
    INSERT INTO bb_content_approvals (draft_id, approved_by, decision, reviewer_notes, edited_copy, content_status)
    VALUES (${draft_id}, ${session.sub}, ${decision}, ${reviewer_notes || null}, ${edited_copy || null}, ${finalContentStatus})
    RETURNING *
  `;

  // Update draft status
  await sql`
    UPDATE bb_content_drafts
    SET content_status = ${finalContentStatus},
        main_copy = COALESCE(${edited_copy || null}, main_copy),
        updated_at = NOW()
    WHERE id = ${draft_id}
  `;

  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, actor, details) VALUES ('approval_decision', 'bb_content_approvals', ${appResult[0].id}, ${session.sub}, ${JSON.stringify({ decision, draft_id })})` ;

  return NextResponse.json({ approval: appResult[0], status: finalContentStatus }, { status: 201 });
}
