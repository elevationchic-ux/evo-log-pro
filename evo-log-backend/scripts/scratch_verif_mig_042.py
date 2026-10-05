"""Controle de la montee 042 sur la base de developpement.

Verifie trois choses que le module promet :
  1. la base est bien a 042 ;
  2. les trois codes `amenagement.place.*` existent, declares sur le domaine
     `amenagement_portuaire` (pas une permission orpheline sans module) ;
  3. les liens role x code correspondent au catalogue, wildcards compris.

Aucune donnee metier n'est verifiee ni inseree : ports_cameroun doit rester
vide tant que les agents n'ont pas saisi leurs arretes.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.permission_catalog import ROLE_GRANTS  # noqa: E402
from app.core.permissions import has_perm  # noqa: E402

DB = Path(__file__).resolve().parents[1] / "kamlog_erp.db"
PLACE = ("amenagement.place.read", "amenagement.place.create", "amenagement.place.modify")
ROLES = ("CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT", "AUDITEUR",
         "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER")

conn = sqlite3.connect(DB)
try:
    version = [r[0] for r in conn.execute("SELECT version_num FROM alembic_version")]
    print(f"alembic : {version}")

    lignes = {r[0]: r[1:] for r in conn.execute(
        "SELECT code, domaine, module, sub_module, action FROM permissions "
        "WHERE code LIKE 'amenagement.place.%'")}
    for code in PLACE:
        print(f"{code:26} -> {lignes.get(code, 'ABSENT')}")

    roles = dict(conn.execute("SELECT name, id FROM roles"))
    for nom in ROLES:
        if nom not in roles:
            print(f"{nom}: role ABSENT")
            continue
        liens = {
            r[0] for r in conn.execute(
                "SELECT p.code FROM role_permissions rp JOIN permissions p ON p.id = rp.permission_id "
                "WHERE rp.role_id = ? AND p.code LIKE 'amenagement.%'", (roles[nom],))
        }
        codes_role = [c for n, _l, _d, cs in ROLE_GRANTS if n == nom for c in cs]
        attendu = {c for c in PLACE if has_perm(codes_role, c)}
        # Les liens reels de la base sont rejoues par le VRAI moteur : un lien
        # wildcard (amenagement.*.* ou amenagement.*.read) ne porte que ce qu'il
        # dit, et c'est has_perm qui le decide, pas une regle approximative ici.
        porte = {c for c in PLACE if has_perm(sorted(liens), c)}
        etat = "OK" if porte == attendu else "DIVERGENCE"
        print(f"{nom:28} base={sorted(porte)} catalogue={sorted(attendu)} {etat}"
              + ("" if etat == "OK" else f"  ecart={sorted(porte ^ attendu)}"))

    n_ports = conn.execute("SELECT COUNT(*) FROM ports_cameroun").fetchone()[0]
    print(f"ports_cameroun : {n_ports} ligne(s) — doit rester 0 tant que rien n'est saisi")
finally:
    conn.close()
