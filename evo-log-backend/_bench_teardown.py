"""Benchmark teardown strategies for 318-table in-memory SQLite."""
import time, os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")
import app.main
from app.core.database import Base
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)

# Get first table's columns for a generic insert
first_tbl = list(Base.metadata.tables.values())[0]
cols = [c.name for c in first_tbl.columns if not c.primary_key and c.nullable][:2]
tbl_name = first_tbl.name
print(f"Using table '{tbl_name}', cols: {cols}")

# Time N iterations of DELETE-all (simulating 10 tests' teardown)
N = 10
t = time.time()
for _ in range(N):
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for table in Base.metadata.tables.values():
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
per_delete = (time.time() - t) / N
print(f"DELETE all 318 tables: {per_delete*1000:.1f}ms each -> {per_delete*589:.1f}s for 589 tests")

# Time N iterations of rollback-only (no DELETEs)
t2 = time.time()
for _ in range(N):
    conn2 = engine.connect()
    trans = conn2.begin()
    conn2.execute(text(f"INSERT INTO {tbl_name} (id) VALUES (1)"))
    trans.rollback()
    conn2.close()
per_rb = (time.time() - t2) / N
print(f"SAVEPOINT rollback:    {per_rb*1000:.3f}ms each -> {per_rb*589:.1f}s for 589 tests")
