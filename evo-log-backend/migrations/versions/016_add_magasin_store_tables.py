"""016 tables du domaine magasin store (Tranche A)

Revision ID: 016_add_magasin_store_tables
Revises: 015_add_2fa_fields
Create Date: 2026-09-24

Cree les 5 tables metier du domain store montees dans
app/routers/v1/magasin_store.py (CRUD reel, remplace le fallback
pending-modules sur /api/v1/magasin/{articles,clients,commandes,
ordres-transfert,bandes-livraison}) :

    articles, commandes, lignes_commande, ordres_transfert, bandes_livraison

Parite stricte avec l'ORM (meme voie que 014 : metadata.create_all sur le
sous-ensemble concerne) et idempotente (checkfirst=True + garde d'existence) :
rejouable sans danger sur une base deja consolidee par create_all().
"""
from alembic import op
import sqlalchemy as sa


revision = "016_add_magasin_store_tables"
down_revision = "015_add_2fa_fields"
branch_labels = None
depends_on = None


# Ordre topologique : articles -> commandes -> lignes_commande ->
# ordres_transfert -> bandes_livraison (FK internes respectees).
STORE_TABLES = [
    "articles",
    "commandes",
    "lignes_commande",
    "ordres_transfert",
    "bandes_livraison",
]


def _orm_metadata():
    # Meme strategie que 014 : reutiliser la Base/metadata de l'app pour une
    # DDL strictement identique au create_all() (tri, types, index, contraintes
    # d'unicite). app.models.__init__ importe le module magasin (qui porte les
    # nouveaux modeles) et résout donc les FK distantes (companies, clients,
    # entrepots, users).
    import app.models  # noqa: F401 - enregistre toute la metadata ORM
    from app.core.database import Base
    return Base.metadata


def upgrade():
    bind = op.get_bind()
    metadata = _orm_metadata()
    existing = set(sa.inspect(bind).get_table_names())

    tables = [metadata.tables[name] for name in STORE_TABLES if name not in existing]
    if not tables:
        return
    # checkfirst=True : double garde d'idempotence ; create_all tri
    # topologiquement les dependances internes du lot.
    metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    # Ordre inverse (bandes -> ... -> articles) pour ne jamais casser une FK.
    for name in reversed(STORE_TABLES):
        if name not in existing:
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=bind).drop(
                bind=bind, checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
