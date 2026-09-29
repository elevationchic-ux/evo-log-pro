"""Sonde CORS reelle de la prod, depuis l'origine Vercel.
Reproduit ce que fait le navigateur : preflight OPTIONS puis POST, avec
l'en-tete Origin. Affiche status + access-control-allow-origin/credentials.
"""
import json
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"
ORIGIN = "https://evo-log-pro.vercel.app"
HOPBYHOP = {"access-control-allow-origin", "access-control-allow-credentials",
            "access-control-allow-methods", "access-control-allow-headers", "vary"}


def hdrs(msg):
    return {k.lower(): v for k, v in msg.headers.items() if k.lower() in HOPBYHOP}


def raw(method, path, body=None, extra=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Origin": ORIGIN}
    if extra:
        headers.update(extra)
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, hdrs(r), r.read().decode()[:120]
    except urllib.error.HTTPError as e:
        return e.code, hdrs(e.headers), e.read().decode()[:120]
    except Exception as e:
        return f"ERR {type(e).__name__}", {}, str(e)[:120]


st, h, b = raw("OPTIONS", "/api/v1/auth/login", extra={
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
})
print(f"PREFLIGHT OPTIONS -> {st}")
print("   headers CORS :", h)

st, h, b = raw("POST", "/api/v1/auth/login", {"username": "CADC TECH", "password": "@C2A0D2C6"})
print(f"POST login (bon)  -> {st}")
print("   headers CORS :", h)
print("   body :", b)

st, h, b = raw("POST", "/api/v1/auth/login", {"username": "CADC TECH", "password": "mauvais"})
print(f"POST login (faux) -> {st}")
print("   headers CORS :", h)
