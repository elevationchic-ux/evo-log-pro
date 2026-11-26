"""059 : tables expansion superadmin-cadc (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "059_superadmin_deep"
down_revision = "058_admin_deep"
branch_labels = None
depends_on = None


TABLES = [
    "platform_audits",
    "compliance_dashboards",
    "retention_policies",
    "platform_incidents",
    "access_reviews",
    "software_licenses",
    "technology_partners",
    "saas_revenue_records",
    "global_config_settings",
    "dr_plans",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("platform_audits"):
        op.create_table(
            "platform_audits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("nb_tenants_audites", sa.Integer, nullable=True),
            sa.Column("constats", sa.Text, nullable=True),
            sa.Column("recommandations", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_platform_audits_uniq"),
        )

    if not _has("compliance_dashboards"):
        op.create_table(
            "compliance_dashboards",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("domaine", sa.String(50), nullable=True),
            sa.Column("nb_tenants_conformes", sa.Integer, nullable=True),
            sa.Column("nb_tenants_hors", sa.Integer, nullable=True),
            sa.Column("score_global_pct", sa.Numeric, nullable=True),
            sa.Column("date_revue", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_compliance_dashboards_uniq"),
        )

    if not _has("retention_policies"):
        op.create_table(
            "retention_policies",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("categorie", sa.String(50), nullable=True),
            sa.Column("duree_conservation_jours", sa.Integer, nullable=True),
            sa.Column("methode_purge", sa.String(50), nullable=True),
            sa.Column("base_legale", sa.Text, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_retention_policies_uniq"),
        )

    if not _has("platform_incidents"):
        op.create_table(
            "platform_incidents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("priorite", sa.String(50), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_resolution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("impact_tenants", sa.Text, nullable=True),
            sa.Column("cause_racine", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_platform_incidents_uniq"),
        )

    if not _has("access_reviews"):
        op.create_table(
            "access_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("date_revue", sa.Date, nullable=True),
            sa.Column("nb_utilisateurs_revus", sa.Integer, nullable=True),
            sa.Column("nb_droits_retires", sa.Integer, nullable=True),
            sa.Column("revue_par", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_access_reviews_uniq"),
        )

    if not _has("software_licenses"):
        op.create_table(
            "software_licenses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("module", sa.String(200), nullable=True),
            sa.Column("editeur", sa.String(200), nullable=True),
            sa.Column("nb_sieges", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("cotisation_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_software_licenses_uniq"),
        )

    if not _has("technology_partners"):
        op.create_table(
            "technology_partners",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("type_partenaire", sa.String(50), nullable=True),
            sa.Column("produit_associe", sa.String(200), nullable=True),
            sa.Column("contrat", sa.Text, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_technology_partners_uniq"),
        )

    if not _has("saas_revenue_records"):
        op.create_table(
            "saas_revenue_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("mois", sa.String(200), nullable=True),
            sa.Column("mrr_xaf", sa.Numeric, nullable=True),
            sa.Column("churn_mrr_xaf", sa.Numeric, nullable=True),
            sa.Column("expansion_mrr_xaf", sa.Numeric, nullable=True),
            sa.Column("arpu_xaf", sa.Numeric, nullable=True),
            sa.Column("nb_customers", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_saas_revenue_records_uniq"),
        )

    if not _has("global_config_settings"):
        op.create_table(
            "global_config_settings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_setting", sa.String(200), nullable=False, index=True),
            sa.Column("valeur", sa.Text, nullable=True),
            sa.Column("categorie", sa.String(50), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("modifie_par", sa.String(200), nullable=True),
            sa.Column("date_modif", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_setting", name="uix_global_config_settings_uniq"),
        )

    if not _has("dr_plans"):
        op.create_table(
            "dr_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("scenario", sa.String(50), nullable=True),
            sa.Column("rto_heures", sa.Numeric, nullable=True),
            sa.Column("rpo_minutes", sa.Numeric, nullable=True),
            sa.Column("solution_secours", sa.Text, nullable=True),
            sa.Column("date_dernier_test", sa.Date, nullable=True),
            sa.Column("resultat_test", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dr_plans_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
