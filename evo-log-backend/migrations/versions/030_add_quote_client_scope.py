"""030 : rattache les cotations de devis a un client reel et persiste le detail.

Le portail B2B (``POST /api/v1/b2b-portal/quotes``) chiffre une demande a partir
de la grille tarifaire persistee du tenant (table ``tarifs``). Pour que le devis
soit relisible plus tard par le bon compte client, deux colonnes manquaient :

* ``client_id``     -> de qui vient la demande (NULL = cotation sans compte) ;
* ``detail_lignes`` -> copie des lignes tarifaires ayant produit le montant.

Sans ``detail_lignes``, seul le total etant persiste, toute relecture d'un devis
reviendrait a le recalculer avec la grille du jour : un tarif modifie reécrirait
retroactivement un devis deja transmis au client. La colonne fige donc la
facturation reellement produite au moment de l'emission.

Proprietes (conventions 024/027/029) :
    - IDEMPOTENT par introspection : colonne deja presente -> no-op ; table
      ``cotations_devis`` absente (base vierge alignee par create_all ou par la
      parite 014/028, qui creent deja les colonnes depuis l'ORM) -> no-op.
    - NON DESTRUCTIF : ajoute uniquement, NULLable, aucune valeur ecrite.
    - FK en mode batch SQLite (SQLite ne sait pas ALTER ... ADD CONSTRAINT) ;
      PostgreSQL recoit la FK nativement.
    - downgrade sans effet assume : dropper ``detail_lignes`` detruirait le
      detail de devis deja transmis ; une colonne NULLable en trop ne casse
      rien (convention declaree de 027/029).

Revision ID: 030_add_quote_client_scope
Revises: 029_add_retour_stock_link
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa


revision = "030_add_quote_client_scope"
down_revision = "029_add_retour_stock_link"
branch_labels = None
depends_on = None


TABLE = "cotations_devis"
CIBLE_FK = "clients"
COLONNE_CLIENT = "client_id"
COLONNE_DETAIL = "detail_lignes"
FK_NOM = "fk_cotations_devis_client_id_clients"


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    if TABLE not in tables:
        # Base neuve : create_all / parite 014+028 creent deja les colonnes
        # depuis l'ORM. Rien a ajouter, rien a deviner.
        return
    colonnes = {c["name"] for c in insp.get_columns(TABLE)}
    dialect = op.get_context().dialect.name

    if COLONNE_CLIENT not in colonnes:
        op.add_column(TABLE, sa.Column(COLONNE_CLIENT, sa.Integer(), nullable=True))
        colonnes.add(COLONNE_CLIENT)
    if COLONNE_DETAIL not in colonnes:
        # JSON natif sur Postgres, TEXT sur SQLite (ce que fait deja l'ORM via
        # create_all) : on reste sur le type declare cote modele pour qu'une
        # base migree et une base generee par l'app ne divergent pas.
        op.add_column(TABLE, sa.Column(COLONNE_DETAIL, sa.JSON(), nullable=True))

    # Index de rattachement (nommage ORM ix_<table>_<colonne>), idempotent.
    index_existants = {i["name"] for i in insp.get_indexes(TABLE)}
    nom_index = f"ix_{TABLE}_{COLONNE_CLIENT}"
    if nom_index not in index_existants:
        op.create_index(nom_index, TABLE, [COLONNE_CLIENT])

    # FK posee seulement si la table mere existe et si la contrainte n'est pas
    # deja en base. Un devis dont le client a ete supprime depuis doit rester
    # lisible : la FK est une contrainte d'integrite, pas une cle obligatoire.
    if CIBLE_FK in tables:
        fks_exist = {
            fk["name"] for fk in insp.get_foreign_keys(TABLE) if fk["name"]
        }
        if FK_NOM not in fks_exist:
            if dialect == "postgresql":
                op.create_foreign_key(FK_NOM, TABLE, CIBLE_FK, [COLONNE_CLIENT], ["id"])
            else:
                with op.batch_alter_table(TABLE) as batch_op:
                    batch_op.create_foreign_key(
                        FK_NOM, CIBLE_FK, [COLONNE_CLIENT], ["id"]
                    )


def downgrade():
    """Volontairement sans effet (conventions 027/029).

    ``detail_lignes`` porte le detail facture de devis deja transmis aux
    clients : le dropper rendrait ces devis incomplets de facon irreversible.
    ``client_id`` non plus n'est pas droppable sans casser les devis rattaches.
    """
    pass
