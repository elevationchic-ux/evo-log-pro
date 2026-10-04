"""Controle rapide du departement amenagement portuaire apres renommage DTO.

Verifie : import des modeles + mappers, parite require_perm/catalogue, routes
OpenAPI sous le prefixe, colonnes reelles de la table de programmation.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evo-log-backend"))

from sqlalchemy.orm import configure_mappers

from app.core.permission_catalog import ROLE_GRANTS, iter_permission_rows
from app.models.amenagement_portuaire import DocumentProgrammation

configure_mappers()
print("table :", DocumentProgrammation.__tablename__)
print("colonnes :", sorted(c.name for c in DocumentProgrammation.__table__.columns))

codes_catalogue = {r[0] for r in iter_permission_rows()}
amgt = sorted(c for c in codes_catalogue if c.startswith("amenagement."))
print("codes amenagement au catalogue :", len(amgt))
print("sous-modules :", sorted({c.split(".")[1] for c in amgt}))

src = (ROOT / "evo-log-backend" / "app" / "routers" / "v1" / "amenagement_portuaire.py").read_text(encoding="utf-8")
utilises = sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))
print("codes utilises par le routeur :", len(utilises))
fantomes = [c for c in utilises if c not in codes_catalogue]
print("codes inconnus du catalogue :", fantomes)

# Porte des droits : chaque code du routeur doit etre couvert par >= 1 role
from app.core.permissions import has_perm

orphelins = [
    c for c in utilises
    if not any(has_perm(codes, c) for _n, _l, _d, codes in ROLE_GRANTS)
]
print("codes sans role porteur :", orphelins)

from app.main import app

paths = app.openapi()["paths"]
prefix = "/api/v1/amenagement-portuaire"
choix = sorted(p for p in paths if p.startswith(prefix))
print("routes openapi :", len(choix))
for p in choix:
    if "programmation" in p:
        print("  ", p, sorted(paths[p].keys()))
