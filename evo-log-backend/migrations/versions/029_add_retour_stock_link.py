"""029 Liaison retour client -> ligne de stock (reintegration physique modelisee).

Revision ID: 029_add_retour_stock_link
Revises: 028_full_orm_parity
Create Date: 2026-10-01

Contexte (P2 issu du batch 17, relance au §21 du rapport Zero-Mock) :
    Le circuit /api/v1/magasin-avance/retours reconstruit au batch 17 devait
    refuser toute reintegration en stock : le modele ``RetourClient`` n'avait
    AUCUNE colonne reliant un retour a une ligne de ``stocks``. Ecrire un
    ``MouvementStock`` a ce stade aurait ete inventer une donnee  le rapport
    l'a declare explicitement : « une migration ajoutant cette liaison serait
    le seul moyen honnete de la rendre reelle ». La voici.

    Cette migration ajoute la liaison, SANS jamais deviner de donnee :
        retours_client : stock_id (NULLable) -> stocks.id
    Les retours deja en base restent ``stock_id = NULL`` (« ligne de retour non
    precisee ») ; le router /traiter ne reintegre desormais que quand la ligne
    est explicitement renseignee a la creation du retour.

Proprietes (conventions 024/027) :
    - IDEMPOTENT par introspection : colonne deja presente -> no-op ; table
      ``retours_client`` absente (base vierge alignee par create_all ou par la
      parite 014/028, qui creent la colonne depuis l'ORM) -> no-op.
    - NON DESTRUCTIF : ajoute uniquement, NULLable, aucune valeur ecrite.
    - FK en mode batch SQLite (recreation de table) seulement si la table mere
      ``stocks`` existe ; PostgreSQL recoit la FK nativement.
    - downgrade sans effet assume : dropper la colonne detruirait les
      reintegrements deja journalises via cette liaison ; une colonne NULLable
      en trop ne casse rien (convention declaree de 027).
"""
from alembic import op
import sqlalchemy as sa


revision = "029_add_retour_stock_link"
down_revision = "028_full_orm_parity"
branch_labels = None
depends_on = None


TABLE = "retours_client"
CIBLE_FK = "stocks"
COLONNE = "stock_id"
FK_NOM = "fk_retours_client_stock_id_stocks"


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    if TABLE not in tables:
        # Base neuve : create_all / parite 014+028 creent deja la colonne
        # depuis l'ORM. Rien a ajouter, rien a deviner.
        return
    colonnes = {c["name"] for c in insp.get_columns(TABLE)}
    dialect = op.get_context().dialect.name

    if COLONNE not in colonnes:
        op.add_column(TABLE, sa.Column(COLONNE, sa.Integer(), nullable=True))
        colonnes.add(COLONNE)

    # Index de rattachement (nommage ORM ix_<table>_<colonne>), idempotent.
    index_existants = {i["name"] for i in insp.get_indexes(TABLE)}
    nom_index = f"ix_{TABLE}_{COLONNE}"
    if nom_index not in index_existants:
        op.create_index(nom_index, TABLE, [COLONNE])

    # FK : posee seulement si la table mere existe et si la contrainte
    # n'est pas deja en base.
    if CIBLE_FK in tables:
        fks_exist = {
            fk["name"] for fk in insp.get_foreign_keys(TABLE) if fk["name"]
        }
        if FK_NOM not in fks_exist:
            if dialect == "postgresql":
                op.create_foreign_key(
                    FK_NOM, TABLE, CIBLE_FK, [COLONNE], ["id"]
                )
            else:
                # SQLite ne sait pas ALTER ... ADD CONSTRAINT : mode batch.
                with op.batch_alter_table(TABLE) as batch_op:
                    batch_op.create_foreign_key(
                        FK_NOM, CIBLE_FK, [COLONNE], ["id"]
                    )


def downgrade():
    """Volontairement sans effet (convention 027).

    La colonne peut porter des liaisons sur lesquelles des mouvements de stock
    ont deja ete journalises : la dropper rendrait ces ecritures orphelines.
    Une colonne NULLable en trop ne casse aucun fonctionnement, alors qu'une
    donnee perdue est irreversible.
    """
    pass
