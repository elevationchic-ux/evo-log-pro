"""079 : tables expansion comptabilite-ohada (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "079_compta_c_deep"
# Re-parente sur 081_coldchain_deep (branche pipeline->courier->coldchain restee
# en tete separate sur 078_dashboard_b_deep) pour garder un seul head lineaire.
down_revision = "081_coldchain_deep"
branch_labels = None
depends_on = None


TABLES = [
    "cmptc_journal_reversals",
    "cmptc_bank_reconciliations",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("cmptc_journal_reversals"):
        op.create_table(
            "cmptc_journal_reversals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ecriture_origine", sa.String(200), nullable=True),
            sa.Column("date_reversal", sa.Date, nullable=True),
            sa.Column("compte_debit", sa.String(200), nullable=True),
            sa.Column("compte_credit", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cmptc_journal_reversals_uniq"),
        )

    if not _has("cmptc_bank_reconciliations"):
        op.create_table(
            "cmptc_bank_reconciliations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("compte_banque", sa.String(200), nullable=True),
            sa.Column("date_releve", sa.Date, nullable=True),
            sa.Column("solde_comptable", sa.Numeric, nullable=True),
            sa.Column("solde_bancaire", sa.Numeric, nullable=True),
            sa.Column("ecart", sa.Numeric, nullable=True),
            sa.Column("date_rapprochement", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cmptc_bank_reconciliations_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
