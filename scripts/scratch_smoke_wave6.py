"""Smoke wave 6 : frappe les 178 endpoints de maintenance + tracabilite via TestClient."""
import sys, json
sys.path.insert(0, ".")
from fastapi.testclient import TestClient

import app.main
from app.main import app as fastapi_app

client = TestClient(fastapi_app)

# 1. Health check
r = client.get("/api/v1/health")
print("health:", r.status_code, r.json() if r.status_code == 200 else r.text[:100])

# 2. Attempt to hit wave 6 nomenclature routes without auth — expect 401/403
for path in [
    "/api/v1/maintenance-industrielle/nomenclatures",
    "/api/v1/tracabilite/nomenclatures",
    "/api/v1/maintenance-industrielle/assets",
    "/api/v1/tracabilite/events",
]:
    r = client.get(path)
    print(f"  {path}: {r.status_code}")

# 3. Authenticated smoke: login as super admin, hit each GET
r = client.post("/api/v1/auth/login", json={"email": "superadmin@kamlog.cm", "password": "Admin.2024!"})
if r.status_code != 200:
    r = client.post("/api/v1/auth/login", json={"email": "admin@kamlog.cm", "password": "Admin.2024!"})
print("login:", r.status_code, r.json() if r.status_code == 200 else r.text[:200])
if r.status_code == 200:
    tok = r.json().get("access_token")
    H = {"Authorization": f"Bearer {tok}"}
    # Try each GET endpoint
    schemas = fastapi_app.openapi()
    ok = err = 0
    errs = []
    for p, methods in schemas["paths"].items():
        if "maintenance-industrielle" in p or "tracabilite" in p:
            if "get" in methods and "{" not in p:
                rr = client.get(p, headers=H)
                if rr.status_code == 200:
                    ok += 1
                else:
                    err += 1
                    errs.append((p, rr.status_code, rr.text[:150]))
    print(f"wave6 GET endpoints: OK={ok}  FAIL={err}")
    for e in errs[:5]:
        print(" ", e)
