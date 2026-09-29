"""Benchmark teardown strategies for 318-table in-memory SQLite.
Tests the SAVEPOINT pattern with StaticPool (one shared connection).
"""
import time, os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "disabled")
import app.main
from app.core.database import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
tbl_names = list(Base.metadata.tables.keys())
print(f"Total tables: {len(tbl_names)}")

# Strategy 1: current DELETE-all
N = 10
t = time.time()
for _ in range(N):
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for tbl in Base.metadata.tables.values():
            conn.execute(tbl.delete())
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
per_delete = (time.time() - t) / N
print(f"DELETE-all 318: {per_delete*1000:.1f}ms/test -> {per_delete*589:.0f}s for 589 tests")

# Strategy 2: outer transaction + rollback (SAVEPOINT isolation)
t2 = time.time()
for i in range(N):
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    # Simulate some writes
    session.execute(text(f"INSERT INTO \"{tbl_names[0]}\" (id) VALUES ({i+1})"))
    session.commit()  # savepoint-level, not real commit
    session.close()
    transaction.rollback()
    connection.close()
per_rb = (time.time() - t2) / N
print(f"TX rollback:     {per_rb*1000:.1f}ms/test -> {per_rb*589:.0f}s for 589 tests")
