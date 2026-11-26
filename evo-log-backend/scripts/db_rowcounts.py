"""Compte les lignes reelles des tables principales (debug local, aucun ecrit)."""
import sqlite3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "kamlog_erp.db"
conn = sqlite3.connect(path)
tables = [r[0] for r in conn.execute(
    "select name from sqlite_master where type='table' order by name")]
non_empty = []
for t in tables:
    try:
        n = conn.execute(f"select count(*) from {t}").fetchone()[0]
    except Exception:
        continue
    if n:
        non_empty.append((t, n))
print(f"tables={len(tables)} non_vide={len(non_empty)}")
for t, n in sorted(non_empty, key=lambda x: -x[1])[:40]:
    print(f"  {t:45s} {n}")
focus = ["users", "companies", "factures", "factures_ohada", "documents",
         "archivages_legal", "entrepots", "stocks", "audit_logs"]
print("--- focus ---")
for t in focus:
    try:
        print(f"  {t:25s} {conn.execute('select count(*) from ' + t).fetchone()[0]}")
    except Exception as e:
        print(f"  {t:25s} ERR {e}")
