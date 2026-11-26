"""086 : tables expansion admin-tenant (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "086_admin_tenant_c_deep"
down_revision = "085_superadmin_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "admtd_domain_configs",
    "admtd_dns_records",
    "admtd_data_residency",
    "admtd_feature_entitlements",
    "admtd_usage_quotas",
    "admtd_impersonation_logs",
    "admtd_onboarding_steps",
    "admtd_white_label_configs",
    "admtd_tenant_backups",
    "admtd_integration_webhooks",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("admtd_domain_configs"):
        op.create_table(
            "admtd_domain_configs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("domaine", sa.String(200), nullable=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("certificat_ssl", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_domain_configs_uniq"),
        )

    if not _has("admtd_dns_records"):
        op.create_table(
            "admtd_dns_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_hote", sa.String(200), nullable=True),
            sa.Column("type_enregistrement", sa.String(200), nullable=True),
            sa.Column("valeur", sa.String(200), nullable=True),
            sa.Column("ttl_secondes", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_dns_records_uniq"),
        )

    if not _has("admtd_data_residency"):
        op.create_table(
            "admtd_data_residency",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("region", sa.String(200), nullable=True),
            sa.Column("hebergeur", sa.String(200), nullable=True),
            sa.Column("certification_conforme", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_data_residency_uniq"),
        )

    if not _has("admtd_feature_entitlements"):
        op.create_table(
            "admtd_feature_entitlements",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("module", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("limite", sa.Integer, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_feature_entitlements_uniq"),
        )

    if not _has("admtd_usage_quotas"):
        op.create_table(
            "admtd_usage_quotas",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ressource", sa.String(200), nullable=True),
            sa.Column("quota_autorise", sa.Integer, nullable=True),
            sa.Column("consomme", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_usage_quotas_uniq"),
        )

    if not _has("admtd_impersonation_logs"):
        op.create_table(
            "admtd_impersonation_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("admin", sa.String(200), nullable=True),
            sa.Column("cible_tenant", sa.String(200), nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_impersonation_logs_uniq"),
        )

    if not _has("admtd_onboarding_steps"):
        op.create_table(
            "admtd_onboarding_steps",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("etape", sa.String(200), nullable=True),
            sa.Column("ordre", sa.Integer, nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("date_completion", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_onboarding_steps_uniq"),
        )

    if not _has("admtd_white_label_configs"):
        op.create_table(
            "admtd_white_label_configs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("nom_affiche", sa.String(200), nullable=True),
            sa.Column("logo_url", sa.String(200), nullable=True),
            sa.Column("couleur_principale", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_white_label_configs_uniq"),
        )

    if not _has("admtd_tenant_backups"):
        op.create_table(
            "admtd_tenant_backups",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("taille_octets", sa.Integer, nullable=True),
            sa.Column("frequence", sa.String(200), nullable=True),
            sa.Column("derniere_reussite", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_tenant_backups_uniq"),
        )

    if not _has("admtd_integration_webhooks"):
        op.create_table(
            "admtd_integration_webhooks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("url_cible", sa.String(200), nullable=True),
            sa.Column("evenement", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admtd_integration_webhooks_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
