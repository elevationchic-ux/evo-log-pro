"""040 : piece comptable en partie double (en-tete + lignes reels).

Le module exposait une ecriture "plate" : une ligne unique portant a la fois
un compte, un debit et un credit, sans jamais controler l'equilibre
somme(debit) == somme(credit) ni exiger les deux contreparties d'une operation.
La table `lignes_journal` (la structure multi-lignes d'une piece) existait mais
n'etait remplie par aucun chemin d'ecriture.

Cette migration prepare l'en-tete d'ecriture (`ecritures_comptables_ohada`) a
porter une VERITABLE piece equilibree :

    - ``total_debit``  : somme des debits des lignes de la piece.
    - ``total_credit`` : somme des credits des lignes de la piece.
    - ``statut``       : brouillon | valide | comptabilise.

Les lignes elles-memes vivent dans `lignes_journal` (deja presente) : une ligne
= un compte + (debit OU credit). L'equilibre et les regles metier sont appliques
dans le service (`PieceComptableService`), pas ici.

Proprietes (conventions 024/027/029/030/031/032/037) :
    - IDEMPOTENT par introspection : colonne deja presente -> no-op.
    - server_default pour ne pas casser les lignes existantes.
    - downgrade supprime les colonnes ajoutees.

Revision ID: 040_add_piece_double_entry
Revises: 039_rbac_amenagement_grants
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa


revision = "040_add_piece_double_entry"
down_revision = "039_rbac_amenagement_grants"
branch_labels = None
depends_on = None

TABLE = "ecritures_comptables_ohada"

# (nom, colonne) des colonnes a ajouter, dans l'ordre.
NEW_COLUMNS = [
    ("total_debit", sa.Numeric(15, 2), "0"),
    ("total_credit", sa.Numeric(15, 2), "0"),
    ("statut", sa.String(20), "brouillon"),
]


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if TABLE not in set(insp.get_table_names()):
        return
    existing = {c["name"] for c in insp.get_columns(TABLE)}
    for name, coltype, default in NEW_COLUMNS:
        if name not in existing:
            op.add_column(
                TABLE,
                sa.Column(name, coltype, nullable=True, server_default=default),
            )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if TABLE not in set(insp.get_table_names()):
        return
    existing = {c["name"] for c in insp.get_columns(TABLE)}
    for name, _coltype, _default in reversed(NEW_COLUMNS):
        if name in existing:
            with op.batch_alter_table(TABLE) as batch_op:
                batch_op.drop_column(name)
