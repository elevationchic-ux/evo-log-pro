"""112 : table liasses_fiscales (consolide TVA + IS CEMAC).

Revision ID: 112_liasses_fiscales
Revises: 111_immobilisations
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "112_liasses_fiscales"
down_revision = "111_immobilisations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "liasses_fiscales" in set(sa.inspect(bind).get_table_names()):
        return
    op.create_table(
        "liasses_fiscales",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column("exercice_id", sa.Integer(), nullable=True),
        sa.Column("date_generation", sa.Date(), nullable=False),
        sa.Column("total_tva_collectee", sa.Numeric(15, 2), nullable=True),
        sa.Column("total_tva_deductible", sa.Numeric(15, 2), nullable=True),
        sa.Column("total_tva_a_payer", sa.Numeric(15, 2), nullable=True),
        sa.Column("total_is", sa.Numeric(15, 2), nullable=True),
        sa.Column("total_impots", sa.Numeric(15, 2), nullable=True),
        sa.Column("nombre_declarations_tva", sa.Integer(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=True),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("valide_par", sa.String(length=100), nullable=True),
        sa.Column("date_validation", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["exercice_id"], ["exercices_comptables.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_liasses_fiscales_id", "liasses_fiscales", ["id"])
    op.create_index("ix_liasses_fiscales_annee", "liasses_fiscales", ["annee"])


def downgrade() -> None:
    op.drop_table("liasses_fiscales")
