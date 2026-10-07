import sqlite3
c = sqlite3.connect('kamlog_erp.db')
r = c.execute("select name from sqlite_master where type='table' and (name like '%entrepot%' or name like '%magasin%' or name like '%depot%' or name like '%warehouse%' or name like '%lieu_stock%')").fetchall()
print('warehouse-like tables:', r)
