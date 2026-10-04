"""Inspecte le DDL reel de quelques tables SQLite (convention de type des colonnes Enum)."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "evo-log-backend" / "kamlog_erp.db"

conn = sqlite3.connect(DB)
for table in ("dossiers_transit", "ports_cameroun", "factures"):
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    print("=" * 20, table)
    print(row[0] if row else "ABSENTE")
print("=" * 20, "alembic version")
try:
    print(conn.execute("SELECT version_num FROM alembic_version").fetchall())
except sqlite3.OperationalError as exc:
    print("pas de table alembic_version:", exc)
