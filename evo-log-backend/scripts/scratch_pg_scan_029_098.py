# Scan statique des migrations 029-098 pour motifs cassants sur PostgreSQL.
import re
import pathlib

suspects = []
patts = [
    (r"CREATE\s+TABLE[^;]*\bTEXT\s*\(\s*\d", "TEXT(n) brut"),
    (r"AUTOINCREMENT", "AUTOINCREMENT"),
    (r"PRAGMA", "PRAGMA"),
    (r"strftime", "strftime"),
    (r"\bGLOB\b", "GLOB"),
    (r"\bINSERT\s+OR\s+(REPLACE|IGNORE)", "INSERT OR ..."),
    (r"sqlite_master", "sqlite_master"),
    (r"\bColumn\(Text\(\d", "Text(n) dans l'AST"),
]
for p in sorted(pathlib.Path("migrations/versions").glob("*.py")):
    s = p.read_text(encoding="utf-8", errors="replace")
    for pat, tag in patts:
        if re.search(pat, s, re.I):
            suspects.append((p.name, tag))

for x in suspects:
    print(x)
print("suspects:", len(suspects))

# Puis: compiler le DDL cree par chaque migration expansion via la metadata
# ORM (les 029+ sont generees et utilisent create_all sur des tables ORM).
import importlib
from pathlib import Path

dossier = Path("app/models")
for f in sorted(dossier.glob("*.py")):
    if f.name == "__init__.py":
        continue
    importlib.import_module("app.models.%s" % f.name[:-3])
from app.core.database import Base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

pg = postgresql.dialect()
bad = []
for name, table in Base.metadata.tables.items():
    ddl = str(CreateTable(table).compile(dialect=pg))
    if re.search(r"\bTEXT\(\d", ddl, re.I):
        bad.append(name)
print("tables PG-invalides via ORM:", bad, "total metadata:", len(Base.metadata.tables))
