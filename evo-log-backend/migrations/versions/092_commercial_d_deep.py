"""092 : tables expansion portail-commercial (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "092_commercial_d_deep"
down_revision = "091_declarant_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "comm_leads",
    "comm_opportunities",
    "comm_quotes",
    "comm_sales_orders",
    "comm_customer_visits",
    "comm_samples",
    "comm_tenders",
    "comm_contract_renewals",
    "comm_price_requests",
    "comm_credit_requests",
    "comm_order_modifications",
    "comm_complaints",
    "comm_upsells",
    "comm_commissions",
    "comm_pipeline_reviews",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("comm_leads"):
        op.create_table(
            "comm_leads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prospect", sa.String(200), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("segment", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_leads_uniq"),
        )

    if not _has("comm_opportunities"):
        op.create_table(
            "comm_opportunities",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("montant_estime", sa.Numeric, nullable=True),
            sa.Column("cloture_prevue", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_opportunities_uniq"),
        )

    if not _has("comm_quotes"):
        op.create_table(
            "comm_quotes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_quotes_uniq"),
        )

    if not _has("comm_sales_orders"):
        op.create_table(
            "comm_sales_orders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("devis", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_sales_orders_uniq"),
        )

    if not _has("comm_customer_visits"):
        op.create_table(
            "comm_customer_visits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("interlocuteur", sa.String(200), nullable=True),
            sa.Column("compte_rendu", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_customer_visits_uniq"),
        )

    if not _has("comm_samples"):
        op.create_table(
            "comm_samples",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_samples_uniq"),
        )

    if not _has("comm_tenders"):
        op.create_table(
            "comm_tenders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("acheteur", sa.String(200), nullable=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("date_limite", sa.Date, nullable=True),
            sa.Column("montant_offre", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_tenders_uniq"),
        )

    if not _has("comm_contract_renewals"):
        op.create_table(
            "comm_contract_renewals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("contrat", sa.String(200), nullable=True),
            sa.Column("echeance", sa.Date, nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_contract_renewals_uniq"),
        )

    if not _has("comm_price_requests"):
        op.create_table(
            "comm_price_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("remise", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_price_requests_uniq"),
        )

    if not _has("comm_credit_requests"):
        op.create_table(
            "comm_credit_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("encours_actuel", sa.Numeric, nullable=True),
            sa.Column("montant_souhaite", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_credit_requests_uniq"),
        )

    if not _has("comm_order_modifications"):
        op.create_table(
            "comm_order_modifications",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commande", sa.String(200), nullable=True),
            sa.Column("changement", sa.Text, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_order_modifications_uniq"),
        )

    if not _has("comm_complaints"):
        op.create_table(
            "comm_complaints",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("canal", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_complaints_uniq"),
        )

    if not _has("comm_upsells"):
        op.create_table(
            "comm_upsells",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("offre", sa.String(200), nullable=True),
            sa.Column("montant_potentiel", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_upsells_uniq"),
        )

    if not _has("comm_commissions"):
        op.create_table(
            "comm_commissions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commercial", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("base_vente", sa.Numeric, nullable=True),
            sa.Column("taux", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_commissions_uniq"),
        )

    if not _has("comm_pipeline_reviews"):
        op.create_table(
            "comm_pipeline_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commercial", sa.String(200), nullable=True),
            sa.Column("nb_opportunites", sa.Integer, nullable=True),
            sa.Column("valeur_ponderee", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_pipeline_reviews_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
