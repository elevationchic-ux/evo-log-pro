import sqlite3
c = sqlite3.connect('kamlog_erp.db')
for t in ['companies','users','fournisseurs','magasins','prestataires','clients','tiers']:
    r = c.execute("select name from sqlite_master where type='table' and name=?", (t,)).fetchone()
    print(t, 'present' if r else 'MISSING')
