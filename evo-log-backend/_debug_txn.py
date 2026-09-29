"""Debug: test if session.rollback() corrupts the outer transaction."""
import os, sys
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")
sys.path.insert(0, os.path.dirname(__file__))

from tests.conftest import _ensure_tables, engine, TestingSessionLocal
from sqlalchemy import text
from datetime import date
from app.utils.numerotation import prochaine_reference

_ensure_tables()

# Test 1: basic flow
print("=== Test 1: commit ===")
conn = engine.connect()
trans = conn.begin()
session = TestingSessionLocal(bind=conn)
ref1 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 5, 1))
session.commit()  # should flush but not SQL commit
print(f"  ref1={ref1}")
trans.rollback()
conn.close()

# Test 6 (the problematic one with explicit rollback):
print("=== Test 6: rollback within session ===")
conn = engine.connect()
trans = conn.begin()
session = TestingSessionLocal(bind=conn)
ref1 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 3, 1))
session.rollback()  # EXPLICIT session.rollback()
ref2 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 3, 1))
session.commit()
print(f"  ref1={ref1}, ref2={ref2}")
trans.rollback()
conn.close()

# Test 2: check if state leaked
print("=== Test 2: fresh transaction ===")
conn = engine.connect()
trans = conn.begin()
session = TestingSessionLocal(bind=conn)
ref = prochaine_reference(session, "FACTURE", date_reference=date(2026, 9, 1))
print(f"  next ref should be FAC-2026-0001: got {ref}")
trans.rollback()
conn.close()

# Check: what does the SequenceNumerotation table have?
print("=== Check sequences ===")
with engine.connect() as c:
    rows = c.execute(text("SELECT company_id, type_document, exercice, courant FROM sequences_numerotation")).fetchall()
    print(f"  Remaining rows: {len(rows)}")
    for r in rows:
        print(f"    {r}")
