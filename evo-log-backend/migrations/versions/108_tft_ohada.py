"""108 : table tft (Tableau des Flux de Tresorerie OHADA).

Revision ID: 108_tft_ohada
Revises: 107_rbac_wave6_grants
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "108_tft_ohada"
down_revision = "107_rbac_wave6_grants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    if "tft" in existing:
        return
    op.create_table(
        "tft",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercice_id", sa.Integer(), nullable=False),
        sa.Column("date_tft", sa.Date(), nullable=False),
        sa.Column("capacite_autofinancement", sa.Numeric(15, 2), nullable=True),
        sa.Column("variation_bfr_exploitation", sa.Numeric(15, 2), nullable=True),
        sa.Column("flux_exploitation", sa.Numeric(15, 2), nullable=True),
        sa.Column("cessions_immobilisations", sa.Numeric(15, 2), nullable=True),
        sa.Column("acquisitions_immobilisations", sa.Numeric(15, 2), nullable=True),
        sa.Column("flux_investissement", sa.Numeric(15, 2), nullable=True),
        sa.Column("augmentation_capital", sa.Numeric(15, 2), nullable=True),
        sa.Column("nouveaux_emprunts", sa.Numeric(15, 2), nullable=True),
        sa.Column("remboursements_emprunts", sa.Numeric(15, 2), nullable=True),
        sa.Column("dividendes_verses", sa.Numeric(15, 2), nullable=True),
        sa.Column("flux_financement", sa.Numeric(15, 2), nullable=True),
        sa.Column("variation_tresorerie", sa.Numeric(15, 2), nullable=True),
        sa.Column("tresorerie_debut", sa.Numeric(15, 2), nullable=True),
        sa.Column("tresorerie_fin", sa.Numeric(15, 2), nullable=True),
        sa.Column("devise", sa.String(length=3), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("valide_par", sa.String(length=100), nullable=True),
        sa.Column("date_validation", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["exercice_id"], ["exercices_comptables.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tft_id", "tft", ["id"])


def downgrade() -> None:
    op.drop_table("tft")
