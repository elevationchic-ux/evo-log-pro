"""057 : tables expansion reports-bi (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "057_reports_deep"
down_revision = "056_b2b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "warehouse_tables",
    "scorecards",
    "industry_benchmarks",
    "predictive_models",
    "custom_dashboards",
    "report_exports",
    "kpi_definitions",
    "drill_paths",
    "cohort_analyses",
    "anomaly_records",
    "regulatory_reports",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("warehouse_tables"):
        op.create_table(
            "warehouse_tables",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_table", sa.String(200), nullable=False, index=True),
            sa.Column("domaine", sa.String(200), nullable=True),
            sa.Column("frequence_refresh", sa.String(50), nullable=True),
            sa.Column("volume_lignes", sa.Integer, nullable=True),
            sa.Column("dernier_refresh", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_table", name="uix_warehouse_tables_uniq"),
        )

    if not _has("scorecards"):
        op.create_table(
            "scorecards",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("pole", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("nb_kpis", sa.Integer, nullable=True),
            sa.Column("score_global_pct", sa.Numeric, nullable=True),
            sa.Column("kpis_rouges", sa.Integer, nullable=True),
            sa.Column("kpis_oranges", sa.Integer, nullable=True),
            sa.Column("kpis_verts", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_scorecards_uniq"),
        )

    if not _has("industry_benchmarks"):
        op.create_table(
            "industry_benchmarks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("indicateur", sa.String(200), nullable=True),
            sa.Column("valeur_interne", sa.Numeric, nullable=True),
            sa.Column("valeur_benchmark", sa.Numeric, nullable=True),
            sa.Column("port_reference", sa.String(200), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("ecart_pct", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_industry_benchmarks_uniq"),
        )

    if not _has("predictive_models"):
        op.create_table(
            "predictive_models",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_modele", sa.String(200), nullable=True),
            sa.Column("type_modele", sa.String(50), nullable=True),
            sa.Column("variable_predite", sa.String(200), nullable=True),
            sa.Column("precision_pct", sa.Numeric, nullable=True),
            sa.Column("date_entrainement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_predictive_models_uniq"),
        )

    if not _has("custom_dashboards"):
        op.create_table(
            "custom_dashboards",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("proprietaire", sa.String(200), nullable=True),
            sa.Column("nb_widgets", sa.Integer, nullable=True),
            sa.Column("partage", sa.String(50), nullable=True),
            sa.Column("frequence", sa.String(50), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_custom_dashboards_uniq"),
        )

    if not _has("report_exports"):
        op.create_table(
            "report_exports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("rapport_source", sa.String(200), nullable=True),
            sa.Column("format", sa.String(50), nullable=True),
            sa.Column("frequence", sa.String(50), nullable=True),
            sa.Column("destinataires", sa.Text, nullable=True),
            sa.Column("dernier_envoi", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_report_exports_uniq"),
        )

    if not _has("kpi_definitions"):
        op.create_table(
            "kpi_definitions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_kpi", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("formule", sa.Text, nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("periodicite", sa.String(50), nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_kpi", name="uix_kpi_definitions_uniq"),
        )

    if not _has("drill_paths"):
        op.create_table(
            "drill_paths",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("niveau_1", sa.String(200), nullable=True),
            sa.Column("niveau_2", sa.String(200), nullable=True),
            sa.Column("niveau_3", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_drill_paths_uniq"),
        )

    if not _has("cohort_analyses"):
        op.create_table(
            "cohort_analyses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_cohorte", sa.String(200), nullable=True),
            sa.Column("criteres", sa.Text, nullable=True),
            sa.Column("taille", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("taux_retention_m1_pct", sa.Numeric, nullable=True),
            sa.Column("taux_retention_m12_pct", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cohort_analyses_uniq"),
        )

    if not _has("anomaly_records"):
        op.create_table(
            "anomaly_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("indicateur", sa.String(200), nullable=True),
            sa.Column("valeur_constatee", sa.Numeric, nullable=True),
            sa.Column("valeur_attendue", sa.Numeric, nullable=True),
            sa.Column("seuil_pct", sa.Numeric, nullable=True),
            sa.Column("date_detection", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_anomaly_records_uniq"),
        )

    if not _has("regulatory_reports"):
        op.create_table(
            "regulatory_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("autorite", sa.String(200), nullable=True),
            sa.Column("type_rapport", sa.String(50), nullable=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_regulatory_reports_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
