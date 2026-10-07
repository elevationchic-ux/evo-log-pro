"""061 : tables expansion amenagement-portuaire (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "061_amenagement_extra_deep"
down_revision = "060_dashboard_deep"
branch_labels = None
depends_on = None


TABLES = [
    "construction_progress",
    "infrastructure_maintenances",
    "isps_records",
    "port_perceptions",
    "annual_activity_reports",
    "sig_layers",
    "domain_archives",
    "amenagement_kpis",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("construction_progress"):
        op.create_table(
            "construction_progress",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("marche_id", sa.Integer, nullable=True),
            sa.Column("lot", sa.String(200), nullable=True),
            sa.Column("avancement_pct", sa.Numeric, nullable=True),
            sa.Column("date_releve", sa.Date, nullable=True),
            sa.Column("surface_m2", sa.Numeric, nullable=True),
            sa.Column("observateur", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_construction_progress_uniq"),
        )

    if not _has("infrastructure_maintenances"):
        op.create_table(
            "infrastructure_maintenances",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ouvrage_id", sa.Integer, nullable=True),
            sa.Column("type_intervention", sa.String(50), nullable=True),
            sa.Column("frequence_mois", sa.Integer, nullable=True),
            sa.Column("date_prochaine", sa.Date, nullable=True),
            sa.Column("cout_estime_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_infrastructure_maintenances_uniq"),
        )

    if not _has("isps_records"):
        op.create_table(
            "isps_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("niveau_isps", sa.String(50), nullable=True),
            sa.Column("date_application", sa.DateTime(timezone=True), nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("authorite_emetteuse", sa.String(200), nullable=True),
            sa.Column("date_levee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_isps_records_uniq"),
        )

    if not _has("port_perceptions"):
        op.create_table(
            "port_perceptions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_perception", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("type_perception", sa.String(50), nullable=True),
            sa.Column("base_calcul", sa.String(200), nullable=True),
            sa.Column("tarif_xaf", sa.Numeric, nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("arrete_reference", sa.String(200), nullable=True),
            sa.Column("date_application", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_perception", name="uix_port_perceptions_uniq"),
        )

    if not _has("annual_activity_reports"):
        op.create_table(
            "annual_activity_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("annee", sa.Integer, nullable=True),
            sa.Column("tonnage_traite_t", sa.Numeric, nullable=True),
            sa.Column("nb_escales", sa.Integer, nullable=True),
            sa.Column("nb_conteneurs_evp", sa.Integer, nullable=True),
            sa.Column("recettes_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_annual_activity_reports_uniq"),
        )

    if not _has("sig_layers"):
        op.create_table(
            "sig_layers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_couche", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("type_couche", sa.String(50), nullable=True),
            sa.Column("projection", sa.String(200), nullable=True),
            sa.Column("date_maj", sa.Date, nullable=True),
            sa.Column("superficie_ha", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_couche", name="uix_sig_layers_uniq"),
        )

    if not _has("domain_archives"):
        op.create_table(
            "domain_archives",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("cote_archive", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("type_piece", sa.String(50), nullable=True),
            sa.Column("periode_couverte", sa.String(200), nullable=True),
            sa.Column("localisation", sa.String(200), nullable=True),
            sa.Column("duree_conservation_an", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "cote_archive", name="uix_domain_archives_uniq"),
        )

    if not _has("amenagement_kpis"):
        op.create_table(
            "amenagement_kpis",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_kpi", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("objectif", sa.Numeric, nullable=True),
            sa.Column("ecart_pct", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_kpi", name="uix_amenagement_kpis_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
