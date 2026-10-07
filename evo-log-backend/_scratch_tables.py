import sqlite3
c = sqlite3.connect('kamlog_erp.db')
r = c.execute("select name from sqlite_master where type='table' and name like '%magasin%'").fetchall()
print('tables matching %magasin%:', r)
