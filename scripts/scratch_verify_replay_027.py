"""Verif replay SQLite vierge de la chaine alembic 001->027 + seed CADC."""
import sqlite3

DB = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend\_ci_replay.db"
c = sqlite3.connect(DB)
print("version:", c.execute("SELECT version_num FROM alembic_version").fetchall())
print("tables:", c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0])
print("cadc_user:", c.execute(
    "SELECT username, is_active, is_superuser, must_change_password, two_factor_enabled "
    "FROM users WHERE username LIKE 'CADC%'"
).fetchall())
print("cadc_role:", c.execute(
    "SELECT name, is_active, is_system, level FROM roles WHERE name='CADC'"
).fetchall())
print("user_roles:", c.execute(
    "SELECT COUNT(*) FROM user_roles ur JOIN users u ON u.id=ur.user_id "
    "JOIN roles r ON r.id=ur.role_id WHERE u.username LIKE 'CADC%' AND r.name='CADC'"
).fetchone()[0])
