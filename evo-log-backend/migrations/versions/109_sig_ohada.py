"""109 : table sig (Situation Globale des Entreprises OHADA).

Revision ID: 109_sig_ohada
Revises: 108_tft_ohada
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "109_sig_ohada"
down_revision = "108_tft_ohada"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "sig" in set(sa.inspect(bind).get_table_names()):
        return
    op.create_table(
        "sig",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercice_id", sa.Integer(), nullable=False),
        sa.Column("date_sig", sa.Date(), nullable=False),
        sa.Column("effectif_moyen", sa.Numeric(10, 2), nullable=True),
        sa.Column("masse_salariale", sa.Numeric(15, 2), nullable=True),
        sa.Column("chiffre_affaires", sa.Numeric(15, 2), nullable=True),
        sa.Column("excédent_brut_exploitation", sa.Numeric(15, 2), nullable=True),
        sa.Column("capacite_autofinancement", sa.Numeric(15, 2), nullable=True),
        sa.Column("investissements", sa.Numeric(15, 2), nullable=True),
        sa.Column("besoin_en_fonds_de_roulement", sa.Numeric(15, 2), nullable=True),
        sa.Column("tresorerie_nette", sa.Numeric(15, 2), nullable=True),
        sa.Column("resultat_net", sa.Numeric(15, 2), nullable=True),
        sa.Column("devise", sa.String(length=3), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("valide_par", sa.String(length=100), nullable=True),
        sa.Column("date_validation", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["exercice_id"], ["exercices_comptables.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sig_id", "sig", ["id"])


def downgrade() -> None:
    op.drop_table("sig")
