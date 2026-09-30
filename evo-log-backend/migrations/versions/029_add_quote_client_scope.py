"""029 : rattache les cotations de devis a un client reel et persiste le detail.

Le portail B2B (``POST /api/v1/b2b-portal/quotes``) chiffre une demande a partir
de la grille tarifaire persistee du tenant. Pour que le devis soit relisible
plus tard par le bon compte client, deux colonnes manquaient :

* ``client_id``  qui est le client demande (NULL = cotation sans compte) ;
* ``detail_lignes`` copie des lignes tarifaires ayant produit le montant.

Sans ``detail_lignes``, le montant total etant seul persiste, toute relecture
d'un devis impose de recalculer avec la grille du jour : un tarif modifie
reécrirait retroactivement un devis deja transmis au client. La colonne stocke
donc la facture reellement produite, pas une valeur recalculee.

Idempotent et garde "objet existant" (meme pattern que
20260919_add_quote_company_scope) : ``cotations_devis`` n'est creee par aucune
migration 001..013, seule la migration 014 (parite ORM) ou ``create_all`` la
materialise selon les environnements.

Revision ID: 029_add_quote_client_scope
Revises: 028_full_orm_parity
"""

from alembic import op
import sqlalchemy as sa


revision = "029_add_quote_client_scope"
down_revision = "028_full_orm_parity"
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
    inspector = sa.inspect(op.get_bind())
    if not _has_table(inspector):
        return

    if not _column_exists(inspector, "client_id"):
        op.add_column(
            TABLE,
            sa.Column("client_id", sa.Integer(), nullable=True),
        )
    if not _index_exists(inspector, "ix_cotations_devis_client_id"):
        op.create_index(
            "ix_cotations_devis_client_id",
            TABLE,
            ["client_id"],
            unique=False,
        )
    if not _fk_exists(inspector, "fk_cotations_devis_client_id"):
        op.create_foreign_key(
            "fk_cotations_devis_client_id",
            TABLE,
            "clients",
            ["client_id"],
            ["id"],
        )

    # JSON natif sur Postgres, TEXT sur SQLite (create_all y stocke du JSON
    # textualise) : on reste sur le type declare par l'ORM pour ne pas creer de
    # derive entre la base migree et la base generatee par l'app.
    if not _column_exists(inspector, "detail_lignes"):
        op.add_column(
            TABLE,
            sa.Column("detail_lignes", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not _has_table(inspector):
        return
    if _column_exists(inspector, "detail_lignes"):
        op.drop_column(TABLE, "detail_lignes")
    if _index_exists(inspector, "ix_cotations_devis_client_id"):
        op.drop_index("ix_cotations_devis_client_id", table_name=TABLE)
    if _column_exists(inspector, "client_id"):
        if _fk_exists(inspector, "fk_cotations_devis_client_id"):
            op.drop_constraint(
                "fk_cotations_devis_client_id",
                TABLE,
                type_="foreignkey",
            )
        op.drop_column(TABLE, "client_id")
