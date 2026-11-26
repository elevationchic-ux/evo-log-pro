"""036 ajout Peremption.numero_serie (suivi serie par lot)

Revision ID: 036_add_peremption_numero_serie
Revises: 035_rbac_acconage_grants
Create Date: 2026-10-03

La classe ORM ``Peremption``, le schema ``PeremptionCreate`` et le routeur
``POST /magasin-avance/peremptions`` reference tous un champ ``numero_serie``
(suivi serie/serial d'un lot), mais la colonne n'avait JAMAIS ete creee en base.
Resultat : ``Peremption(numero_serie=...)`` levait un TypeError a la moindre
inscription de peremption -- endpoint 500 systematique, jamais couvert par un
test passant.

Correction additive et idempotente : colonne nullable String(100) (un lot peut
avoir une serie ou non). Nullable -> aucune donnee inventee pour les lignes
existantes. Garde d'existence par ``sa.inspect`` ; drop en mode batch (SQLite ne
supporte pas ALTER ... DROP COLUMN nativement).
"""
from alembic import op
import sqlalchemy as sa


revision = "036_add_peremption_numero_serie"
down_revision = "036_rbac_qhse_grants"
branch_labels = None
depends_on = None


def _peremption_columns():
    inspector = sa.inspect(op.get_bind())
    if "peremptions" not in set(inspector.get_table_names()):
        return set()
    return {c["name"] for c in inspector.get_columns("peremptions")}


def upgrade():
    cols = _peremption_columns()
    if "numero_serie" not in cols:
        op.add_column(
            "peremptions",
            sa.Column("numero_serie", sa.String(length=100), nullable=True),
        )


def downgrade():
    cols = _peremption_columns()
    if "numero_serie" in cols:
        with op.batch_alter_table("peremptions") as batch_op:
            batch_op.drop_column("numero_serie")
