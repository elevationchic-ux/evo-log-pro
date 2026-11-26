"""111 : table immobilisations (registre amortissable OHADA).

Revision ID: 111_immobilisations
Revises: 110_notes_annexes
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "111_immobilisations"
down_revision = "110_notes_annexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "immobilisations" in set(sa.inspect(bind).get_table_names()):
        return
    op.create_table(
        "immobilisations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("numero_immobilisation", sa.String(length=50), nullable=False),
        sa.Column("designation", sa.String(length=300), nullable=False),
        sa.Column("date_acquisition", sa.Date(), nullable=False),
        sa.Column("valeur_acquisition", sa.Numeric(15, 2), nullable=False),
        sa.Column("valeur_residuelle", sa.Numeric(15, 2), nullable=True),
        sa.Column("duree_mois", sa.Integer(), nullable=False),
        sa.Column("compte_immobilisation", sa.String(length=20), nullable=False),
        sa.Column("compte_amortissement", sa.String(length=20), nullable=False),
        sa.Column("compte_dotation", sa.String(length=20), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_immobilisations_id", "immobilisations", ["id"])


def downgrade() -> None:
    op.drop_table("immobilisations")
