"""051 : tables expansion comptabilite-ohada (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "051_comptabilite_deep"
down_revision = "050_magasin_deep"
branch_labels = None
depends_on = None


TABLES = [
    "asset_registrations",
    "depreciation_schedules",
    "provisions",
    "bank_reconciliations",
    "intercompany_entries",
    "budget_controls",
    "audit_pafs",
    "tax_declarations",
    "payroll_entries",
    "treasury_accounts",
    "analytical_sections",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("asset_registrations"):
        op.create_table(
            "asset_registrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_inventaire", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(50), nullable=True),
            sa.Column("date_acquisition", sa.Date, nullable=True),
            sa.Column("valeur_acquisition_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_residuelle_xaf", sa.Numeric, nullable=True),
            sa.Column("duree_amortissement_an", sa.Integer, nullable=True),
            sa.Column("mode_amortissement", sa.String(50), nullable=True),
            sa.Column("compte_immo", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_inventaire", name="uix_asset_registrations_uniq"),
        )

    if not _has("depreciation_schedules"):
        op.create_table(
            "depreciation_schedules",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("asset_id", sa.Integer, nullable=True),
            sa.Column("exercice", sa.Integer, nullable=True),
            sa.Column("dotation_xaf", sa.Numeric, nullable=True),
            sa.Column("cumul_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_nette_xaf", sa.Numeric, nullable=True),
            sa.Column("date_ecriture", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_depreciation_schedules_uniq"),
        )

    if not _has("provisions"):
        op.create_table(
            "provisions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_provision", sa.String(50), nullable=True),
            sa.Column("exercice", sa.Integer, nullable=True),
            sa.Column("montant_xaf", sa.Numeric, nullable=True),
            sa.Column("date_constat", sa.Date, nullable=True),
            sa.Column("compte_charge", sa.String(200), nullable=True),
            sa.Column("comporte_passif", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("motivation", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_provisions_uniq"),
        )

    if not _has("bank_reconciliations"):
        op.create_table(
            "bank_reconciliations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("compte_banque", sa.String(200), nullable=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("solde_banque_xaf", sa.Numeric, nullable=True),
            sa.Column("solde_compta_xaf", sa.Numeric, nullable=True),
            sa.Column("ecart_xaf", sa.Numeric, nullable=True),
            sa.Column("nb_lignes_pointees", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_bank_reconciliations_uniq"),
        )

    if not _has("intercompany_entries"):
        op.create_table(
            "intercompany_entries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("entite_emettrice", sa.String(200), nullable=True),
            sa.Column("entite_destinatrice", sa.String(200), nullable=True),
            sa.Column("date_ecriture", sa.Date, nullable=True),
            sa.Column("montant_xaf", sa.Numeric, nullable=True),
            sa.Column("nature", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_intercompany_entries_uniq"),
        )

    if not _has("budget_controls"):
        op.create_table(
            "budget_controls",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("centre_cout", sa.String(200), nullable=True),
            sa.Column("exercice", sa.Integer, nullable=True),
            sa.Column("budget_prevu_xaf", sa.Numeric, nullable=True),
            sa.Column("consomme_xaf", sa.Numeric, nullable=True),
            sa.Column("engagement_xaf", sa.Numeric, nullable=True),
            sa.Column("ecart_pct", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_budget_controls_uniq"),
        )

    if not _has("audit_pafs"):
        op.create_table(
            "audit_pafs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("hash_ligne", sa.String(200), nullable=False, index=True),
            sa.Column("date_ecriture", sa.Date, nullable=True),
            sa.Column("numero_piece", sa.String(200), nullable=True),
            sa.Column("compte", sa.String(200), nullable=True),
            sa.Column("libelle", sa.Text, nullable=True),
            sa.Column("debit_xaf", sa.Numeric, nullable=True),
            sa.Column("credit_xaf", sa.Numeric, nullable=True),
            sa.Column("hash_precedent", sa.String(200), nullable=True),
            sa.Column("validite", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "hash_ligne", name="uix_audit_pafs_uniq"),
        )

    if not _has("tax_declarations"):
        op.create_table(
            "tax_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_declaration", sa.String(50), nullable=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("base_imposable_xaf", sa.Numeric, nullable=True),
            sa.Column("droits_xaf", sa.Numeric, nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tax_declarations_uniq"),
        )

    if not _has("payroll_entries"):
        op.create_table(
            "payroll_entries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("masse_salariale_xaf", sa.Numeric, nullable=True),
            sa.Column("charges_patronales_xaf", sa.Numeric, nullable=True),
            sa.Column("impot_retenu_xaf", sa.Numeric, nullable=True),
            sa.Column("net_paye_xaf", sa.Numeric, nullable=True),
            sa.Column("date_passage", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_payroll_entries_uniq"),
        )

    if not _has("treasury_accounts"):
        op.create_table(
            "treasury_accounts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_compte", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("type_compte", sa.String(50), nullable=True),
            sa.Column("banque", sa.String(200), nullable=True),
            sa.Column("rib", sa.String(200), nullable=True),
            sa.Column("solde_actuel_xaf", sa.Numeric, nullable=True),
            sa.Column("devise", sa.String(200), nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_compte", name="uix_treasury_accounts_uniq"),
        )

    if not _has("analytical_sections"):
        op.create_table(
            "analytical_sections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_section", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("type_section", sa.String(50), nullable=True),
            sa.Column("cle_repartition", sa.String(200), nullable=True),
            sa.Column("unite_oeuvre", sa.String(200), nullable=True),
            sa.Column("cout_total_xaf", sa.Numeric, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_section", name="uix_analytical_sections_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
