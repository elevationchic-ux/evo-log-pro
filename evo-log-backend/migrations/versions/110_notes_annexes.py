"""110 : table notes_annexes (notes normalisees SYSCOHADA).

Revision ID: 110_notes_annexes
Revises: 109_sig_ohada
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "110_notes_annexes"
down_revision = "109_sig_ohada"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "notes_annexes" in set(sa.inspect(bind).get_table_names()):
        return
    op.create_table(
        "notes_annexes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("annexes_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("intitule", sa.String(length=200), nullable=False),
        sa.Column("contenu", sa.Text(), nullable=True),
        sa.Column("montant", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["annexes_id"], ["annexes_ohada.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notes_annexes_id", "notes_annexes", ["id"])


def downgrade() -> None:
    op.drop_table("notes_annexes")
