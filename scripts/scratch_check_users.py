# -*- coding: utf-8 -*-
"""Inspect dev DB users and (re)seed a known admin login if missing."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "evo-log-backend" / "kamlog_erp.db"

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    n = cur.execute("select count(*) from users").fetchone()[0]
    print("users:", n)
    rows = cur.execute(
        "select id, username, email, is_active, is_superuser, substr(hashed_password,1,10) from users limit 10"
    ).fetchall()
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    main()
