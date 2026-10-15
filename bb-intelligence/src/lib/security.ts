import { NextRequest } from 'next/server';

export interface UrlValidationResult {
  ok: boolean;
  error?: string;
  url?: URL;
}

const BLOCKED_HOSTNAMES = [
  'localhost',
  '127.0.0.1',
  '0.0.0.0',
  '::1',
  '169.254.169.254',
  'metadata.google.internal'
];

const ALLOWED_SCHEMES = ['http:', 'https:'];

export function validateOutboundUrl(rawUrl: string): UrlValidationResult {
  if (!rawUrl || typeof rawUrl !== 'string') {
    return { ok: false, error: 'URL must be a non-empty string.' };
  }

  try {
    const parsed = new URL(rawUrl);

    if (!ALLOWED_SCHEMES.includes(parsed.protocol)) {
      return { ok: false, error: `Protocol ${parsed.protocol} is not allowed.` };
    }

    const hostname = parsed.hostname.toLowerCase();

    if (BLOCKED_HOSTNAMES.includes(hostname)) {
      return { ok: false, error: 'Access to local or cloud metadata hosts is forbidden.' };
    }

    if (/^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)/.test(hostname)) {
      return { ok: false, error: 'Access to private local network IPs is forbidden.' };
    }

    return { ok: true, url: parsed };
  } catch {
    return { ok: false, error: 'Malformed URL provided.' };
  }
}

export async function safeFetch(rawUrl: string, options: RequestInit = {}): Promise<Response> {
  const check = validateOutboundUrl(rawUrl);
  if (!check.ok) {
    throw new Error(`SSRF Guard Blocked Request: ${check.error}`);
  }
  return fetch(rawUrl, {
    ...options,
    headers: {
      'User-Agent': 'BrandBattle-Intelligence-Agent/1.0 (+https://brandbattle.in)',
      ...(options.headers || {})
    }
  });
}

export function getClientIp(req: NextRequest): string {
  const forwarded = req.headers.get('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  const realIp = req.headers.get('x-real-ip');
  if (realIp) return realIp;
  return '127.0.0.1';
}

export function sanitizeInput(input: string): string {
  if (!input) return '';
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}
