# Scratch batch 15 : quantifier la pollution audit_logs (base de dev).
import sqlite3

c = sqlite3.connect("file:kamlog_erp.db.bak-pre-b15?mode=ro", uri=True)
q = lambda s, *a: c.execute(s, a).fetchall()

print("total audit_logs:", q("SELECT COUNT(*) FROM audit_logs")[0][0])
print("testserver:", q("SELECT COUNT(*) FROM audit_logs WHERE url LIKE 'http://testserver%'")[0][0])
print("par host (top 8):")
for row in q("SELECT substr(url, 1, instr(substr(url,12), '/')+11) AS host, COUNT(*) "
             "FROM audit_logs GROUP BY host ORDER BY 2 DESC LIMIT 8"):
    print("  ", row)
print("date range testserver:", q("SELECT MIN(created_at), MAX(created_at) FROM audit_logs WHERE url LIKE 'http://testserver%'"))
print("date range autres:", q("SELECT MIN(created_at), MAX(created_at) FROM audit_logs WHERE url NOT LIKE 'http://testserver%'"))
print("dernieres lignes non-testserver (8):")
for row in q("SELECT id, method, substr(url,1,70), status_code, created_at FROM audit_logs "
             "WHERE url NOT LIKE 'http://testserver%' ORDER BY id DESC LIMIT 8"):
    print("  ", row)
print()
print("users:", q("SELECT id, username, email, is_superuser, company_id, role_level FROM users ORDER BY id"))
print()
print("companies:", q("SELECT id, nom, code, is_active FROM companies ORDER BY id"))
print("organizations:", q("SELECT id, name FROM organizations ORDER BY id") if q("SELECT 1 FROM sqlite_master WHERE name='organizations'") else "n/a")
print("agencies:", q("SELECT id, nom, code FROM agencies ORDER BY id") if q("SELECT 1 FROM sqlite_master WHERE name='agencies'") else "n/a")
print("alembic:", q("SELECT * FROM alembic_version"))
