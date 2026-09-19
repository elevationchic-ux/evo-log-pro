"""add company scope to vehicles

Revision ID: 010_add_vehicle_company_scope
Revises: 009_add_transport_avance_complete
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa


revision = "010_add_vehicle_company_scope"
down_revision = "009_add_transport_avance_complete"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vehicules", sa.Column("company_id", sa.Integer(), nullable=True))
    op.create_index("ix_vehicules_company_id", "vehicules", ["company_id"], unique=False)
    op.create_foreign_key(
        "fk_vehicules_company_id",
        "vehicules",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_vehicules_company_id", "vehicules", type_="foreignkey")
    op.drop_index("ix_vehicules_company_id", table_name="vehicules")
    op.drop_column("vehicules", "company_id")
