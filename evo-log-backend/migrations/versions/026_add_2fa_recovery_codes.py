"""026 codes de secours 2FA sur users

Revision ID: 026_add_2fa_recovery_codes
Revises: 025_seed_superadmin_cadc
Create Date: 2026-09-25

Ajoute a la table ``users`` le stockage des codes de secours delivres avec la
2FA (RFC 6238) :

    - two_factor_recovery_codes       : tableau JSON de hachages SHA-256
      [{"hash": "...", "used_at": null|iso8601}]. Les codes en clair ne sont
      JAMAIS persistes ; ils ne sont visibles qu'au moment de la generation.
    - two_factor_recovery_issued_at   : horodatage de la derniere emission, qui
      permet a l'ecran d'indiquer depuis quand le jeu de codes courant date.

Sans ces colonnes, un utilisateur qui perd son generateur de codes ne peut plus
se connecter : la 2FA devenait un risque de verrouillage, pas une securite.

Idempotent (garde d'existence des colonnes) et multi-dialecte.
"""
from alembic import op
import sqlalchemy as sa


revision = "026_add_2fa_recovery_codes"
down_revision = "025_seed_superadmin_cadc"
branch_labels = None
depends_on = None


def _user_columns():
    inspector = sa.inspect(op.get_bind())
    if "users" not in set(inspector.get_table_names()):
        return set()
    return {c["name"] for c in inspector.get_columns("users")}


def upgrade():
    cols = _user_columns()
    if "two_factor_recovery_codes" not in cols:
        op.add_column(
            "users",
            sa.Column("two_factor_recovery_codes", sa.Text(), nullable=True),
        )
    if "two_factor_recovery_issued_at" not in cols:
        op.add_column(
            "users",
            sa.Column(
                "two_factor_recovery_issued_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )


def downgrade():
    cols = _user_columns()
    to_drop = [
        name
        for name in ("two_factor_recovery_codes", "two_factor_recovery_issued_at")
        if name in cols
    ]
    if to_drop:
        with op.batch_alter_table("users") as batch_op:
            for name in to_drop:
                batch_op.drop_column(name)
