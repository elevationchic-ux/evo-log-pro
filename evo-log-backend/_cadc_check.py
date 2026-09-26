import sqlite3
c = sqlite3.connect("_tmp_cadc_check.db")
cur = c.cursor()
cols_u = [r[1] for r in cur.execute("PRAGMA table_info(users)")]
cols_p = [r[1] for r in cur.execute("PRAGMA table_info(subscription_plans)")]
print("users has matricule:", "matricule" in cols_u, "| job_title:", "job_title" in cols_u)
print("plans has max_modules:", "max_modules" in cols_p)
row = cur.execute(
    "SELECT username, email, role_level, is_superuser, must_change_password, company_id, substr(hashed_password,1,7) "
    "FROM users WHERE username='CADC TECH'"
).fetchone()
print("CADC user:", row)
link = cur.execute(
    "SELECT r.name, r.level, r.is_system FROM user_roles ur JOIN roles r ON r.id=ur.role_id "
    "JOIN u2 ON 1=1" if False else
    "SELECT r.name, r.level, r.is_system FROM user_roles ur JOIN roles r ON r.id=ur.role_id "
    "JOIN users us ON us.id=ur.user_id WHERE us.username='CADC TECH'"
).fetchall()
print("CADC role links:", link)
c.close()
