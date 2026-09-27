import app.main as m
from fastapi.testclient import TestClient

print("app id:", id(m.app), "class:", type(m.app).__name__)
print("len routes:", len(m.app.routes))
# hit a real endpoint
with TestClient(m.app) as c:
    r = c.get("/api/v1/saas/console/companies")
    print("console GET status:", r.status_code)
    r2 = c.get("/api/v1/company-admin/profil")
    print("company-admin GET status:", r2.status_code)
    # list route paths that include a router with 'auth'
    import json
    oa = c.get("/api/openapi.json")
    j = oa.json()
    print("openapi paths count:", len(j.get("paths", {})))
    print("has console:", any("console" in p for p in j.get("paths", {})))
    print("has company-admin:", any("company-admin" in p for p in j.get("paths", {})))
