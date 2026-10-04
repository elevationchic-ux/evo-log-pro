"""Genere la migration 038 (tables du departement Amenagement portuaire).

La parite stricte avec l'ORM etant une convention du projet (migrations
014/028), le DDL est produit a partir du metadata SQLAlchemy plutot que
frappe a la main : types, nullabilite, index, cles uniques et noms de
contraintes FK sont releves tels que l'application les declare.

Sortie : evo-log-backend/migrations/versions/038_add_amenagement_portuaire.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evo-log-backend"))

import app.models.port_cameroun  # noqa: F401  (referentiel des cibles de FK)
import app.models.amenagement_portuaire as ap  # noqa: E402
import sqlalchemy as sa  # noqa: E402
from sqlalchemy.orm import configure_mappers  # noqa: E402

configure_mappers()

TABLES = [
    ap.SchemaDirecteur, ap.ProjetAmenagement, ap.DocumentProgrammation,
    ap.MarcheAmenagement, ap.AutorisationDomaniale, ap.ConcessionPortuaire,
    ap.InfrastructurePortuaire, ap.Dragage, ap.AutorisationTravaux,
]

# Nom de constante courte et legible dans la migration generee.
CONSTS = {
    "SchemaDirecteur": "SCHEMA_DIRECTEUR",
    "ProjetAmenagement": "PROJET",
    "DocumentProgrammation": "PROGRAMMATION",
    "MarcheAmenagement": "MARCHE",
    "AutorisationDomaniale": "TITRE",
    "ConcessionPortuaire": "CONCESSION",
    "InfrastructurePortuaire": "INFRASTRUCTURE",
    "Dragage": "DRAGAGE",
    "AutorisationTravaux": "AUTORISATION",
}

HEADER = '''"""038 : departement Amenagement portuaire (Douala, Kribi, Limbe).

Le module tient le registre de la maitrise d\'ouvrage du domaine portuaire,
aligne sur le circuit camerounais reel :

    schemas_directeurs_amgt      schemas / plans directeurs (APN, autorite portuaire)
    projets_amenagement          operations d\'investissement programmees
    documents_programmation_amgt fiche technique, visa de maturite (decret
                                 2018/0492), PIP/CDMT, visas d\'engagement
    marches_amenagement          marches publics (COLIFE/CIP) et contrats PPP (loi 2023/008)
    autorisations_domaniales_amgt titres d\'occupation du domaine portuaire
    concessions_amenagement      affermage, concession, BOT/CET, AOT
    infrastructures_amenagees    inventaire technique des ouvrages livres
    campagnes_dragage            dragages de construction et d\'entretien
    autorisations_travaux_amgt   EIES, permis, visas administratifs (loi 96/012)

AUCUNE DONNEE N\'EST INSEREE : ces tables decrivent le domaine public, dont le
contenu appartient aux documents officiels. Un champ NULL veut dire « non
renseigne », et la migration 039 ne seed que des droits RBAC.

Colonnes nomenclature : l\'ORM declare des enums Python en VARCHAR (sans type
natif ni CHECK, voir app/models/amenagement_portuaire._enum) — le DDL est donc
identique sur SQLite et PostgreSQL, et cette migration reproduit exactement les
memes types.

Proprietes (conventions 024/027/029/030/031/032/037) :
    - IDEMPOTENT par introspection : table deja presente -> no-op.
    - contraintes FK nommees, mode batch SQLite.
    - ajoute aussi les deux colonnes reclamees par GET /api/v1/public/ports
      (autorite_portuaire, tirant_eau_max) qui manquaient dans ports_cameroun :
      colonnees NULL, aucune valeur n\'est completee.
    - downgrade droppe les neuf tables et les deux colonnes.

Revision ID: 038_add_amenagement_portuaire
Revises: 037_add_customs_caution_register
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa


revision = "038_add_amenagement_portuaire"
down_revision = "037_add_customs_caution_register"
branch_labels = None
depends_on = None

# Ports du departement : colonnees mais JAMAIS remplies automatiquement.
T_PORTS = "ports_cameroun"
NEW_PORT_COLS = ("autorite_portuaire", "tirant_eau_max")
'''


def _sa_type(col):
    t = col.type
    # Text et Enum heritent de String : a tester AVANT, sinon le rendu perdrait
    # le type reel (TEXT) au profit d'un VARCHAR sans taille.
    if isinstance(t, sa.Text):
        return "sa.Text()"
    if isinstance(t, sa.String):
        return f"sa.String({t.length})" if t.length else "sa.String()"
    if isinstance(t, sa.Numeric):
        return f"sa.Numeric({t.precision}, {t.scale})"
    if isinstance(t, sa.Integer):
        return "sa.Integer()"
    if isinstance(t, sa.Boolean):
        return "sa.Boolean()"
    if isinstance(t, sa.Date):
        return "sa.Date()"
    if isinstance(t, sa.DateTime):
        return "sa.DateTime(timezone=True)"
    raise AssertionError(f"Type non pris en charge : {t!r} ({col.name})")


def _cols(table):
    out = []
    for col in table.columns:
        parts = [f'"{col.name}"', _sa_type(col)]
        if col.primary_key:
            parts.append("primary_key=True")
        else:
            parts.append("nullable=True" if col.nullable else "nullable=False")
        if col.unique and not col.index:
            parts.append("unique=True")
        # server_default : seul now() est rendu (les autres defauts de l'ORM
        # sont cote Python et n'ont rien a faire dans le DDL).
        if col.server_default is not None:
            arg = getattr(col.server_default, "arg", None)
            if isinstance(arg, sa.sql.functions.Function):
                parts.append("server_default=sa.func.now()")
        out.append("            sa.Column(" + ", ".join(parts) + "),")
    return out


def _fks(table):
    out = []
    for col in table.columns:
        for fk in col.foreign_keys:
            target = fk.target_fullname.split(".")
            out.append(
                f'            sa.ForeignKeyConstraint(["{col.name}"], '
                f'["{fk.target_fullname}"], name="fk_{table.name}_{col.name}_{target[0]}"),'
            )
    return out


def _indexes(table):
    out = []
    for col in table.columns:
        if not col.index:
            continue
        # index=True + unique=True : l'ORM genere un UNIQUE INDEX, pas une
        # contrainte distincte. Le nom ix_<table>_<col> reprend la convention
        # SQLAlchemy (et celle des migrations 024/028 deja en base).
        suffix = ", unique=True" if col.unique else ""
        out.append(
            f'        op.create_index("ix_{table.name}_{col.name}", '
            f'"{table.name}", ["{col.name}"]{suffix})'
        )
    return out


blocs = []
for cls in TABLES:
    t = cls.__table__
    const = "T_" + CONSTS[cls.__name__]
    body = "\n".join(_cols(t) + _fks(t))
    idx = "\n".join(_indexes(t))
    blocs.append(
        f'\n    if {const} not in tables:\n'
        f"        op.create_table(\n            {const},\n{body}\n        )\n{idx}"
    )

consts = "\n".join(f'T_{CONSTS[c.__name__]} = "{c.__tablename__}"' for c in TABLES)

port_cols = '''
    # ── ports_cameroun : colonnes attendues par GET /api/v1/public/ports ──────
    if T_PORTS in tables:
        cols = {c["name"] for c in sa.inspect(bind).get_columns(T_PORTS)}
        if "autorite_portuaire" not in cols:
            op.add_column(T_PORTS, sa.Column("autorite_portuaire", sa.String(160), nullable=True))
        if "tirant_eau_max" not in cols:
            op.add_column(T_PORTS, sa.Column("tirant_eau_max", sa.Numeric(6, 2), nullable=True))
'''

downgrade = "\n".join(
    f'    if T_{CONSTS[c.__name__]} in tables:\n'
    f'        op.drop_table(T_{CONSTS[c.__name__]})'
    for c in reversed(TABLES)
)

script = (
    f'{HEADER}\n{consts}\n\n\ndef upgrade():\n'
    '    bind = op.get_bind()\n    insp = sa.inspect(bind)\n'
    '    tables = set(insp.get_table_names())\n'
)
script += "\n".join(blocs)
script += port_cols
script += (
    '\n\ndef downgrade():\n    bind = op.get_bind()\n'
    '    insp = sa.inspect(bind)\n'
    '    tables = set(insp.get_table_names())\n'
)
script += '    if T_PORTS in tables:\n        cols = {c["name"] for c in insp.get_columns(T_PORTS)}\n'
script += '        with op.batch_alter_table(T_PORTS) as batch:\n'
script += '            if "tirant_eau_max" in cols:\n                batch.drop_column("tirant_eau_max")\n'
script += '            if "autorite_portuaire" in cols:\n                batch.drop_column("autorite_portuaire")\n'
script += downgrade + "\n"

out = ROOT / "evo-log-backend" / "migrations" / "versions" / "038_add_amenagement_portuaire.py"
out.write_text(script, encoding="utf-8")
print("ecrit :", out)
print("lignes :", script.count(chr(10)) + 1)
