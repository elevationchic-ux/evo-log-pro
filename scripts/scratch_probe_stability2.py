"""Caracterise l'instabilite prod : alterne health et login, 10 cycles.

Objectif : distinguer
  - crash-loop global (health ALSO 502 par intervalles), de
  - plantage/timeout specifique au chemin /auth/login (health toujours 200,
    login toujours 502 ou tres lent).
Horodate chaque sonde pour voir la period icite (redemarrages ~ toutes les X s).
"""
import json
import time
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"
ORIGIN = "https://evo-log-pro.vercel.app"


def call(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Origin": ORIGIN}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            acao = r.headers.get("access-control-allow-origin", "-")
            return r.status, time.time() - t, acao
    except urllib.error.HTTPError as e:
        acao = e.headers.get("access-control-allow-origin", "-")
        return e.code, time.time() - t, acao
    except Exception as e:
        return f"ERR:{type(e).__name__}", time.time() - t, "-"


ts0 = time.strftime("%H:%M:%S")
print(f"debut {ts0}")
for i in range(10):
    hs, ht, hca = call("/api/health")
    ls, lt, lca = call("/api/v1/auth/login", method="POST",
                       body={"username": "ghost.probe", "password": "x"})
    stamp = time.strftime("%H:%M:%S")
    print(f"[{stamp}] health {hs} {ht:4.1f}s acao={hca:12s} | login {ls} {lt:4.1f}s acao={lca}")
    time.sleep(3)
