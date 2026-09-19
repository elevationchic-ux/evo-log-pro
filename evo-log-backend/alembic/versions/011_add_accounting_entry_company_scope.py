"""add company scope to OHADA accounting entries

Revision ID: 011_add_accounting_entry_company_scope
Revises: 010_add_vehicle_company_scope
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa


revision = "011_add_accounting_entry_company_scope"
down_revision = "010_add_vehicle_company_scope"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("ecritures_comptables_ohada", sa.Column("company_id", sa.Integer(), nullable=True))
    op.create_index("ix_ecritures_comptables_ohada_company_id", "ecritures_comptables_ohada", ["company_id"], unique=False)
    op.create_foreign_key(
        "fk_ecritures_comptables_ohada_company_id",
        "ecritures_comptables_ohada",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_ecritures_comptables_ohada_company_id", "ecritures_comptables_ohada", type_="foreignkey")
    op.drop_index("ix_ecritures_comptables_ohada_company_id", table_name="ecritures_comptables_ohada")
    op.drop_column("ecritures_comptables_ohada", "company_id")
