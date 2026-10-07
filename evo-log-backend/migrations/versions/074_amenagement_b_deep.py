"""074 : tables expansion amenagement-portuaire (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "074_amenagement_b_deep"
down_revision = "073_port_ops_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "amgtb_dredging_projects",
    "amgtb_concession_plots",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("amgtb_dredging_projects"):
        op.create_table(
            "amgtb_dredging_projects",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("objectif_tirant_eau_m", sa.Integer, nullable=True),
            sa.Column("volume_a_draguer_m3", sa.Integer, nullable=True),
            sa.Column("volume_rejete_m3", sa.Integer, nullable=True),
            sa.Column("entreprise", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_amgtb_dredging_projects_uniq"),
        )

    if not _has("amgtb_concession_plots"):
        op.create_table(
            "amgtb_concession_plots",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("superficie_m2", sa.Integer, nullable=True),
            sa.Column("concessionnaire", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("redevance_annuelle", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_amgtb_concession_plots_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
