"""Sondes differentielles login prod (app stable) :
- utilisateur INEXISTANT + mot de passe -> doit renvoyer 401 (court-circuit
  `not user`) dans le code courant ;
- CADC TECH -> 500 observe.
Si inexistant=401 et existant=500, l'exception se situe APRES la verification
du mot de passe (payload/roles/company), sinon dans le SELECT lui-meme.
"""
import json
import time
import urllib.request

BASE = "https://evo-log-backend-production.up.railway.app"


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return "ERR", f"{type(e).__name__} {e}"


for label, body in [
    ("inexistant", {"username": "zzz__no_such_user__999", "password": "Xy9!nope"}),
    ("inexistant2", {"username": "ghost.user.probe", "password": "Xy9!nope"}),
    ("cadctech", {"username": "CADC TECH", "password": "@C2A0D2C6"}),
]:
    code, text = post("/api/v1/auth/login", body)
    print(f"{label} -> {code} ({text})")
    time.sleep(3)
