import glob
import sqlite3

paths = glob.glob("*.db") + glob.glob("instance/*.db") + glob.glob("app/*.db") + glob.glob("*.sqlite*")
print("dbs:", paths)
con = sqlite3.connect(paths[0])
print("plan_comptable:", con.execute("select count(*) from plan_comptable_ohada").fetchone()[0])
print("journaux:", con.execute("select count(*) from journaux_auxiliaires_ohada").fetchone()[0])
print("exercices:", con.execute("select numero_exercice, statut from exercices_comptables_ohada").fetchall())
print("alembic_version:", con.execute("select version_num from alembic_version").fetchall())
con.close()
