# Scratch batch 15 : verification apres purge.
# 1) Etat de la base de dev (lecture seule) : plus aucune ligne testserver.
# 2) Smoke boot de l'app via TestClient AVEC garde-fou DATABASE_URL=:memory:
#    (identique au conftest pytest) pour ne pas re-polluer le fichier de dev.
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 1. Inventaire post-purge (lecture seule) -------------------------------
c = sqlite3.connect("file:kamlog_erp.db?mode=ro", uri=True)
ts = c.execute("SELECT COUNT(*) FROM audit_logs WHERE url LIKE 'http://testserver%'").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
companies = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
c.close()
print(f"POST-PURGE: audit_logs={total} (testserver restants={ts}) users={users} companies={companies}")
assert ts == 0, "des lignes pytest subsistent !"

# --- 2. Smoke boot sans toucher le fichier de dev ---------------------------
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "disabled"
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

with TestClient(app) as client:
    r = client.get("/api/health")
    print("GET /api/health ->", r.status_code, r.json())
    assert r.status_code == 200

m = sqlite3.connect("file:kamlog_erp.db?mode=ro", uri=True)
ts2 = m.execute("SELECT COUNT(*) FROM audit_logs WHERE url LIKE 'http://testserver%'").fetchone()[0]
m.close()
assert ts2 == 0, "le smoke boot a re-ecrit dans la base de dev !"
print("SMOKE OK  le boot applicatif n'a pas re-pollue kamlog_erp.db")
