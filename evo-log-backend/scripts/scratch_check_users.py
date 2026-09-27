import sqlite3

c = sqlite3.connect("kamlog_erp.db")
tables = {t[0] for t in c.execute("select name from sqlite_master where type='table'")}
cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
print("users 2fa cols:", [x for x in cols if "two_factor" in x or "recovery" in x])
print("has alembic_version:", "alembic_version" in tables)
if "alembic_version" in tables:
    print("version:", [r[0] for r in c.execute("select version_num from alembic_version")])
