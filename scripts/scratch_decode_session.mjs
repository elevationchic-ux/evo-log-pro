// Décode le JWE de session NextAuth v4 avec la méthode interne (sha256(secret) -> cle A256GCM dir)
import crypto from 'crypto';
import * as jose from 'jose';

const BASE = 'http://127.0.0.1:3000';
const SECRET = 'dev-only-secret-change-me-0123456789abcdef';

function parseSetCookie(header) {
  const [pair, ...attrs] = header.split(';');
  const idx = pair.indexOf('=');
  return { name: pair.slice(0, idx).trim(), value: pair.slice(idx + 1).trim(), attrs: attrs.map(a => a.trim()) };
}

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
  console.log('raw JWE (first 40):', token ? token.slice(0, 40) : 'NONE');

  // NextAuth v4 derive: sha256(secret) -> 256-bit key; JWE alg=dir enc=A256GCM
  const keyBytes = crypto.createHash('sha256').update(SECRET).digest();
  const key = await jose.importJWK({ kty: 'oct', k: Buffer.from(keyBytes).toString('base64url'), alg: 'A256GCM', ext: true }, 'A256GCM');
  try {
    const { payload } = await jose.compactDecrypt(token, key);
    const obj = JSON.parse(new TextDecoder().decode(payload));
    console.log('DECODED OK. keys:', Object.keys(obj));
    console.log('name:', obj.name, '| email:', obj.email);
    console.log('has accessToken:', !!obj.accessToken, '| roles:', JSON.stringify(obj.roles));
    console.log('exp:', obj.exp, '| now:', Math.floor(Date.now() / 1000), '| valid:', obj.exp > Math.floor(Date.now() / 1000));
  } catch (e) {
    console.log('DECODE FAILED:', e.code || e.message);
  }
}
main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
