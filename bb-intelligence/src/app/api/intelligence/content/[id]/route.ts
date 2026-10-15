import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql } from '@/lib/db';
import { checkSafetyGates } from '@/lib/scoring';

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { id } = await params;
  const rows = await sql`SELECT * FROM bb_content_drafts WHERE id = ${id}`;
  if (!rows.length) return NextResponse.json({ error: 'Draft not found.' }, { status: 404 });
  const approvals = await sql`SELECT * FROM bb_content_approvals WHERE draft_id = ${id} ORDER BY decided_at DESC LIMIT 1`;
  return NextResponse.json({ draft: rows[0], latest_approval: approvals[0] || null });
}

export async function PUT(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { id } = await params;
  const body = await req.json();
  const result = await sql`
    UPDATE bb_content_drafts
    SET main_copy = COALESCE(${body.main_copy || null}, main_copy),
        hook = COALESCE(${body.hook || null}, hook),
        call_to_action = COALESCE(${body.call_to_action || null}, call_to_action),
        hashtags = COALESCE(${body.hashtags ? JSON.stringify(body.hashtags) : null}::jsonb, hashtags),
        reviewer_notes = COALESCE(${body.reviewer_notes || null}, reviewer_notes),
        content_status = COALESCE(${body.content_status || null}, content_status),
        updated_at = NOW()
    WHERE id = ${id} AND content_status != 'PUBLISHED'
    RETURNING *
  `;
  if (!result.length) return NextResponse.json({ error: 'Draft not found or already published.' }, { status: 404 });
  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, details) VALUES ('draft_edited', 'bb_content_drafts', ${id}, '{}')`;
  return NextResponse.json({ draft: result[0] });
}

export async function POST(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  // This endpoint handles approval/rejection actions
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { id } = await params;
  const body = await req.json();
  const { action, notes, reviewer } = body;

  if (!['approve', 'reject'].includes(action)) {
    return NextResponse.json({ error: 'action must be approve or reject.' }, { status: 400 });
  }

  const drafts = await sql`SELECT * FROM bb_content_drafts WHERE id = ${id}`;
  if (!drafts.length) return NextResponse.json({ error: 'Draft not found.' }, { status: 404 });
  const draft = drafts[0];

  if (draft.content_status === 'PUBLISHED') {
    return NextResponse.json({ error: 'Published content cannot be re-approved or rejected.' }, { status: 400 });
  }

  // Safety gates check
  const existingApprovals = await sql`SELECT id FROM bb_content_approvals WHERE draft_id = ${id} AND decision = 'approved'`;
  const gates = checkSafetyGates({
    verificationStatus: String(draft.verification_status || 'UNVERIFIED'),
    contentStatus: String(draft.content_status),
    evidenceRefs: Array.isArray(draft.evidence_refs) ? draft.evidence_refs as number[] : [],
    hasApproval: action === 'approve' ? true : existingApprovals.length > 0,
  });

  const newStatus = action === 'approve' ? 'APPROVED' : 'REJECTED';

  await sql`
    INSERT INTO bb_content_approvals (draft_id, decision, reviewer, notes)
    VALUES (${id}, ${action === 'approve' ? 'approved' : 'rejected'}, ${reviewer || 'team'}, ${notes || null})
  `;

  await sql`
    UPDATE bb_content_drafts SET content_status = ${newStatus}, updated_at = NOW() WHERE id = ${id}
  `;

  await sql`INSERT INTO bb_audit_logs (action, entity_type, entity_id, details)
    VALUES (${action === 'approve' ? 'draft_approved' : 'draft_rejected'}, 'bb_content_drafts', ${id}, ${JSON.stringify({ reviewer, notes, safety_gate_warnings: gates.reasons })})`;

  return NextResponse.json({ ok: true, new_status: newStatus, safety_gate_warnings: gates.reasons });
}
