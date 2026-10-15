import { NextRequest, NextResponse } from 'next/server';
import { signSession, validatePassword, COOKIE_NAME } from '@/lib/auth';
import { sql, initSchema } from '@/lib/db';
import { getClientIp } from '@/lib/security';

export async function POST(req: NextRequest) {
  try {
    await initSchema();
    const body = await req.json();
    const { password } = body;

    if (!password || typeof password !== 'string') {
      return NextResponse.json({ error: 'Password required.' }, { status: 400 });
    }

    if (!validatePassword(password)) {
      await sql`INSERT INTO bb_audit_logs (action, actor, details, ip_address)
        VALUES ('login_failed', 'anonymous', '{}'::jsonb, ${getClientIp(req)})`;
      return NextResponse.json({ error: 'Invalid password.' }, { status: 401 });
    }

    const token = await signSession();
    await sql`INSERT INTO bb_audit_logs (action, actor, details, ip_address)
      VALUES ('login_success', 'team', '{}'::jsonb, ${getClientIp(req)})`;

    const response = NextResponse.json({ ok: true, redirectTo: '/dashboard' });
    response.cookies.set(COOKIE_NAME, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: Number(process.env.BB_JWT_EXPIRES_IN || 86400),
      path: '/',
    });
    return response;
  } catch (err) {
    console.error('[auth/login]', err);
    return NextResponse.json({ error: 'Internal server error.' }, { status: 500 });
  }
}
