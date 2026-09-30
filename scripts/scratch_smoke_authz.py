"""Smoke-test authentifie EN LIGNE de TOUS les endpoints GET (lecture seule).

1) login superadmin (CADC TECH) -> JWT
2) telecharge /openapi.json (ou /api/v1/openapi.json)
3) pour chaque operation GET SANS parametre de chemin (pas de '{'), appelle avec
   Bearer. Les endpoints a parametre ({id}) sont supposes (risque d'effet de bord
   / 404 sur id invente). POST/PUT/DELETE/PATCH ignores (ecriture).
4) classe chaque reponse. Le VRAI signal de bug = 5xx (500) ou timeout.
   401/403 = RBAC legitime. 404 = route non montee. 422 = requete attendue.

Sortie : compte global + detail par prefixe de module + liste des 500/timeout.
"""
import json
import time
import urllib.request
import urllib.error

BASE = "https://evo-log-backend-production.up.railway.app"
USER, PWD = "CADC TECH", "@C2A0D2C6"


def req(method, path, token=None, timeout=10, body=None):
    url = BASE + path
    headers = {"User-Agent": "smoke"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    else:
        data = None
    r = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return type(e).__name__, b""


# 1) login
st, raw = req("POST", "/api/v1/auth/login", body={"username": USER, "password": PWD})
if st != 200:
    print("LOGIN ECHOUE", st, raw[:200])
    raise SystemExit(1)
token = json.loads(raw)["access_token"]
print("login OK")

# 2) openapi
spec = None
for p in ("/api/v1/openapi.json", "/openapi.json"):
    st, raw = req("GET", p, timeout=15)
    if st == 200:
        try:
            spec = json.loads(raw)
            print("openapi from", p)
            break
        except Exception:
            pass
if spec is None:
    print("OPENAPI INDISPONIBLE")
    raise SystemExit(1)

get_paths = sorted(
    path for path, ops in spec.get("paths", {}).items()
    if "get" in {k.lower() for k in ops} and "{" not in path
)
print("GET sans param:", len(get_paths))

by_prefix = {}
fails_5xx = []
timeouts = []
counts = {}
for i, path in enumerate(get_paths, 1):
    code, _ = req("GET", path, token=token, timeout=10)
    # retry once on cold-start proxy 502 / network
    if code in (502, 503, 504, "timeout", "TimeoutError", "URLError") :
        time.sleep(1.5)
        code, _ = req("GET", path, token=token, timeout=12)
    label = code if isinstance(code, int) else f"ERR:{code}"
    counts[label] = counts.get(label, 0) + 1
    pref = "/" + path.strip("/").split("/")[1] if len(path.strip("/").split("/")) > 1 else path
    by_prefix.setdefault(pref, {})[label] = by_prefix.setdefault(pref, {}).get(label, 0) + 1
    if isinstance(code, int) and code >= 500:
        fails_5xx.append((path, code))
    elif not isinstance(code, int):
        timeouts.append((path, code))
    if i % 25 == 0:
        print(f"  ...{i}/{len(get_paths)}")

print("\n==== COMPTE GLOBAL (code -> nb) ====")
for k in sorted(counts, key=lambda x: str(x)):
    print(f"  {k:>12}: {counts[k]}")

print("\n==== VRAIS BUGS SERVEUR (5xx) ====")
if fails_5xx:
    for path, code in fails_5xx:
        print(f"  {code}  {path}")
else:
    print("  (aucun 5xx - le backend ne plante sur aucun endpoint de lecture)")

print("\n==== TIMEOURS / RESIAU (a re-tester, pas forcement des bugs) ====")
for path, code in timeouts[:40]:
    print(f"  {code}  {path}")
print(f"  total non-HTTP: {len(timeouts)}")

json.dump({"counts": counts, "fails_5xx": fails_5xx, "timeouts": timeouts},
          open("scripts/_smoke_authz.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\necrit scripts/_smoke_authz.json")
