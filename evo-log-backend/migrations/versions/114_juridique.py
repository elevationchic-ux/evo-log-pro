"""114 : domaine juridique (contrats + contentieux).

Revision ID: 114_juridique
Revises: 113_maint_plan_compteur
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "114_juridique"
down_revision = "113_maint_plan_compteur"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    existantes = set(sa.inspect(bind).get_table_names())

    if "juridique_contrats" not in existantes:
        op.create_table(
            "juridique_contrats",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("reference", sa.String(length=60), nullable=False),
            sa.Column("type_contrat", sa.String(length=40), nullable=False),
            sa.Column("objet", sa.Text(), nullable=False),
            sa.Column("partie_adverse", sa.String(length=300), nullable=True),
            sa.Column("montant", sa.Numeric(18, 2), nullable=True),
            sa.Column("devise", sa.String(length=3), nullable=True),
            sa.Column("date_debut", sa.Date(), nullable=False),
            sa.Column("date_fin", sa.Date(), nullable=True),
            sa.Column("reconduction", sa.String(length=20), nullable=True),
            sa.Column("preavis_jours", sa.Integer(), nullable=True),
            sa.Column("statut", sa.String(length=20), nullable=True),
            sa.Column("document_url", sa.String(length=500), nullable=True),
            sa.Column("document_hash", sa.String(length=128), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_juridique_contrats_id", "juridique_contrats", ["id"])
        op.create_index("ix_juridique_contrats_reference", "juridique_contrats", ["reference"])
        op.create_index("ix_juridique_contrats_statut", "juridique_contrats", ["statut"])
        op.create_index("ix_juridique_contrats_company_id", "juridique_contrats", ["company_id"])

    if "juridique_contentieux" not in existantes:
        op.create_table(
            "juridique_contentieux",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("reference", sa.String(length=60), nullable=False),
            sa.Column("contrat_id", sa.Integer(), nullable=True),
            sa.Column("type_contentieux", sa.String(length=40), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("montant_reclame", sa.Numeric(18, 2), nullable=True),
            sa.Column("montant_obtenu", sa.Numeric(18, 2), nullable=True),
            sa.Column("date_declaration", sa.Date(), nullable=False),
            sa.Column("date_echeance", sa.Date(), nullable=True),
            sa.Column("juridiction", sa.String(length=200), nullable=True),
            sa.Column("statut", sa.String(length=20), nullable=True),
            sa.Column("date_cloture", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.ForeignKeyConstraint(["contrat_id"], ["juridique_contrats.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_juridique_contentieux_id", "juridique_contentieux", ["id"])
        op.create_index("ix_juridique_contentieux_reference", "juridique_contentieux", ["reference"])
        op.create_index("ix_juridique_contentieux_statut", "juridique_contentieux", ["statut"])
        op.create_index("ix_juridique_contentieux_company_id", "juridique_contentieux", ["company_id"])
        op.create_index("ix_juridique_contentieux_contrat_id", "juridique_contentieux", ["contrat_id"])


def downgrade() -> None:
    op.drop_table("juridique_contentieux")
    op.drop_table("juridique_contrats")
