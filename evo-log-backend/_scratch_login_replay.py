"""Reproduce le flux /auth/login complet contre une DB rejouee comme en prod.

But: identifier la ligne qui leve une exception non capturee (500 cote Railway)
alors que la suite pytest passe (fixtures differentes).
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(BASE, "_ci_replay_clean.db")
os.environ.setdefault("SECRET_KEY", "test-secret-replay-parity")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)

for ident, pwd in (("CADC TECH", "@C2A0D2C6"), ("supadmin", "supadmin123"), ("admin", "admin123")):
    r = client.post("/api/v1/auth/login", json={"username": ident, "password": pwd})
    print(f"[{ident}] -> {r.status_code}")
    try:
        body = r.json()
        keys = sorted(body.keys()) if isinstance(body, dict) else body
        print("   keys:", keys)
        if r.status_code == 500:
            print("   body:", str(body)[:500])
    except Exception as e:
        print("   raw:", r.text[:500], e)
