import sqlite3

c = sqlite3.connect(":memory:")
c.execute(
    "CREATE TABLE roles (name TEXT, description TEXT, level INTEGER, "
    "company_id INTEGER, modules_allowed TEXT, is_active BOOLEAN, is_system BOOLEAN)"
)
c.execute(
    "INSERT INTO roles (name, description, level, company_id, modules_allowed, "
    "is_active, is_system) VALUES ('t', 'd', 0, NULL, NULL, TRUE, TRUE)"
)
print("roles:", c.execute("SELECT * FROM roles").fetchall())

c.execute(
    "CREATE TABLE users (username TEXT, email TEXT, hashed_password TEXT, "
    "full_name TEXT, is_active BOOLEAN, is_superuser BOOLEAN, "
    "must_change_password BOOLEAN, role_level INTEGER, company_id INTEGER, "
    "language TEXT, timezone TEXT, two_factor_enabled BOOLEAN)"
)
c.execute(
    "INSERT INTO users (username, email, hashed_password, full_name, is_active, "
    "is_superuser, must_change_password, role_level, company_id, language, "
    "timezone, two_factor_enabled) VALUES ('u', 'e', 'h', 'f', TRUE, TRUE, "
    "FALSE, 0, NULL, 'fr', 'Africa/Douala', FALSE)"
)
print("users:", c.execute("SELECT * FROM users").fetchall())
print("SQLITE_OK")
