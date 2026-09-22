"""Add tenant scope to B2B quotes.

Revision ID: 20260919_add_quote_company_scope
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20260919_add_quote_company_scope"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cotations_devis",
        sa.Column("company_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_cotations_devis_company_id",
        "cotations_devis",
        ["company_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_cotations_devis_company_id",
        "cotations_devis",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_cotations_devis_company_id",
        "cotations_devis",
        type_="foreignkey",
    )
    op.drop_index("ix_cotations_devis_company_id", table_name="cotations_devis")
    op.drop_column("cotations_devis", "company_id")
