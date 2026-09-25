"""023 Tracabilite du tarif CEMAC (colonnes de provenance).

Revision ID: 023_add_tarif_cemac_provenance
Revises: 022_add_sequences_numerotation
Create Date: 2026-09-25

Contexte : la table ``nomenclature_cemac`` (creee par la revision de parite
014) porte les taux par position SH que le moteur UNIQUE de liquidation
(app/services/taxation_douaniere.py) consomme. Mais rien ne tracait D'OU vient
un taux. Conformement a la politique "aucune donnee inventee", on ajoute :

    date_fin_effet     fin de validite du taux (le tarif CEMAC evolue)
    source_reference   reference officielle (arrete, fichier DGD/CAMCIS, lot
                       d'import, ou "saisie manuelle <agent>")

Colonnes NULLables et ajout IDEMPOTENT (garde par inspection des colonnes) :
aucune valeur n'est ecrite ici, seul l'espace de provenance est prepare. Les
taux reels sont charges par scripts/import_tarif_cemac.py depuis un fichier
OFFICIEL fourni -- jamais inventes.
"""
from alembic import op
import sqlalchemy as sa


revision = "023_add_tarif_cemac_provenance"
down_revision = "022_add_sequences_numerotation"
branch_labels = None
depends_on = None


TABLE = "nomenclature_cemac"
NEW_COLUMNS = {
    "date_fin_effet": sa.Date(),
    "source_reference": sa.String(length=200),
}


def _existing_columns(bind):
    insp = sa.inspect(bind)
    if TABLE not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(TABLE)}


def upgrade():
    bind = op.get_bind()
    have = _existing_columns(bind)
    if not have and TABLE not in set(sa.inspect(bind).get_table_names()):
        # Table absente (base vierge) : la revision 014 la creera depuis l'ORM
        # (qui contient deja les nouvelles colonnes). Rien a ajouter.
        return
    for name, column_type in NEW_COLUMNS.items():
        if name in have:
            continue
        op.add_column(TABLE, sa.Column(name, column_type, nullable=True))


def downgrade():
    bind = op.get_bind()
    if TABLE not in set(sa.inspect(bind).get_table_names()):
        return
    have = _existing_columns(bind)
    # SQLite : drop column via batch mode.
    with op.batch_alter_table(TABLE) as batch_op:
        for name in NEW_COLUMNS:
            if name in have:
                batch_op.drop_column(name)
