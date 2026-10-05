import sqlite3

conn = sqlite3.connect("kamlog_erp.db")
cols = [r[1] for r in conn.execute("PRAGMA table_info(ports_cameroun)")]
print("COLS:", cols)
for row in conn.execute("SELECT * FROM ports_cameroun LIMIT 30"):
    print(row)
