"""080 : tables expansion finance-ohada (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "080_finance_c_deep"
down_revision = "079_compta_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "finc_cash_flow_forecasts",
    "finc_invoice_financings",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("finc_cash_flow_forecasts"):
        op.create_table(
            "finc_cash_flow_forecasts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("solde_debut", sa.Numeric, nullable=True),
            sa.Column("entrees_prevues", sa.Numeric, nullable=True),
            sa.Column("sorties_prevues", sa.Numeric, nullable=True),
            sa.Column("position_finale", sa.Numeric, nullable=True),
            sa.Column("horizon_jours", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_finc_cash_flow_forecasts_uniq"),
        )

    if not _has("finc_invoice_financings"):
        op.create_table(
            "finc_invoice_financings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("affacteur", sa.String(200), nullable=True),
            sa.Column("facture", sa.String(200), nullable=True),
            sa.Column("montant_facture", sa.Numeric, nullable=True),
            sa.Column("avance_pct", sa.Integer, nullable=True),
            sa.Column("commission", sa.Numeric, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_finc_invoice_financings_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
