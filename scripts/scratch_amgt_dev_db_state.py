"""Verifie l'etat reel de la base de developpement apres 038 + 039.

Controle : presence des 9 tables du departement, des 2 colonnes ajoutees a
ports_cameroun, des 50 codes amenagement en table, et des liens RBAC des roles
porteurs. Aucune donnee metier ne doit avoir ete inseree par la migration.
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.getcwd())  # lance depuis evo-log-backend

from app.models.amenagement_portuaire import (
    SchemaDirecteur, ProjetAmenagement, DocumentProgrammation, MarcheAmenagement,
    AutorisationDomaniale, ConcessionPortuaire, InfrastructurePortuaire,
    Dragage, AutorisationTravaux,
)

DB = "kamlog_erp.db"

# Noms tires du modele (source de verite), jamais reecrits ici.
TABLES = [c.__tablename__ for c in (
    SchemaDirecteur, ProjetAmenagement, DocumentProgrammation, MarcheAmenagement,
    AutorisationDomaniale, ConcessionPortuaire, InfrastructurePortuaire,
    Dragage, AutorisationTravaux,
)]

ROLES = [
    "CHEF_AMENAGEMENT_PORTUAIRE", "INGENIEUR_AMENAGEMENT", "AUDITEUR",
    "CHEF_EXPLOITATION", "DIRECTEUR_FINANCIER",
]

con = sqlite3.connect(DB)
cur = con.cursor()

exists = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
print("version alembic :", cur.execute("SELECT version_num FROM alembic_version").fetchall())

print("\n-- tables du departement --")
for t in TABLES:
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] if t in exists else None
    print(f"  {t:34s} presente={t in exists} lignes={n}")

print("\n-- colonnes ports_cameroun --")
cols = {r[1] for r in cur.execute("PRAGMA table_info(ports_cameroun)")}
for c in ("autorite_portuaire", "tirant_eau_max"):
    print(f"  {c:20s} {c in cols}")

print("\n-- codes amenagement en table --")
n_codes = cur.execute(
    "SELECT COUNT(*) FROM permissions WHERE code LIKE 'amenagement.%'").fetchone()[0]
n_sap = cur.execute(
    "SELECT COUNT(*) FROM permissions WHERE code LIKE 'amenagement.%' AND code LIKE '%*%'"
).fetchone()[0]
print(f"  total={n_codes} (dont wildcards={n_sap})")

print("\n-- roles porteurs --")
for r in ROLES:
    row = cur.execute(
        "SELECT id, level, is_system, modules_allowed FROM roles WHERE name = ?", (r,)
    ).fetchone()
    if not row:
        print(f"  {r:26s} ABSENT")
        continue
    rid, level, is_system, mods = row
    liens = cur.execute(
        "SELECT COUNT(*) FROM role_permissions WHERE role_id = ?", (rid,)
    ).fetchone()[0]
    amgt = cur.execute(
        "SELECT COUNT(*) FROM role_permissions rp JOIN permissions p ON p.id = rp.permission_id "
        "WHERE rp.role_id = ? AND p.code LIKE 'amenagement.%'", (rid,)
    ).fetchone()[0]
    try:
        mods_lues = json.loads(mods or "[]")
    except (TypeError, ValueError):
        mods_lues = mods  # role plus ancien, format different : affiche tel quel
    print(f"  {r:26s} level={level} system={bool(is_system)} liens={liens} "
          f"liens_amenagement={amgt} modules={mods_lues}")

print("\n-- aucune donnee metier injectee --")
for t in TABLES:
    if t in exists:
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert n == 0, f"{t} contient {n} ligne(s) : la migration n'est pas supposee seeder"
print("  9 tables vides : OK")
con.close()
print("\nOK")
