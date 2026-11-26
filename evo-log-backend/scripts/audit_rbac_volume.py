"""Migre une base VIERGE jusqu'a head et compte le RBAC reellement seme.

Deux usages :
  1. prouver que la chaine complete (001 -> head) s'applique encore sur une base
     neuve, ce que les tests unitaires ne verifient que partiellement ;
  2. rendre les chiffres cites dans docs/RBAC_ACCREDITATIONS.md (permissions,
     roles, grants, lignes par domaine) au lieu d'un herite jamais revu.

Le script ne ecrit rien dans la base de developpement : il cree une base
temporaire, c'est tout l'interet du titre « vierge ».
"""
import os
import pathlib
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

RACINE = pathlib.Path(__file__).resolve().parents[1]
db_file = pathlib.Path(tempfile.mkdtemp()) / "vierge_rbactail.db"
url = f"sqlite:///{db_file.as_posix()}"
os.environ["DATABASE_URL"] = url

cfg = Config(str(RACINE / "alembic.ini"))
cfg.set_main_option("script_location", str(RACINE / "migrations"))
command.upgrade(cfg, "head")

db = sessionmaker(bind=create_engine(url))()


def scal(q):
    return db.execute(text(q)).scalar()


colonnes = [r[0] for r in db.execute(text("PRAGMA table_info(permissions)")).all()]
print("colonnes permissions :", colonnes)

total_perms = scal("SELECT COUNT(*) FROM permissions")
total_roles = scal("SELECT COUNT(*) FROM roles")
total_grants = scal("SELECT COUNT(*) FROM role_permissions")
print(f"permissions = {total_perms}, roles = {total_roles}, grants = {total_grants}")

# Le domaine se déduit du préfixe du code (aucune colonne `domain` n'est garantie).
domaines = db.execute(text(
    "SELECT substr(code, 1, instr(code, '.') - 1) AS d, COUNT(*) FROM permissions "
    "GROUP BY d ORDER BY COUNT(*) DESC")).all()
print("domaines :", ", ".join(f"{d}={n}" for d, n in domaines))

amen = [r[0] for r in db.execute(text(
    "SELECT code FROM permissions WHERE code LIKE 'amenagement.%' ORDER BY code")).all()]
print(f"codes amenagement = {len(amen)}")
places = [c for c in amen if c.split(".")[1] == "place"]
print("place :", places)

from app.core.permissions import has_perm  # noqa: E402

for nom in ("CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT", "AUDITEUR",
            "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER"):
    rid = scal(f"SELECT id FROM roles WHERE name='{nom}'")
    codes = [r[0] for r in db.execute(text(
        "SELECT p.code FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id "
        f"WHERE rp.role_id={rid}")).all()]
    rendu = {
        a: bool(has_perm(codes, f"amenagement.place.{a}")) for a in ("read", "create", "modify")
    }
    liens = len([c for c in codes if c.startswith("amenagement.")])
    print(f"{nom:28} liens_amenagement={liens:3} place={rendu}")

db.close()
