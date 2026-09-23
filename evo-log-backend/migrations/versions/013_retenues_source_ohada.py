"""013 split OHADA withholding tax into its own table

Add revision ID here: 013_retenues_source_ohada
Create Date: 2026-09-23

Le modele OHADA RetenueSource (finance_ohada) et le modele Cameroun
RetenueSourceCameroun (fiscalite_cameroun) declaraient la MEME table
`retenues_source` avec des colonnes NOT NULL incompatibles. En base migree
(008), l'endpoint POST /finance/retenues-source echouait : la table ne
contient que les colonnes Cameroun. Seperation propre : le volet OHADA passe
dans `retenues_source_ohada`.
"""
from alembic import op
import sqlalchemy as sa

revision = "013_retenues_source_ohada"
down_revision = "012_perf_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "retenues_source_ohada",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("numero_retenu", sa.String(length=50), nullable=False),
        sa.Column("facture_id", sa.Integer(), nullable=True),
        sa.Column("date_retenu", sa.Date(), nullable=False),
        sa.Column("type_retenu", sa.String(length=50), nullable=True),
        sa.Column("taux_retenu", sa.Numeric(), nullable=False),
        sa.Column("base_imposable", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("montant_retenu", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("devise", sa.String(length=3), nullable=True),
        sa.Column("beneficiaire", sa.String(length=100), nullable=True),
        sa.Column("raison_sociale", sa.String(length=200), nullable=True),
        sa.Column(
            "statut",
            sa.Enum("DUE", "PAYEE", "PARTIEL", "REPORT", "CONTENTIEUX", name="statuttaxe"),
            nullable=True,
        ),
        sa.Column("date_paiement", sa.Date(), nullable=True),
        sa.Column("reference_paiement", sa.String(length=100), nullable=True),
        sa.Column("declarer", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["facture_id"], ["factures.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_retenues_source_ohada_id", "retenues_source_ohada", ["id"], unique=False)
    op.create_index("ix_retenues_source_ohada_numero_retenu", "retenues_source_ohada", ["numero_retenu"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_retenues_source_ohada_numero_retenu", table_name="retenues_source_ohada")
    op.drop_index("ix_retenues_source_ohada_id", table_name="retenues_source_ohada")
    op.drop_table("retenues_source_ohada")
