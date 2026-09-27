import sqlite3

con = sqlite3.connect("kamlog_erp.db")
cur = con.cursor()
for t in ("comptes", "factures", "ecritures_comptables", "paiements"):
    n = cur.execute('select count(*) from "%s"' % t).fetchone()[0]
    print("### %s  (%d lignes)" % (t, n))
    for cid, nom, typ, notnull, dflt, pk in cur.execute('PRAGMA table_info("%s")' % t):
        print("   %-24s %-12s notnull=%d dflt=%s pk=%d" % (nom, typ, notnull, dflt, pk))
con.close()
