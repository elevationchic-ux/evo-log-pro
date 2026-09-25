"""021 Registre generique multi-modules (inspections QHSE, BSDD, ISPS...).

Revision ID: 021_add_registre_entries
Revises: 020_rbac_granulaire_accreditations
Create Date: 2026-09-25

Table creee (depuis la metadata ORM, parite stricte) :
    registre_entries   lignes de registre persistees reellement depuis les
                       formulaires des ecrans (registry par module, payload
                       JSON, reference et statut). Aucune donnee inventee.
"""
from alembic import op
import sqlalchemy as sa


revision = "021_add_registre_entries"
down_revision = "020_rbac_granulaire_accreditations"
branch_labels = None
depends_on = None


REGISTRE_TABLES = [
    "registre_entries",
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
    tables = [metadata.tables[name] for name in REGISTRE_TABLES if name not in existing]
    if tables:
        metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    for name in reversed(REGISTRE_TABLES):
        if name not in _table_names():
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=op.get_bind()).drop(
                bind=op.get_bind(), checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
