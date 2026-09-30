"""Montre l'alternance chaud/froid due au thrash de redéploiement.

6 sondes /api/health espacées de ~18s, timeout court par sonde. Si on voit un
mélange de 200 (fenêtre chaude) et 502/timeout (fenêtre de boot), c'est un
redéploiement en cours (build valide), PAS une panne définitive.
"""
import time
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"


def ping():
    t = time.time()
    try:
        with urllib.request.urlopen(BASE + "/api/health", timeout=12) as r:
            return r.status, time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, time.time() - t
    except Exception as e:
        return type(e).__name__, time.time() - t


for i in range(6):
    st, dt = ping()
    print(f"[{time.strftime('%H:%M:%S')}] health {st} in {dt:4.1f}s", flush=True)
    time.sleep(18)
