# -*- coding: utf-8 -*-
import sqlite3
con = sqlite3.connect("kamlog_erp.db")
print("alembic version:", con.execute("select version_num from alembic_version").fetchall())
print("heavylift tables:", [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'heavylift%'").fetchall()])
print("pipeline tables:", [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'pipeline%'").fetchall()])
print("courier tables:", [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'courier%'").fetchall()])
print("coldchain tables:", [r[0] for r in con.execute("select name from sqlite_master where type='table' and name like 'coldchain%'").fetchall()])
con.close()
