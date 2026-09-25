// Diagnostic NextAuth: flux credentials complet avec jar à cookies
const BASE = 'http://127.0.0.1:3000';

function parseSetCookie(header) {
  // "name=value; Path=/; Expires=...; HttpOnly; SameSite=Lax" -> {name, value, attrs}
  const [pair, ...attrs] = header.split(';');
  const idx = pair.indexOf('=');
  return { name: pair.slice(0, idx).trim(), value: pair.slice(idx + 1).trim(), attrs: attrs.map(a => a.trim()) };
}

async function main() {
  const jar = new Map();
  const cookieHeader = () => [...jar.entries()].map(([k, v]) => `${k}=${v}`).join('; ');

  // 1. providers
  let r = await fetch(`${BASE}/api/auth/providers`);
  console.log('providers:', r.status);

  // 2. csrf
  r = await fetch(`${BASE}/api/auth/csrf`);
  const { csrfToken } = await r.json();
  for (const sc of r.headers.getSetCookie()) {
    const c = parseSetCookie(sc);
    if (c.value) jar.set(c.name, c.value); else jar.delete(c.name);
  }
  console.log('csrf:', csrfToken ? csrfToken.slice(0, 12) + '...' : 'MISSING', '| cookies:', [...jar.keys()].join(','));

  // 3. login via callback/credentials (form POST, comme NextAuth v4)
  const body = new URLSearchParams({
    csrfToken,
    json: 'true',
    email: 'admin@evolog.cm',
    username: 'admin@evolog.cm',
    password: 'admin123',
    callbackUrl: `${BASE}/dashboard`,
  });
  r = await fetch(`${BASE}/api/auth/callback/credentials`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', Cookie: cookieHeader() },
    body: body.toString(),
    redirect: 'manual',
  });
  console.log('callback status:', r.status, '| location:', r.headers.get('location'));
  const before = [...jar.keys()].join(',');
  for (const sc of r.headers.getSetCookie()) {
    const c = parseSetCookie(sc);
    console.log('  Set-Cookie:', c.name, '=', (c.value ? c.value.slice(0, 20) + '...' : '(vide/suppression)'), '|', c.attrs.join('; '));
    if (c.value) jar.set(c.name, c.value); else jar.delete(c.name);
  }
  console.log('cookies avant:', before, '-> après:', [...jar.keys()].join(','));

  // 4. session
  r = await fetch(`${BASE}/api/auth/session`, { headers: { Cookie: cookieHeader() } });
  const txt = await r.text();
  console.log('session:', r.status, '| body:', txt.slice(0, 200));
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
