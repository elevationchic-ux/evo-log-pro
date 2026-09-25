# -*- coding: utf-8 -*-
"""Sync the dev SQLite DB with the SQLAlchemy models:
- create missing tables (create_all)
- add missing columns (ALTER TABLE ADD COLUMN, SQLite-compatible, nullable)
Dev-only helper; production uses Postgres + alembic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evo-log-backend"))

from sqlalchemy import inspect, text  # noqa: E402
from app.core.database import engine, Base  # noqa: E402
import app.models  # noqa: F401,E402  (register all models on Base.metadata)

ADDITIONAL_TYPES = {}


def sql_type(col):
    return col.type.compile(engine.dialect)


def main():
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    added = 0
    with engine.begin() as conn:
        for table_name, table in Base.metadata.tables.items():
            if not insp.has_table(table_name):
                continue
            existing = {c["name"] for c in insp.get_columns(table_name)}
            for col in table.columns:
                if col.name in existing:
                    continue
                if col.primary_key:
                    continue  # cannot ADD COLUMN a PK in SQLite
                ddl = f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {sql_type(col)}'
                conn.execute(text(ddl))
                added += 1
                print(f"  + {table_name}.{col.name} {sql_type(col)}")
    print(f"\nSync terminee: {added} colonne(s) ajoutee(s).")


if __name__ == "__main__":
    main()
