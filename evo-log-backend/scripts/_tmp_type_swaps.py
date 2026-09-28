"""Analyse temporaire : divergences de FAMILLE de type modele <-> base replay.

Sert a dimensionner la migration 028 (colonnes que le modele declare String
alors que la base porte un horodatage, et l'inverse).
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlalchemy as sa  # noqa: E402
from scripts.audit_schema_drift import MODELES_EN_ECHEC  # noqa: E402
from app.core.database import Base  # noqa: E402

CIBLE = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "_tmpreplay" / "kamlog_replay.db")
con = sqlite3.connect(CIBLE)
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
base = {
    t: {r[1]: (r[2].upper(), r[3], r[4]) for r in cur.execute("PRAGMA table_info('%s')" % t)}
    for t in tables
}

print("modules en echec:", MODELES_EN_ECHEC)
print("tables modeles:", len(Base.metadata.tables), " tables base:", len(tables))

swaps, defauts_manquants = [], []
for nom, table in sorted(Base.metadata.tables.items()):
    si = base.get(nom)
    if si is None:
        continue
    for col in table.columns:
        if col.name not in si:
            continue
        tsql, notnull, dflt = si[col.name]
        fam = tsql.split("(")[0].strip()
        est_date = fam in ("DATE",)
        est_horodate = fam in ("DATETIME", "TIMESTAMP")
        if isinstance(col.type, sa.String) and (est_date or est_horodate):
            swaps.append((nom, col.name, tsql, str(col.type)))
        if notnull and dflt is None and col.server_default is not None:
            defauts_manquants.append((nom, col.name, tsql))

print("\n== colonnes String modele / date-horodate base ==")
for x in swaps:
    print("  ", x)
print("\n== NOT NULL sans DEFAULT en base alors que le modele porte un server_default ==")
for x in defauts_manquants:
    print("  ", x)
print("\ntotaux: swaps=%d defauts=%d" % (len(swaps), len(defauts_manquants)))
