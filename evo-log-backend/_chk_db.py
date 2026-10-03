import sqlite3
c = sqlite3.connect("kamlog_erp.db")
print("cautions:", c.execute("select id, reference from cautions_douanieres").fetchall())
print("dum:", c.execute("select id, numero_dum from dum_customs_records").fetchall())
print("emplacements:", c.execute("select id, code, statut from parc_emplacements limit 6").fetchall())
print("mouvements:", c.execute("select count(*) from parc_mouvements").fetchall())
