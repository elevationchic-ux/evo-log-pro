"""058 : tables expansion admin-saas (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "058_admin_deep"
down_revision = "057_reports_deep"
branch_labels = None
depends_on = None


TABLES = [
    "feature_flags",
    "api_quotas",
    "white_labels",
    "tenant_onboardings",
    "saas_api_keys",
    "tenant_webhooks",
    "data_migrations",
    "platform_tickets",
    "billing_entries",
    "usage_analytics",
    "uptime_records",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("feature_flags"):
        op.create_table(
            "feature_flags",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_flag", sa.String(200), nullable=False, index=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("tenants_concernes", sa.Text, nullable=True),
            sa.Column("date_debut_rollout", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_flag", name="uix_feature_flags_uniq"),
        )

    if not _has("api_quotas"):
        op.create_table(
            "api_quotas",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("api_group", sa.String(200), nullable=True),
            sa.Column("limite_minute", sa.Integer, nullable=True),
            sa.Column("limite_jour", sa.Integer, nullable=True),
            sa.Column("consommation_actuelle", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_api_quotas_uniq"),
        )

    if not _has("white_labels"):
        op.create_table(
            "white_labels",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("nom_marque", sa.String(200), nullable=True),
            sa.Column("domaine_personnalise", sa.String(200), nullable=True),
            sa.Column("logo_url", sa.String(200), nullable=True),
            sa.Column("couleur_primaire", sa.String(200), nullable=True),
            sa.Column("couleur_secondaire", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_white_labels_uniq"),
        )

    if not _has("tenant_onboardings"):
        op.create_table(
            "tenant_onboardings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_activation", sa.Date, nullable=True),
            sa.Column("nb_etapes_completes", sa.Integer, nullable=True),
            sa.Column("responsable_succeed", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tenant_onboardings_uniq"),
        )

    if not _has("saas_api_keys"):
        op.create_table(
            "saas_api_keys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("label", sa.String(200), nullable=True),
            sa.Column("scopes", sa.Text, nullable=True),
            sa.Column("date_creation", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("derniere_utilisation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_saas_api_keys_uniq"),
        )

    if not _has("tenant_webhooks"):
        op.create_table(
            "tenant_webhooks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("url_destination", sa.String(200), nullable=True),
            sa.Column("evenements_abonnes", sa.Text, nullable=True),
            sa.Column("secret_hmac", sa.String(200), nullable=True),
            sa.Column("dernier_succes", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tenant_webhooks_uniq"),
        )

    if not _has("data_migrations"):
        op.create_table(
            "data_migrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("type_migration", sa.String(50), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("nb_lignes_prevues", sa.Integer, nullable=True),
            sa.Column("nb_lignes_importees", sa.Integer, nullable=True),
            sa.Column("nb_lignes_rejetees", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_data_migrations_uniq"),
        )

    if not _has("platform_tickets"):
        op.create_table(
            "platform_tickets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("priorite", sa.String(50), nullable=True),
            sa.Column("assigne_a", sa.String(200), nullable=True),
            sa.Column("date_creation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_platform_tickets_uniq"),
        )

    if not _has("billing_entries"):
        op.create_table(
            "billing_entries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("type_facture", sa.String(50), nullable=True),
            sa.Column("montant_ht_xaf", sa.Numeric, nullable=True),
            sa.Column("tva_xaf", sa.Numeric, nullable=True),
            sa.Column("total_ttc_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_billing_entries_uniq"),
        )

    if not _has("usage_analytics"):
        op.create_table(
            "usage_analytics",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant_id", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("utilisateurs_actifs", sa.Integer, nullable=True),
            sa.Column("utilisateurs_seats", sa.Integer, nullable=True),
            sa.Column("taux_adoption_pct", sa.Numeric, nullable=True),
            sa.Column("score_sante", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_usage_analytics_uniq"),
        )

    if not _has("uptime_records"):
        op.create_table(
            "uptime_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("service", sa.String(200), nullable=True),
            sa.Column("region", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("latence_ms", sa.Integer, nullable=True),
            sa.Column("disponibilite_pct", sa.Numeric, nullable=True),
            sa.Column("date_mesure", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_uptime_records_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
