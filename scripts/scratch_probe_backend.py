import urllib.request, urllib.error, json
BASE = "http://127.0.0.1:8000"

def call(path, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return "ERR", str(e)

# Login
s, b = call("/api/v1/auth/login", "POST", {"username":"admin@evolog.cm","password":"admin123"})
assert s == 200, (s, b[:200])
tok = json.loads(b)["access_token"]
print("OK login")

# Probe wave 6
for path in [
    "/api/v1/maintenance-industrielle/nomenclatures",
    "/api/v1/tracabilite/nomenclatures",
    "/api/v1/maintenance-industrielle/assets",
    "/api/v1/tracabilite/events",
]:
    s, b = call(path, token=tok)
    print(f"  {path}: {s} {b[:80]}")
