"""Dump la forme reelle des tables RH dans la base de reference (replay Alembic).

Usage: python scripts/_dump_rh_shape.py [_replay.db]
Sortie: _rh_shape.json (ascii) -- evite la corruption d'encoding de la console.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "_replay.db")

TABLES = [
    "conges", "absences", "temps_travail", "formations", "participations_formation",
    "evaluations_performance", "organigramme", "competences", "competences_employe",
    "primes", "documents_employe", "contrats_travail", "salaires",
]

if not DB.exists():
    print("BASE INTROUVABLE: %s" % DB)
    sys.exit(1)

conn = sqlite3.connect(str(DB))
out = {}
for t in TABLES:
    rows = conn.execute("PRAGMA table_info(%s)" % t).fetchall()
    if not rows:
        out[t] = "ABSENTE"
        continue
    out[t] = [
        {"nom": r[1], "type": r[2], "notnull": bool(r[3]), "defaut": r[4], "pk": bool(r[5])}
        for r in rows
    ]
conn.close()

(ROOT / "_rh_shape.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
print("ecrit: %s" % (ROOT / "_rh_shape.json"))
