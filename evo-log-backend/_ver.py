import sqlite3

con = sqlite3.connect("kamlog_erp.db")
cur = con.cursor()
try:
    print("alembic_version:", cur.execute("select version_num from alembic_version").fetchall())
except Exception as exc:
    print("pas de table alembic_version:", exc)
n = cur.execute("select count(name) from sqlite_master where type='table'").fetchone()[0]
print("tables:", n)
con.close()
