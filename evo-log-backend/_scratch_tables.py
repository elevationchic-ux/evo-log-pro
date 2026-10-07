import sqlite3
c = sqlite3.connect('kamlog_erp.db')
print(c.execute("select name from sqlite_master where type='table' and (name like '%navire%' or name like '%vessel%' or name like '%bateau%')").fetchall())
