"""Sonde l'API Railway en production: le compte CADC existe-t-il, la base est-elle up?

Juste assez de requetes pour ne pas declencher le rate-limit (10/min sur /login).
"""
import json
import urllib.request
import urllib.error

BASE = "https://evo-log-backend-production.up.railway.app"


def call(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()[:400].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode("utf-8", "replace")
    except Exception as e:
        return None, repr(e)


# 1. Sante du backend
print("health:", call("GET", "/health"))

# 2. Tentatives d'identifiants (3 max, rate-limit)
for ident in ("CADC TECH", "cadctechnique@evolog.cm"):
    st, body = call("POST", "/api/v1/auth/login",
                    {"username": ident, "password": "@C2A0D2C6"})
    print(f"login[{ident}] -> {st}: {body}")

# 3. Controle: un compte qui devrait exister si le bootstrap env a ete pose
st, body = call("POST", "/api/v1/auth/login",
                {"username": "admin", "password": "admin123"})
print(f"login[admin] -> {st}: {body}")
