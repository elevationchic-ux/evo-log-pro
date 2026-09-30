"""031 : colonnes priorite et pieces sur les ordres de maintenance.

L'ecran atelier ``/maintenance/edit`` collecte une priorite d'intervention et
la liste des pieces rechange a imputer. Le modele ``Maintenance`` ne portait
aucune colonne pour ces deux champs : la saisie etait acceptée par l'API puis
perdue a l'enregistrement, et rechargée vide. Plutot que de les noyer dans
``notes`` (ou de les supprimer du formulaire), on leur donne une colonne :

    maintenances.priorite  (basse | normale | urgente | critique)
    maintenances.pieces    (texte libre des pieces declarees)

``pieces`` reste du texte descriptif : la consommation reellement imputee au
WMS passe par ``POST /api/v1/maintenance/destockage-pieces`` et produit des
mouvements de stock traces. L'un declare l'intention, l'autre l'execution ;
confondre les deux ferait passer une liste indicative pour un debit de stock.

Proprietes (conventions 024/027/029/030) :
    - IDEMPOTENT par introspection : colonne deja presente -> no-op ; table
      ``maintenances`` absente (base vierge alignee par create_all ou par les
      migrations de parite, qui creent deja les colonnes depuis l'ORM) -> no-op.
    - NON DESTRUCTIF : ajoute uniquement, NULLable, aucune valeur ecrite. Les
      ordres deja en base restent ``priorite = NULL`` (« non renseignee ») :
      rien n'est requalifie retroactivement.
    - downgrade sans effet assume : dropper detruirait les priorites et listes
      de pieces saisies sur des ordres clotures.

Revision ID: 031_add_maintenance_priority_parts
Revises: 030_add_quote_client_scope
Create Date: 2026-10-03
"""
from alembic import op
import sqlalchemy as sa


revision = "031_add_maintenance_priority_parts"
down_revision = "030_add_quote_client_scope"
branch_labels = None
depends_on = None


TABLE = "maintenances"
COLONNES = {
    "priorite": sa.String(20),
    "pieces": sa.Text(),
}


def upgrade():
    insp = sa.inspect(op.get_bind())
    if TABLE not in set(insp.get_table_names()):
        # Base neuve : create_all / parite ORM creent deja les colonnes.
        return
    colonnes = {c["name"] for c in insp.get_columns(TABLE)}
    for nom, type_ in COLONNES.items():
        if nom not in colonnes:
            op.add_column(TABLE, sa.Column(nom, type_, nullable=True))


def downgrade():
    """Volontairement sans effet (conventions 027/029/030).

    Les deux colonnes portent des saisies d'atelier sur des ordres deja
    clotures : les dropper est irreversible et sans benefit.
    """
    pass
