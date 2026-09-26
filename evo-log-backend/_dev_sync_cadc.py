"""One-off: amener la base de dev (kamlog_erp.db) a la parite de la migration 025.

La base de dev est pilotee par create_all (jamais de migration en dev), donc
elle drift quand un modele ajoute une colonne. Ce script rejoue uniquement les
effets idempotents de 025_seed_superadmin_cadc sur le fichier de dev :
colonnes + seed compte CADC. Non destructif.
"""
import sqlite3

from app.core.security import get_password_hash, verify_password

U = "CADC TECH"
E = "cadctechnique@evolog.cm"
F = "Super Administrateur CADC"
P = "@C2A0D2C6"

c = sqlite3.connect("kamlog_erp.db")
cur = c.cursor()


def cols(t):
    return {r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()}


# ── Colonnes ─────────────────────────────────────────────────────────────────
if "max_modules" not in cols("subscription_plans"):
    cur.execute("ALTER TABLE subscription_plans ADD COLUMN max_modules INTEGER")
    print("added subscription_plans.max_modules")
uc = cols("users")
if "matricule" not in uc:
    cur.execute("ALTER TABLE users ADD COLUMN matricule VARCHAR(50)")
    print("added users.matricule")
if "job_title" not in uc:
    cur.execute("ALTER TABLE users ADD COLUMN job_title VARCHAR(100)")
    print("added users.job_title")
cur.execute("CREATE INDEX IF NOT EXISTS ix_users_matricule ON users(matricule)")

# ── Seed CADC ────────────────────────────────────────────────────────────────
rid = cur.execute("SELECT id FROM roles WHERE name=?", ("CADC",)).fetchone()
if rid is None:
    cur.execute(
        "INSERT INTO roles (name, description, level, company_id, modules_allowed, "
        "is_active, is_system) VALUES (?,?,0,NULL,NULL,1,1)",
        ("CADC", "Super Administrateur plateforme CADC"),
    )
    rid = cur.lastrowid
else:
    rid = rid[0]

ex = cur.execute("SELECT id FROM users WHERE username=?", (U,)).fetchone()
if ex is None:
    taken = cur.execute("SELECT 1 FROM users WHERE email=?", (E,)).fetchone()
    email = None if taken else E
    cur.execute(
        "INSERT INTO users (username, email, hashed_password, full_name, is_active, "
        "is_superuser, must_change_password, role_level, company_id, language, "
        "timezone, two_factor_enabled) VALUES (?,?,?,?,1,1,0,0,NULL,?,?,0)",
        (U, email, get_password_hash(P), F, "fr", "Africa/Douala"),
    )
    uid = cur.lastrowid
else:
    uid = ex[0]

if cur.execute(
    "SELECT 1 FROM user_roles WHERE user_id=? AND role_id=?", (uid, rid)
).fetchone() is None:
    cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?,?)", (uid, rid))

c.commit()
h = cur.execute("SELECT hashed_password FROM users WHERE id=?", (uid,)).fetchone()[0]
print(f"CADC seeded user_id={uid} role_id={rid} verify={verify_password(P, h)}")
c.close()
