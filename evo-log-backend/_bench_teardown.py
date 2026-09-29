"""Benchmark teardown strategies for 318-table in-memory SQLite."""
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

# INSERT one row
Session = sessionmaker(bind=engine)
s = Session()
s.execute(text("INSERT INTO companies (code, nom, sirene, is_active) VALUES ('X','X','X',1)"))
s.commit()
s.close()

# Strategy 1: DELETE all 318 tables
t = time.time()
with engine.connect() as conn:
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    for table in Base.metadata.tables.values():
        conn.execute(table.delete())
    conn.execute(text("PRAGMA foreign_keys=ON"))
    conn.commit()
print(f"DELETE all 318 tables: {(time.time()-t)*1000:.1f}ms")

# Strategy 2: DELETE only tables with rows (track dirty set)
t = time.time()
with engine.connect() as conn:
    conn.execute(text("PRAGMA foreign_keys=OFF"))
    conn.execute(text("DELETE FROM companies"))
    conn.execute(text("PRAGMA foreign_keys=ON"))
    conn.commit()
print(f"DELETE 1 dirty table:   {(time.time()-t)*1000:.1f}ms")

# Strategy 3: SAVEPOINT rollback
t = time.time()
conn3 = engine.connect()
trans = conn3.begin()
conn3.execute(text("INSERT INTO companies (code, nom, sirene, is_active) VALUES ('Y','Y','Y',1)"))
trans.rollback()
conn3.close()
print(f"SAVEPOINT rollback:     {(time.time()-t)*1000:.2f}ms")
