// Décode le JWE NextAuth v4 (alg=dir, enc=A256GCM, key=sha256(secret)) en pur node crypto.
import crypto from 'crypto';

const BASE = 'http://127.0.0.1:3000';
const SECRET = 'dev-only-secret-change-me-0123456789abcdef';

function parseSetCookie(header) {
  const [pair, ...attrs] = header.split(';');
  const idx = pair.indexOf('=');
  return { name: pair.slice(0, idx).trim(), value: pair.slice(idx + 1).trim(), attrs: attrs.map(a => a.trim()) };
}
const b64u = (s) => Buffer.from(s, 'base64url');

async function main() {
  const jar = new Map();
  const cookieHeader = () => [...jar.entries()].map(([k, v]) => `${k}=${v}`).join('; ');

  let r = await fetch(`${BASE}/api/auth/csrf`);
  const { csrfToken } = await r.json();
  for (const sc of r.headers.getSetCookie()) { const c = parseSetCookie(sc); jar.set(c.name, c.value); }

  const body = new URLSearchParams({ csrfToken, json: 'true', email: 'admin@evolog.cm', username: 'admin@evolog.cm', password: 'admin123', callbackUrl: `${BASE}/dashboard` });
  r = await fetch(`${BASE}/api/auth/callback/credentials`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded', Cookie: cookieHeader() }, body: body.toString(), redirect: 'manual' });
  let token = null;
  for (const sc of r.headers.getSetCookie()) { const c = parseSetCookie(sc); if (c.name === 'next-auth.session-token') token = c.value; }
  if (!token) { console.log('NO session-token cookie set'); return; }
  console.log('JWE parts:', token.split('.').length);

  const [protectedB64, ivB64, ctB64, tagB64] = token.split('.');
  const key = crypto.createHash('sha256').update(SECRET).digest();
  const iv = b64u(ivB64), ct = b64u(ctB64), tag = b64u(tagB64);
  try {
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAAD(Buffer.from(protectedB64, 'ascii'));
    decipher.setAuthTag(tag);
    const out = Buffer.concat([decipher.update(ct), decipher.final()]);
    const obj = JSON.parse(out.toString('utf8'));
    console.log('DECODED OK. keys:', Object.keys(obj).join(','));
    console.log('name:', obj.name, '| email:', obj.email);
    console.log('has accessToken:', !!obj.accessToken, '| roles:', JSON.stringify(obj.roles));
    console.log('exp:', obj.exp, '| valid:', obj.exp > Math.floor(Date.now() / 1000));
  } catch (e) {
    console.log('DECODE FAILED:', e.message);
  }

  // Rappel: /session avec ce cookie
  jar.set('next-auth.session-token', token);
  const rs = await fetch(`${BASE}/api/auth/session`, { headers: { Cookie: cookieHeader() } });
  console.log('/session =>', rs.status, JSON.stringify(await rs.json()).slice(0, 120));
}
main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
