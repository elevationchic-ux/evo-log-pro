"""020 Pont de compatibilite : tables des endpoints ajoutes cote backend.

Revision ID: 020_add_gap_bridge_tables
Revises: 019_add_transport_exploitation_tables
Create Date: 2026-09-25

Tables creees (depuis la metadata ORM, parite stricte) :
    system_settings   preferences cle/valeur par entreprise (profil global,
                      configuration systeme) alimentees par l'ecran Parametres
    tarifs            grille tarifaire commerciale (finance), lignes reelles

Aucune donnee inventee : les tables sont simplement mises en place, elles ne
sont remplies que par les ecritures proviennent des ecrans correspondants.

Meme voie que 014/016/017/018/019 : DDL generee depuis la metadata ORM,
idempotente (gardes d'existence) et rollback propre.
"""
from alembic import op
import sqlalchemy as sa


revision = "020_add_gap_bridge_tables"
down_revision = "019_add_transport_exploitation_tables"
branch_labels = None
depends_on = None


GAP_BRIDGE_TABLES = [
    "system_settings",
    "tarifs",
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
    tables = [metadata.tables[name] for name in GAP_BRIDGE_TABLES if name not in existing]
    if tables:
        metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    for name in reversed(GAP_BRIDGE_TABLES):
        if name not in _table_names():
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=op.get_bind()).drop(
                bind=op.get_bind(), checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
