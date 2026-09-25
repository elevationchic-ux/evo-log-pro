"""017 tables Tranche B : parc (zones, emplacements, mouvements gate) +
purchase (requisitions)

Revision ID: 017_add_parc_purchase_tables
Revises: 016_add_magasin_store_tables
Create Date: 2026-09-24

Tables creees :
    parc_zones, parc_emplacements, parc_mouvements, purchase_requisitions

Meme voie que 014/016 : DDL generee depuis la metadata ORM (parite stricte)
et idempotente (garde d'existence + checkfirst).
"""
from alembic import op
import sqlalchemy as sa


revision = "017_add_parc_purchase_tables"
down_revision = "016_add_magasin_store_tables"
branch_labels = None
depends_on = None


# Ordre topologique : les FK emplacements -> zones et mouvements ->
# emplacements imposent cet ordre de creation.
TRANCHE_B_TABLES = [
    "parc_zones",
    "parc_emplacements",
    "parc_mouvements",
    "purchase_requisitions",
]


def _orm_metadata():
    import app.models  # noqa: F401 - enregistre toute la metadata ORM
    from app.core.database import Base
    return Base.metadata


def upgrade():
    bind = op.get_bind()
    metadata = _orm_metadata()
    existing = set(sa.inspect(bind).get_table_names())

    tables = [metadata.tables[name] for name in TRANCHE_B_TABLES if name not in existing]
    if not tables:
        return
    metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    for name in reversed(TRANCHE_B_TABLES):
        if name not in existing:
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=bind).drop(
                bind=bind, checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
