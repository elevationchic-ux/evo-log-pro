# -*- coding: utf-8 -*-
"""Affiche l'utilisateur admin et son company_id + compte des seeds smoke."""
import sqlite3

DB = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend\kamlog_erp.db"
con = sqlite3.connect(DB)
try:
    for row in con.execute(
        "SELECT id, email, company_id, is_superuser FROM users LIMIT 5"
    ):
        print("user:", row)
    for q, label in (
        ("SELECT id, code, company_id FROM tiers", "tiers"),
        ("SELECT id, reference, company_id FROM missions", "missions"),
        ("SELECT id, reference, company_id FROM commandes", "commandes"),
        ("SELECT id, code, company_id FROM prestataires", "prestataires"),
    ):
        try:
            print(label, con.execute(q).fetchall())
        except Exception as e:
            print(label, "ERR", e)
finally:
    con.close()
