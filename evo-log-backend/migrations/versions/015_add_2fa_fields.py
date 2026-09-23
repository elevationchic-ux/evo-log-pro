"""015 champs d'authentification a deux facteurs (TOTP) sur users

Revision ID: 015_add_2fa_fields
Revises: 014_schema_parity_from_orm
Create Date: 2026-09-23

Ajoute a la table ``users`` les colonnes necessaires a l'2FA TOTP :
    - two_factor_enabled      : active/exige la verification TOTP
    - two_factor_secret       : secret base32 (stocke, jamais renvoye en clair)
    - two_factor_confirmed_at : horodatage de la validation du secret

Idempotent (garde d'existence des colonnes) et multi-dialecte : drop en mode
batch pour SQLite (qui ne supporte pas ALTER ... DROP COLUMN nativement).
"""
from alembic import op
import sqlalchemy as sa


revision = "015_add_2fa_fields"
down_revision = "014_schema_parity_from_orm"
branch_labels = None
depends_on = None


def _user_columns():
    inspector = sa.inspect(op.get_bind())
    if "users" not in set(inspector.get_table_names()):
        return set()
    return {c["name"] for c in inspector.get_columns("users")}


def upgrade():
    cols = _user_columns()
    if "two_factor_enabled" not in cols:
        # NOT NULL + defaut false : les lignes existantes basculent en 2FA off.
        op.add_column(
            "users",
            sa.Column(
                "two_factor_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    if "two_factor_secret" not in cols:
        op.add_column(
            "users",
            sa.Column("two_factor_secret", sa.String(length=64), nullable=True),
        )
    if "two_factor_confirmed_at" not in cols:
        op.add_column(
            "users",
            sa.Column("two_factor_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade():
    cols = _user_columns()
    to_drop = [
        name
        for name in ("two_factor_enabled", "two_factor_secret", "two_factor_confirmed_at")
        if name in cols
    ]
    if to_drop:
        with op.batch_alter_table("users") as batch_op:
            for name in to_drop:
                batch_op.drop_column(name)
