"""022 Sequences de numerotation legale (factures, avoirs, reglements).

Revision ID: 022_add_sequences_numerotation
Revises: 021_add_registre_entries
Create Date: 2026-09-25

Table creee (depuis la metadata ORM, parite stricte) :
    sequences_numerotation   compteurs légaux par (entreprise, type de pièce,
                             annee civile). Remplace la numerotation par
                             uuid/timestamp/ID recyclable, contraire a
                             l'exigence DGI de sequence continue sans trou.
"""
from alembic import op
import sqlalchemy as sa


revision = "022_add_sequences_numerotation"
down_revision = "021_add_registre_entries"
branch_labels = None
depends_on = None


SEQUENCE_TABLES = [
    "sequences_numerotation",
]


def _orm_metadata():
    import app.models  # noqa: F401 - enregistre toute la metadata ORM
    from app.core.database import Base
    return Base.metadata


def _table_names():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    bind = op.get_bind()
    metadata = _orm_metadata()
    existing = _table_names()
    tables = [metadata.tables[name] for name in SEQUENCE_TABLES if name not in existing]
    if tables:
        metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    for name in reversed(SEQUENCE_TABLES):
        if name not in _table_names():
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=op.get_bind()).drop(
                bind=op.get_bind(), checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
