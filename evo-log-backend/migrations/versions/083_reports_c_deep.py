"""083 : tables expansion reports-bi (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "083_reports_c_deep"
down_revision = "082_b2b_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "rptc_scheduled_reports",
    "rptc_templates",
    "rptc_data_exports",
    "rptc_ad_hoc_queries",
    "rptc_olap_cubes",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("rptc_scheduled_reports"):
        op.create_table(
            "rptc_scheduled_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("frequence", sa.String(200), nullable=True),
            sa.Column("format", sa.String(200), nullable=True),
            sa.Column("destinataires", sa.String(200), nullable=True),
            sa.Column("prochaine_execution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rptc_scheduled_reports_uniq"),
        )

    if not _has("rptc_templates"):
        op.create_table(
            "rptc_templates",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("source_donnees", sa.String(200), nullable=True),
            sa.Column("version", sa.String(200), nullable=True),
            sa.Column("nb_blocs", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rptc_templates_uniq"),
        )

    if not _has("rptc_data_exports"):
        op.create_table(
            "rptc_data_exports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("format", sa.String(200), nullable=True),
            sa.Column("filtres", sa.Text, nullable=True),
            sa.Column("lignes_exportees", sa.Integer, nullable=True),
            sa.Column("demandeur", sa.String(200), nullable=True),
            sa.Column("date_export", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rptc_data_exports_uniq"),
        )

    if not _has("rptc_ad_hoc_queries"):
        op.create_table(
            "rptc_ad_hoc_queries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("source_donnees", sa.String(200), nullable=True),
            sa.Column("dimensions", sa.Text, nullable=True),
            sa.Column("auteur", sa.String(200), nullable=True),
            sa.Column("derniere_execution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("partage", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rptc_ad_hoc_queries_uniq"),
        )

    if not _has("rptc_olap_cubes"):
        op.create_table(
            "rptc_olap_cubes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("dimensions", sa.Text, nullable=True),
            sa.Column("mesures", sa.Text, nullable=True),
            sa.Column("nb_lignes", sa.Integer, nullable=True),
            sa.Column("date_dernier_refresh", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rptc_olap_cubes_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
