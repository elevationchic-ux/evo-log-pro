"""078 : tables expansion dashboard (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "078_dashboard_b_deep"
down_revision = "077_magasin_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "dashb_operational_kpis",
    "dashb_scorecards",
    "dashb_alert_rules",
    "dashb_refresh_jobs",
    "dashb_saved_views",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("dashb_operational_kpis"):
        op.create_table(
            "dashb_operational_kpis",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("periode", sa.Date, nullable=True),
            sa.Column("objectif", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dashb_operational_kpis_uniq"),
        )

    if not _has("dashb_scorecards"):
        op.create_table(
            "dashb_scorecards",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("direction", sa.String(200), nullable=True),
            sa.Column("periode", sa.Date, nullable=True),
            sa.Column("score_global", sa.Numeric, nullable=True),
            sa.Column("nb_indicateurs", sa.Integer, nullable=True),
            sa.Column("tendance", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dashb_scorecards_uniq"),
        )

    if not _has("dashb_alert_rules"):
        op.create_table(
            "dashb_alert_rules",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("indicateur", sa.String(200), nullable=True),
            sa.Column("condition", sa.String(200), nullable=True),
            sa.Column("seuil", sa.Numeric, nullable=True),
            sa.Column("destinataires", sa.String(200), nullable=True),
            sa.Column("canal", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dashb_alert_rules_uniq"),
        )

    if not _has("dashb_refresh_jobs"):
        op.create_table(
            "dashb_refresh_jobs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("frequence", sa.String(200), nullable=True),
            sa.Column("derniere_execution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_sec", sa.Integer, nullable=True),
            sa.Column("lignes_traitees", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dashb_refresh_jobs_uniq"),
        )

    if not _has("dashb_saved_views"):
        op.create_table(
            "dashb_saved_views",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("owner", sa.String(200), nullable=True),
            sa.Column("type_visuel", sa.String(200), nullable=True),
            sa.Column("filtres", sa.Text, nullable=True),
            sa.Column("partage", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dashb_saved_views_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
