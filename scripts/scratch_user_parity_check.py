"""Compare les colonnes ORM User avec une DB rejouee vierge (001->head).

Si l'ORM reclame une colonne que la chaine ne cree pas, tout SELECT User
(=> tout login) leve une erreur 500 sur le moteur strict (PostgreSQL),
silencieusement toleree la ou la colonne existe deja (prod bootstrappee
par create_all, tests sur SQLite deja complete).
"""
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "evo-log-backend")
sys.path.insert(0, BASE)

import sqlalchemy as sa  # noqa: E402
from app.models.user import User, Role  # noqa: E402

# 1. Colonnes ORM
orm_user_cols = {c.name for c in User.__table__.columns}
orm_role_cols = {c.name for c in Role.__table__.columns}

# 2. Colonnes d'une DB vierge rejouee ( cree par scratch_replay_clean )
db = os.path.join(BASE, "_ci_replay_clean.db")
if not os.path.exists(db):
    print("DB de replay absente:", db, "- lance scratch_replay_clean.py d'abord")
    sys.exit(2)

eng = sa.create_engine("sqlite:///" + db)
insp = sa.inspect(eng)


def missing(table, orm_cols):
    if table not in insp.get_table_names():
        return f"TABLE {table} ABSENTE"
    db_cols = {c["name"] for c in insp.get_columns(table)}
    miss = sorted(orm_cols - db_cols)
    return f"manquant(s) dans {table}: {miss}" if miss else f"{table}: parite OK ({len(orm_cols)} colonnes)"


print(missing("users", orm_user_cols))
print(missing("roles", orm_role_cols))
for t in ("user_roles", "permissions", "role_permissions"):
    if t in insp.get_table_names():
        print(f"{t}: presente")
    else:
        print(f"TABLE {t} ABSENTE")
