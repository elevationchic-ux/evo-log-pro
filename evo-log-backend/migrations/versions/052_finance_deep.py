"""052 : tables expansion finance-ohada (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "052_finance_deep"
down_revision = "051_comptabilite_deep"
branch_labels = None
depends_on = None


TABLES = [
    "multiyear_budgets",
    "credit_facilities",
    "cash_pools",
    "financial_investments",
    "fx_exposures",
    "payment_schedules",
    "expense_reports",
    "petty_cash_boxes",
    "bank_guarantees",
    "lease_contracts",
    "cash_forecasts",
    "treasury_alerts",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("multiyear_budgets"):
        op.create_table(
            "multiyear_budgets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("exercice_debut", sa.Integer, nullable=True),
            sa.Column("exercice_fin", sa.Integer, nullable=True),
            sa.Column("montant_prevu_xaf", sa.Numeric, nullable=True),
            sa.Column("axes_strategiques", sa.Text, nullable=True),
            sa.Column("vote_ba", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_multiyear_budgets_uniq"),
        )

    if not _has("credit_facilities"):
        op.create_table(
            "credit_facilities",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("banque", sa.String(200), nullable=True),
            sa.Column("type_facilite", sa.String(50), nullable=True),
            sa.Column("montant_autorise_xaf", sa.Numeric, nullable=True),
            sa.Column("montant_utilise_xaf", sa.Numeric, nullable=True),
            sa.Column("taux_interet_pct", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_credit_facilities_uniq"),
        )

    if not _has("cash_pools"):
        op.create_table(
            "cash_pools",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("entite_pilote", sa.String(200), nullable=True),
            sa.Column("entites_participantes", sa.Text, nullable=True),
            sa.Column("montant_pool_xaf", sa.Numeric, nullable=True),
            sa.Column("interet_intragroupe_pct", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cash_pools_uniq"),
        )

    if not _has("financial_investments"):
        op.create_table(
            "financial_investments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_placement", sa.String(50), nullable=True),
            sa.Column("institution", sa.String(200), nullable=True),
            sa.Column("montant_place_xaf", sa.Numeric, nullable=True),
            sa.Column("rendement_attendu_pct", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_financial_investments_uniq"),
        )

    if not _has("fx_exposures"):
        op.create_table(
            "fx_exposures",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("devise", sa.String(200), nullable=True),
            sa.Column("exposition_nette", sa.Numeric, nullable=True),
            sa.Column("valeur_couverte", sa.Numeric, nullable=True),
            sa.Column("instrument_couverture", sa.String(50), nullable=True),
            sa.Column("taux_couverture_pct", sa.Numeric, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fx_exposures_uniq"),
        )

    if not _has("payment_schedules"):
        op.create_table(
            "payment_schedules",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("fournisseur_id", sa.Integer, nullable=True),
            sa.Column("facture_id", sa.Integer, nullable=True),
            sa.Column("montant_echeance_xaf", sa.Numeric, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("mode_reglement", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_payment_schedules_uniq"),
        )

    if not _has("expense_reports"):
        op.create_table(
            "expense_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_note_frais", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("montant_total_xaf", sa.Numeric, nullable=True),
            sa.Column("nb_justificatifs", sa.Integer, nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("validateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_note_frais", name="uix_expense_reports_uniq"),
        )

    if not _has("petty_cash_boxes"):
        op.create_table(
            "petty_cash_boxes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_regie", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("fond_initial_xaf", sa.Numeric, nullable=True),
            sa.Column("solde_actuel_xaf", sa.Numeric, nullable=True),
            sa.Column("date_derniere_reconciliation", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_regie", name="uix_petty_cash_boxes_uniq"),
        )

    if not _has("bank_guarantees"):
        op.create_table(
            "bank_guarantees",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("banque_emettrice", sa.String(200), nullable=True),
            sa.Column("beneficiaire", sa.String(200), nullable=True),
            sa.Column("type_garantie", sa.String(50), nullable=True),
            sa.Column("montant_xaf", sa.Numeric, nullable=True),
            sa.Column("commission_pct", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_bank_guarantees_uniq"),
        )

    if not _has("lease_contracts"):
        op.create_table(
            "lease_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_contrat", sa.String(50), nullable=True),
            sa.Column("bien_concerne", sa.String(200), nullable=True),
            sa.Column("loyer_mensuel_xaf", sa.Numeric, nullable=True),
            sa.Column("duree_mois", sa.Integer, nullable=True),
            sa.Column("valeur_residuelle_xaf", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_lease_contracts_uniq"),
        )

    if not _has("cash_forecasts"):
        op.create_table(
            "cash_forecasts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("horizon_mois", sa.Integer, nullable=True),
            sa.Column("entree_attendue_xaf", sa.Numeric, nullable=True),
            sa.Column("sortie_attendue_xaf", sa.Numeric, nullable=True),
            sa.Column("tresorerie_projete_xaf", sa.Numeric, nullable=True),
            sa.Column("hypothese", sa.Text, nullable=True),
            sa.Column("date_revision", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cash_forecasts_uniq"),
        )

    if not _has("treasury_alerts"):
        op.create_table(
            "treasury_alerts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_alerte", sa.String(50), nullable=True),
            sa.Column("seuil_declencheur", sa.Numeric, nullable=True),
            sa.Column("valeur_constatee", sa.Numeric, nullable=True),
            sa.Column("date_alerte", sa.DateTime(timezone=True), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_treasury_alerts_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
