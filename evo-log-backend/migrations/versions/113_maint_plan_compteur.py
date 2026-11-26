"""113 : colonnes de suivi compteur sur maint_maintenance_plans.

Le moteur de planification preventive compare le dernier releve technique
(heures moteur, km, cycles) a une baseline par plan : sans ces colonnes,
aucun declenchement a compteur n'est possible sans faux positifs.

Revision ID: 113_maint_plan_compteur
Revises: 112_liasses_fiscales
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "113_maint_plan_compteur"
down_revision = "112_liasses_fiscales"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    colonnes = {c["name"] for c in sa.inspect(bind).get_columns("maint_maintenance_plans")}
    if "dernier_releve_compteur" not in colonnes:
        op.add_column(
            "maint_maintenance_plans",
            sa.Column("dernier_releve_compteur", sa.Float(), nullable=True))
    if "dernier_releve_date" not in colonnes:
        op.add_column(
            "maint_maintenance_plans",
            sa.Column("dernier_releve_date", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("maint_maintenance_plans", "dernier_releve_date")
    op.drop_column("maint_maintenance_plans", "dernier_releve_compteur")
