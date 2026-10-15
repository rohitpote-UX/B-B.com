import { NextRequest, NextResponse } from 'next/server';
import { getSessionFromRequest } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';

export async function GET(req: NextRequest) {
  const session = await getSessionFromRequest(req);
  if (!session?.authenticated) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  await initSchema();

  const logs = await sql`
    SELECT * FROM bb_audit_logs
    ORDER BY created_at DESC
    LIMIT 100
  `;

  return NextResponse.json({ logs });
}
