# -*- coding: utf-8 -*-
"""Applique la revision 024 (chaine documentaire) directement sur la base SQLite
locale, de facon idempotente (colonnes NULLables uniquement, aucune donnee)."""
import sqlite3
import sys

DB = "kamlog_erp.db"

COLONNES = {
    "declarations_douaniere_avance": ["conteneur_id INTEGER", "escale_id INTEGER", "numero_bl TEXT"],
    "declarations_entrepot": ["conteneur_id INTEGER", "numero_bl TEXT"],
    "missions": ["conteneur_id INTEGER", "numero_bl TEXT"],
    "factures_ohada": ["conteneur_id INTEGER", "escale_id INTEGER"],
}

con = sqlite3.connect(DB)
cur = con.cursor()
tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
changed = 0
for table, cols in COLONNES.items():
    if table not in tables:
        print(f"{table}: table absente, ignoree")
        continue
    have = {r[1] for r in cur.execute(f"PRAGMA table_info({table})")}
    for decl in cols:
        name = decl.split()[0]
        if name in have:
            continue
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {decl}")
        changed += 1
        print(f"{table}: + {decl}")
        cur.execute(f"CREATE INDEX IF NOT EXISTS ix_{table}_{name} ON {table} ({name})")
con.commit()
con.close()
print(f"OK, {changed} colonne(s) ajoutee(s)")
sys.exit(0)
