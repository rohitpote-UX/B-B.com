import { SignJWT, jwtVerify } from 'jose';
import { NextRequest } from 'next/server';

export const COOKIE_NAME = 'bb_intel_session';
const JWT_SECRET = new TextEncoder().encode(
  process.env.BB_JWT_SECRET || 'bb-intelligence-super-secret-jwt-key-2026-secure'
);

export interface SessionPayload {
  sub: string;
  role: string;
  authenticated: boolean;
  exp?: number;
}

export function validatePassword(password: string): boolean {
  const envPassword = process.env.BB_TEAM_PASSWORD || 'brandbattle2026!';
  return password === envPassword;
}

export async function signSession(): Promise<string> {
  const expiresSeconds = Number(process.env.BB_JWT_EXPIRES_IN || 86400);
  return new SignJWT({ sub: 'team', role: 'operator', authenticated: true })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(`${expiresSeconds}s`)
    .sign(JWT_SECRET);
}

export async function verifySession(token: string): Promise<SessionPayload | null> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return {
      sub: String(payload.sub || 'team'),
      role: String(payload.role || 'operator'),
      authenticated: Boolean(payload.authenticated),
      exp: payload.exp
    };
  } catch {
    return null;
  }
}

export async function getSessionFromRequest(req: NextRequest): Promise<SessionPayload | null> {
  const cookieToken = req.cookies.get(COOKIE_NAME)?.value;
  if (cookieToken) {
    const session = await verifySession(cookieToken);
    if (session) return session;
  }

  const authHeader = req.headers.get('Authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    return verifySession(token);
  }

  // Development bypass helper if requested
  if (process.env.NODE_ENV === 'development' && process.env.BB_DEV_AUTO_AUTH === 'true') {
    return { sub: 'dev', role: 'admin', authenticated: true };
  }

  return null;
}
