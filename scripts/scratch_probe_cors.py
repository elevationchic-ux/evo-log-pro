"""Sonde CORS reelle de la prod.

Envoie une vraie requete cross-origin (avec header Origin = Vercel) et lit les
en-tetes Access-Control-* de la reponse. Distingue 3 cas :
  - preflight OPTIONS -> doit renvoyer ACAO + ACA-Headers sinon le navigateur bloque
  - POST /auth/login  -> doit echo l'ACAO de l'origine + AC-Credentials:true
  - /api/health       -> reponse de base (verifie si l'app est en ligne vs 502 proxy)
"""
import json
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"
ORIGIN = "https://evo-log-pro.vercel.app"

CORS_HDRS = [
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "access-control-allow-methods",
    "access-control-allow-headers",
    "vary",
]


def call(path, method="GET", body=None, extra=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Origin": ORIGIN}
    if data:
        headers["Content-Type"] = "application/json"
    if extra:
        headers.update(extra)
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read().decode()[:120]
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()[:120]
    except Exception as e:
        return "ERR", {}, f"{type(e).__name__}: {e}"


def show(tag, status, hdrs, body):
    print(f"\n=== {tag} -> {status} ===")
    found = {k: v for k, v in hdrs.items() if k.lower() in CORS_HDRS}
    if found:
        for k, v in found.items():
            print(f"  {k}: {v}")
    else:
        print("  (AUCUN en-tete CORS)")
    if body:
        print(f"  body: {body}")


# 1) sante : l'app est-elle en ligne (vs 502 proxy) ?
st, h, b = call("/api/health")
show("GET /api/health", st, h, b)

# 2) preflight CORS sur login
st, h, b = call("/api/v1/auth/login", method="OPTIONS", extra={
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
})
show("OPTIONS /auth/login (preflight)", st, h, b)

# 3) POST login reel (mauvais mdp -> 401 attendu, mais avec ACAO ?)
st, h, b = call("/api/v1/auth/login", method="POST",
                body={"username": "ghost.cors.probe", "password": "wrong"})
show("POST /auth/login (ghost)", st, h, b)
