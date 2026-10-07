# -*- coding: utf-8 -*-
"""Inventorie les tables candidates pour le smoke test (ids seed)."""
import re
import sqlite3

DB = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend\kamlog_erp.db"
con = sqlite3.connect(DB)
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("tables total:", len(tables))
pat = re.compile(r"escale|mission|client|tiers|fourniss|commande|conteneur|facture|reglement|reservation|document|supplier|prestataire")
for t in sorted(tables):
    if pat.search(t):
        try:
            n = con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
            first = None
            if n:
                first = con.execute("SELECT id FROM %s LIMIT 1" % t).fetchone()[0]
            print("%-32s rows=%-6d first_id=%s" % (t, n, first))
        except Exception as e:
            print("%-32s ERR %s" % (t, str(e)[:60]))
con.close()
