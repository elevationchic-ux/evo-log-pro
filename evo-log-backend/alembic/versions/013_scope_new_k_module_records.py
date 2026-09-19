"""scope new K module records by company

Revision ID: 013_scope_new_k_module_records
Revises: 012_add_fuel_sensor_company_scope
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa


revision = "013_scope_new_k_module_records"
down_revision = "012_add_fuel_sensor_company_scope"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("cotations_devis", "electronic_pods", "procurement_purchase_orders", "compliance_audits"):
        column = "company_id"
        op.add_column(table, sa.Column(column, sa.Integer(), nullable=True))
        op.create_index(f"ix_{table}_{column}", table, [column], unique=False)
        op.create_foreign_key(f"fk_{table}_{column}", table, "companies", [column], ["id"])


def downgrade():
    for table in ("compliance_audits", "procurement_purchase_orders", "electronic_pods", "cotations_devis"):
        column = "company_id"
        op.drop_constraint(f"fk_{table}_{column}", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_{column}", table_name=table)
        op.drop_column(table, column)
