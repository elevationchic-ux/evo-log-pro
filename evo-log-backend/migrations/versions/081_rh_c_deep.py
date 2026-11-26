"""081 : tables expansion rh-personnel (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "081_rh_c_deep"
down_revision = "080_finance_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "rhc_training_plans",
    "rhc_disciplinary_records",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("rhc_training_plans"):
        op.create_table(
            "rhc_training_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("organisme", sa.String(200), nullable=True),
            sa.Column("heures_financees", sa.Integer, nullable=True),
            sa.Column("heures_realisees", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rhc_training_plans_uniq"),
        )

    if not _has("rhc_disciplinary_records"):
        op.create_table(
            "rhc_disciplinary_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("type_sanction", sa.String(200), nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("date_effet", sa.Date, nullable=True),
            sa.Column("date_fin_effet", sa.Date, nullable=True),
            sa.Column("decideur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rhc_disciplinary_records_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
