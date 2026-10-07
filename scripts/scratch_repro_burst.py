# -*- coding: utf-8 -*-
"""Reproduction de la cascade « injoignable » : rafale concurrente simulant un
chargement de module (nomenclatures + listes + health), mesure des latences.

Usage: python scratch_repro_burst.py [base_url] [concurrency]
"""
import sys, time, json, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40
TIMEOUT = 15.0  # calque le timeout axios du frontend

def http(path, token=None, method="GET", data=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=(json.dumps(data).encode() if data else None),
                                 headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=TIMEOUT)
        r.read()
        return round(time.time() - t0, 2), None
    except urllib.error.HTTPError as e:
        e.read()
        return round(time.time() - t0, 2), f"HTTP {e.code}"
    except Exception as e:
        return round(time.time() - t0, 2), type(e).__name__ + ":" + str(e)[:40]

# login (warm)
st, err = None, None
req = urllib.request.Request(BASE + "/api/v1/auth/login", method="POST",
                             data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
                             headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access_token"]

PATHS = [
    "/api/v1/logistique-3pl/nomenclatures",
    "/api/v1/logistique-3pl/tpl-crossdocks",
    "/api/v1/logistique-3pl/tpl-contracts",
    "/api/v1/logistique-3pl/tpl-warehouses",
    "/health",
]

results = []
def burst():
    paths = (PATHS * ((N // len(PATHS)) + 1))[:N]
    with ThreadPoolExecutor(max_workers=N) as ex:
        futs = [ex.submit(http, p, token) for p in paths]
        for f in futs:
            results.append(f.result())

t0 = time.time()
burst()
wall = round(time.time() - t0, 2)
lat = sorted(r[0] for r in results)
errs = [r for r in results if r[1]]
print(f"BASE={BASE} N={N} wall={wall}s")
print(f"lat min={lat[0]} med={lat[len(lat)//2]} p90={lat[int(len(lat)*0.9)]} max={lat[-1]}")
print(f"errors={len(errs)}/{N}")
for e in errs[:8]:
    print("   ", e)
