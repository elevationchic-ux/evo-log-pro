"""056 : tables expansion client-b2b (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "056_b2b_deep"
down_revision = "055_qhse_deep"
branch_labels = None
depends_on = None


TABLES = [
    "client_onboardings",
    "sla_contracts",
    "b2b_contracts",
    "satisfaction_surveys",
    "client_credit_limits",
    "b2b_documents",
    "service_requests",
    "pricing_agreements",
    "shipment_bookings",
    "client_claims",
    "account_reports",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("client_onboardings"):
        op.create_table(
            "client_onboardings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("raison_sociale", sa.String(200), nullable=True),
            sa.Column("niu", sa.String(200), nullable=True),
            sa.Column("rc", sa.String(200), nullable=True),
            sa.Column("contact_principal", sa.String(200), nullable=True),
            sa.Column("email", sa.String(200), nullable=True),
            sa.Column("telephone", sa.String(200), nullable=True),
            sa.Column("date_demande", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_client_onboardings_uniq"),
        )

    if not _has("sla_contracts"):
        op.create_table(
            "sla_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("type_prestation", sa.String(200), nullable=True),
            sa.Column("engagement_valeur", sa.Numeric, nullable=True),
            sa.Column("taux_atteint_pct", sa.Numeric, nullable=True),
            sa.Column("penalite_xaf", sa.Numeric, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sla_contracts_uniq"),
        )

    if not _has("b2b_contracts"):
        op.create_table(
            "b2b_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_contrat", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("type_contrat", sa.String(50), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("montant_engage_xaf", sa.Numeric, nullable=True),
            sa.Column("nb_avenants", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_contrat", name="uix_b2b_contracts_uniq"),
        )

    if not _has("satisfaction_surveys"):
        op.create_table(
            "satisfaction_surveys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("date_enquete", sa.Date, nullable=True),
            sa.Column("note_global", sa.Numeric, nullable=True),
            sa.Column("score_nps", sa.Integer, nullable=True),
            sa.Column("commentaires", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_satisfaction_surveys_uniq"),
        )

    if not _has("client_credit_limits"):
        op.create_table(
            "client_credit_limits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("plafond_xaf", sa.Numeric, nullable=True),
            sa.Column("encours_actuel_xaf", sa.Numeric, nullable=True),
            sa.Column("delai_paiement_jours", sa.Integer, nullable=True),
            sa.Column("date_revision", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_client_credit_limits_uniq"),
        )

    if not _has("b2b_documents"):
        op.create_table(
            "b2b_documents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("type_document", sa.String(200), nullable=True),
            sa.Column("nom_fichier", sa.String(200), nullable=True),
            sa.Column("date_envoi", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_reception", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2b_documents_uniq"),
        )

    if not _has("service_requests"):
        op.create_table(
            "service_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("type_demande", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("date_creation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_echeance", sa.DateTime(timezone=True), nullable=True),
            sa.Column("priorite", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_service_requests_uniq"),
        )

    if not _has("pricing_agreements"):
        op.create_table(
            "pricing_agreements",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("type_prestation", sa.String(200), nullable=True),
            sa.Column("remise_pct", sa.Numeric, nullable=True),
            sa.Column("palier_volume", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pricing_agreements_uniq"),
        )

    if not _has("shipment_bookings"):
        op.create_table(
            "shipment_bookings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("type_expedition", sa.String(50), nullable=True),
            sa.Column("date_reservation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("conteneurs_prevus", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_shipment_bookings_uniq"),
        )

    if not _has("client_claims"):
        op.create_table(
            "client_claims",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("date_reclamation", sa.Date, nullable=True),
            sa.Column("montant_reclame_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_client_claims_uniq"),
        )

    if not _has("account_reports"):
        op.create_table(
            "account_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("factures_emises_xaf", sa.Numeric, nullable=True),
            sa.Column("reglements_recus_xaf", sa.Numeric, nullable=True),
            sa.Column("solde_a_payer_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_account_reports_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
