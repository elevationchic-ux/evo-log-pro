import sys
sys.path.insert(0, "evo-log-backend")
sys.path.insert(0, "evo-log-backend/tests")

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
r = c.get("/api/v1/admin-saas/feature-flags")
print("STATUS:", r.status_code)
print("BODY:", r.text[:500])
