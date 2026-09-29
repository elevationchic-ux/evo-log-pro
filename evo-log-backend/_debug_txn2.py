"""Test join_transaction_mode='create_savepoint' isolation with session.rollback()."""
import os, sys
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.conftest import _ensure_tables, engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from app.utils.numerotation import prochaine_reference

_ensure_tables()

# Test 1: basic flow with create_savepoint
print("=== Test 1: commit ===")
conn = engine.connect()
trans = conn.begin()
session = Session(bind=conn, join_transaction_mode="create_savepoint")
ref1 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 5, 1))
session.commit()
print(f"  ref1={ref1}")
trans.rollback()
conn.close()

# Test 6 (the problematic one with explicit rollback):
print("=== Test 6: rollback within session ===")
conn = engine.connect()
trans = conn.begin()
session = Session(bind=conn, join_transaction_mode="create_savepoint")
ref1 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 3, 1))
session.rollback()  # Should only rollback the savepoint
ref2 = prochaine_reference(session, "FACTURE", date_reference=date(2026, 3, 1))
session.commit()
print(f"  ref1={ref1}, ref2={ref2}")
trans.rollback()
conn.close()

# Test 2: check if state leaked
print("=== Test 2: fresh transaction ===")
conn = engine.connect()
trans = conn.begin()
session = Session(bind=conn, join_transaction_mode="create_savepoint")
ref = prochaine_reference(session, "FACTURE", date_reference=date(2026, 9, 1))
print(f"  next ref should be FAC-2026-0001: got {ref}")
session.commit()
trans.rollback()
conn.close()

# Check table state
print("=== Check sequences table ===")
with engine.connect() as c:
    rows = c.execute(text("SELECT company_id, type_document, exercice, courant FROM sequences_numerotation")).fetchall()
    print(f"  Remaining rows: {len(rows)}")
