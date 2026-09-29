"""Sonde courte : 4 cycles health+login, timeout 15s, sortie flush immediate."""
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
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, time.time() - t, r.headers.get("access-control-allow-origin", "-")
    except urllib.error.HTTPError as e:
        return e.code, time.time() - t, e.headers.get("access-control-allow-origin", "-")
    except Exception as e:
        return f"ERR:{type(e).__name__}", time.time() - t, "-"


for i in range(4):
    hs, ht, hca = call("/api/health")
    print(f"[{time.strftime('%H:%M:%S')}] health {hs} {ht:4.1f}s acao={hca}", flush=True)
    ls, lt, lca = call("/api/v1/auth/login", method="POST",
                       body={"username": "ghost.probe", "password": "x"})
    print(f"[{time.strftime('%H:%M:%S')}] login  {ls} {lt:4.1f}s acao={lca}", flush=True)
