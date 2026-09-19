"""add company scope to fuel tank sensors

Revision ID: 012_add_fuel_sensor_company_scope
Revises: 011_add_accounting_entry_company_scope
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa


revision = "012_add_fuel_sensor_company_scope"
down_revision = "011_add_accounting_entry_company_scope"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fuel_tank_sensors", sa.Column("company_id", sa.Integer(), nullable=True))
    op.create_index("ix_fuel_tank_sensors_company_id", "fuel_tank_sensors", ["company_id"], unique=False)
    op.create_foreign_key(
        "fk_fuel_tank_sensors_company_id",
        "fuel_tank_sensors",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_fuel_tank_sensors_company_id", "fuel_tank_sensors", type_="foreignkey")
    op.drop_index("ix_fuel_tank_sensors_company_id", table_name="fuel_tank_sensors")
    op.drop_column("fuel_tank_sensors", "company_id")
