"""Add tenant scope to B2B quotes.

Revision ID: 20260919_add_quote_company_scope
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20260919_add_quote_company_scope"
down_revision = None
branch_labels = None
depends_on = None


TABLE = "cotations_devis"


def _has_table(inspector) -> bool:
    return TABLE in set(inspector.get_table_names())


def _column_exists(inspector, column: str) -> bool:
    try:
        return column in {c["name"] for c in inspector.get_columns(TABLE)}
    except Exception:
        return False


def _index_exists(inspector, name: str) -> bool:
    try:
        return name in {i["name"] for i in inspector.get_indexes(TABLE)}
    except Exception:
        return False


def _fk_exists(inspector, name: str) -> bool:
    try:
        return name in {fk["name"] for fk in inspector.get_foreign_keys(TABLE)}
    except Exception:
        return False


def upgrade() -> None:
    # Garde "objet existant" (meme pattern que 011_tenant_scope_roots) :
    # cotations_devis n'est cree ni par 001..013 ni par une base vierge
    # (seul create_all de l'app la materialise), et la colonne company_id est
    # deja dans le modele ORM -> sans garde, cette migration casse aussi bien
    # sur une base neuve que sur une base deja bootstrapee par l'app.
    inspector = sa.inspect(op.get_bind())
    if not _has_table(inspector):
        return
    if not _column_exists(inspector, "company_id"):
        op.add_column(
            TABLE,
            sa.Column("company_id", sa.Integer(), nullable=True),
        )
    if not _index_exists(inspector, "ix_cotations_devis_company_id"):
        op.create_index(
            "ix_cotations_devis_company_id",
            TABLE,
            ["company_id"],
            unique=False,
        )
    if not _fk_exists(inspector, "fk_cotations_devis_company_id"):
        op.create_foreign_key(
            "fk_cotations_devis_company_id",
            TABLE,
            "companies",
            ["company_id"],
            ["id"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not _has_table(inspector):
        return
    if _index_exists(inspector, "ix_cotations_devis_company_id"):
        op.drop_index("ix_cotations_devis_company_id", table_name=TABLE)
    if _column_exists(inspector, "company_id"):
        if _fk_exists(inspector, "fk_cotations_devis_company_id"):
            op.drop_constraint(
                "fk_cotations_devis_company_id",
                TABLE,
                type_="foreignkey",
            )
        op.drop_column(TABLE, "company_id")
