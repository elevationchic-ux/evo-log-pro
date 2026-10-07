"""084 : tables expansion admin-saas (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "084_admin_c_deep"
down_revision = "083_reports_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "admc_subscription_plans",
    "admc_tenant_invites",
    "admc_api_tokens",
    "admc_billing_invoices",
    "admc_usage_metering",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("admc_subscription_plans"):
        op.create_table(
            "admc_subscription_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("prix_mensuel", sa.Numeric, nullable=True),
            sa.Column("nb_utilisateurs", sa.Integer, nullable=True),
            sa.Column("nb_modules", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admc_subscription_plans_uniq"),
        )

    if not _has("admc_tenant_invites"):
        op.create_table(
            "admc_tenant_invites",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("email", sa.String(200), nullable=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("role_propose", sa.String(200), nullable=True),
            sa.Column("invite_par", sa.String(200), nullable=True),
            sa.Column("date_expiration", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admc_tenant_invites_uniq"),
        )

    if not _has("admc_api_tokens"):
        op.create_table(
            "admc_api_tokens",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("portee", sa.String(200), nullable=True),
            sa.Column("cree_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("expire_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("derniere_utilisation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admc_api_tokens_uniq"),
        )

    if not _has("admc_billing_invoices"):
        op.create_table(
            "admc_billing_invoices",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("periode_facturee", sa.String(200), nullable=True),
            sa.Column("montant_ht", sa.Numeric, nullable=True),
            sa.Column("tva", sa.Numeric, nullable=True),
            sa.Column("montant_ttc", sa.Numeric, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admc_billing_invoices_uniq"),
        )

    if not _has("admc_usage_metering"):
        op.create_table(
            "admc_usage_metering",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tenant", sa.String(200), nullable=True),
            sa.Column("ressource", sa.String(200), nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("quantite_consommee", sa.Numeric, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("date_releve", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_admc_usage_metering_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
