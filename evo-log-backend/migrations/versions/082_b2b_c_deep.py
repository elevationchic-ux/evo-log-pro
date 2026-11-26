"""082 : tables expansion client-b2b (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "082_b2b_c_deep"
down_revision = "081_rh_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "b2bc_contracts",
    "b2bc_price_lists",
    "b2bc_sales_orders",
    "b2bc_credit_accounts",
    "b2bc_support_tickets",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("b2bc_contracts"):
        op.create_table(
            "b2bc_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("type_contrat", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("valeur_annuelle", sa.Numeric, nullable=True),
            sa.Column("contact", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2bc_contracts_uniq"),
        )

    if not _has("b2bc_price_lists"):
        op.create_table(
            "b2bc_price_lists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("version", sa.String(200), nullable=True),
            sa.Column("devise", sa.String(200), nullable=True),
            sa.Column("date_debut_validite", sa.Date, nullable=True),
            sa.Column("date_fin_validite", sa.Date, nullable=True),
            sa.Column("remise_globale_pct", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2bc_price_lists_uniq"),
        )

    if not _has("b2bc_sales_orders"):
        op.create_table(
            "b2bc_sales_orders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("date_commande", sa.Date, nullable=True),
            sa.Column("nb_lignes", sa.Integer, nullable=True),
            sa.Column("montant_total", sa.Numeric, nullable=True),
            sa.Column("date_livraison_souhaitee", sa.Date, nullable=True),
            sa.Column("contrat_ref", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2bc_sales_orders_uniq"),
        )

    if not _has("b2bc_credit_accounts"):
        op.create_table(
            "b2bc_credit_accounts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("limite_credit", sa.Numeric, nullable=True),
            sa.Column("encours", sa.Numeric, nullable=True),
            sa.Column("delai_paiement_jours", sa.Integer, nullable=True),
            sa.Column("date_dernier_paiement", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2bc_credit_accounts_uniq"),
        )

    if not _has("b2bc_support_tickets"):
        op.create_table(
            "b2bc_support_tickets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("sujet", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("priorite", sa.String(200), nullable=True),
            sa.Column("date_ouverture", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_resolution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_b2bc_support_tickets_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
