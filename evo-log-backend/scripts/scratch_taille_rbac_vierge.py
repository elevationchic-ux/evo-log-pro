"""Migre une base VIERGE jusqu'a head et compte le RBAC reellement seme.

Sert a ecrire dans docs/RBAC_ACCREDITATIONS.md des chiffres verifies plutot
qu'herites : volume de permissions, roles, grants, et le sous-module `place`
du departement amenagement.
"""
import os
import pathlib
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

RACINE = pathlib.Path(__file__).resolve().parents[1]
db_file = pathlib.Path(tempfile.mkdtemp()) / "vierge_rbactail.db"
url = f"sqlite:///{db_file.as_posix()}"
os.environ["DATABASE_URL"] = url

cfg = Config(str(RACINE / "alembic.ini"))
cfg.set_main_option("script_location", str(RACINE / "migrations"))
command.upgrade(cfg, "head")

engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

scal = lambda q: db.execute(type("X", (), {}) is None or __import__("sqlalchemy").text(q)).scalar()  # noqa: E731
from sqlalchemy import text  # noqa: E402

total_perms = scal("SELECT COUNT(*) FROM permissions")
total_roles = scal("SELECT COUNT(*) FROM roles")
total_grants = scal("SELECT COUNT(*) FROM role_permissions")
domaines = db.execute(text("SELECT domain, COUNT(*) FROM permissions GROUP BY domain ORDER BY domain")).all()
amen = [r[0] for r in db.execute(text("SELECT code FROM permissions WHERE domain='amenagement' ORDER BY code")).all()]
print(f"permissions = {total_perms}, roles = {total_roles}, grants = {total_grants}")
print("domaines :", ", ".join(f"{d}={n}" for d, n in domaines))
print(f"codes amenagement = {len(amen)}")

from app.core.permissions import has_perm  # noqa: E402

for nom in ("CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT", "AUDITEUR",
            "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER"):
    rid = db.execute(text(f"SELECT id FROM roles WHERE name='{nom}'")).scalar()
    codes = [r[0] for r in db.execute(text(
        "SELECT p.code FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id "
        f"WHERE rp.role_id={rid}")).all()]
    user = type("U", (), {"id": 1, "company_id": None, "role": nom, "level": 2,
                          "permissions": codes})()
    tests = {
        "place.read": has_perm(user, "amenagement.place.read"),
        "place.create": has_perm(user, "amenagement.place.create"),
        "place.modify": has_perm(user, "amenagement.place.modify"),
    }
    print(f"{nom:28} liens_amenagement={len([c for c in codes if c.startswith('amenagement.')]):3} {tests}")

db.close()
print(f"\nbase vierge : {db_file}")
