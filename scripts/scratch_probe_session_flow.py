"""Prouve le flow NextAuth 'ticket' contre la prod :
1) POST /api/v1/auth/login (CADC TECH) -> access_token (le navigateur fait ca)
2) GET  /api/v1/auth/session  Bearer <access_token> -> doit renvoyer 200 + access_token
C'est exactement ce que authorize() (cote serveur Vercel) appelle. Si ces deux
etapes passent en prod, le seul maillon qui pouvait casser etait l'API_BASE
serveur (localhost) -> corrige dans src/lib/auth.ts.
"""
import json
import time
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"


def call(path, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()[:200]
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


s1, j1 = call("/api/v1/auth/login", "POST", {"username": "CADC TECH", "password": "@C2A0D2C6"})
tok = (j1 or {}).get("access_token") if isinstance(j1, dict) else None
print(f"1) login        -> {s1} | access_token={'OUI' if tok else 'NON'} | user_id={(j1 or {}).get('user_id') if isinstance(j1, dict) else j1}")
time.sleep(2)
s2, j2 = call("/api/v1/auth/session", "GET", token=tok)
has_tok = isinstance(j2, dict) and j2.get("access_token")
print(f"2) GET /session -> {s2} | access_token={'OUI' if has_tok else 'NON'} | roles={(j2 or {}).get('roles') if isinstance(j2, dict) else j2}")
print("CONTRAT OK" if (s1 == 200 and tok and s2 == 200 and has_tok) else "CONTRAT CASSE")
