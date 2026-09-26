import os
import sqlite3

db = os.path.join(os.path.dirname(__file__), "..", "kamlog_erp.db")
c = sqlite3.connect(db)
tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table'").fetchall()]
cand = [t for t in tabs if any(k in t for k in ("corridor", "procedure_tir", "poste_frontalier", "frais", "incident"))]
cand += [t for t in ("missions", "camions", "transport_pannes") if t in tabs]
for t in sorted(set(cand)):
    n = c.execute(f"select count(*) from {t}").fetchone()[0]
    print(f"{t:35} {n}")
