"""024 Fermeture de la chaine documentaire (dossier marchandise de bout en bout).

Revision ID: 024_add_chaine_documentaire_links
Revises: 023_add_tarif_cemac_provenance
Create Date: 2026-09-26

Contexte (P1 issu du batch 6) : la vue consolidee
``app/services/dossier_marchandise.py`` ne pouvait relier honnetement que les
etapes portuaires (escale, connaissement, acconage, cycle, parc). Les quatre
etapes aval - declaration douaniere, magasin sous douane, mission de
livraison, facture - etaient renvoyees ``non_liciable_en_base`` : AUCUNE
colonne de ces tables ne reference un conteneur, une escale ou un B/L.

Cette migration prepare l'espace de rattachement SANS jamais deviner de
donnees (toutes les colonnes sont NULLables, aucune valeur n'est ecrite) :

    declarations_douaniere_avance : conteneur_id -> conteneurs.id
                                    escale_id    -> escales.id
                                    numero_bl    (reference saisie)
    declarations_entrepot         : conteneur_id -> conteneurs.id
                                    numero_bl
    missions                      : conteneur_id -> conteneurs.id
                                    numero_bl
    factures_ohada                : conteneur_id -> conteneurs.id
                                    escale_id    -> escales.id

Les FK sont declarees dans les modeles ORM ; ici elles sont ajoutees via le
mode batch SQLite (recreation de table) quand la table mere existe, et
silencieusement absentees sinon (base vierge : la revision de parite 014 ou
create_all cree deja les colonnes depuis l'ORM). Garde d'idempotence par
inspection : re-execution sure dans les deux sens.
"""
from alembic import op
import sqlalchemy as sa


revision = "024_add_chaine_documentaire_links"
down_revision = "023_add_tarif_cemac_provenance"
branch_labels = None
depends_on = None


# table -> {colonne: type} ; les FK sont portees par l'ORM et reproduites ici.
COLONNES = {
    "declarations_douaniere_avance": {
        "conteneur_id": sa.Integer(),
        "escale_id": sa.Integer(),
        "numero_bl": sa.String(length=50),
    },
    "declarations_entrepot": {
        "conteneur_id": sa.Integer(),
        "numero_bl": sa.String(length=50),
    },
    "missions": {
        "conteneur_id": sa.Integer(),
        "numero_bl": sa.String(length=50),
    },
    "factures_ohada": {
        "conteneur_id": sa.Integer(),
        "escale_id": sa.Integer(),
    },
}

FKS = {
    "declarations_douaniere_avance": [
        ("fk_ddavance_conteneur", "conteneur_id", "conteneurs", "id"),
        ("fk_ddavance_escale", "escale_id", "escales", "id"),
    ],
    "declarations_entrepot": [
        ("fk_declentrepot_conteneur", "conteneur_id", "conteneurs", "id"),
    ],
    "missions": [
        ("fk_mission_conteneur", "conteneur_id", "conteneurs", "id"),
    ],
    "factures_ohada": [
        ("fk_facture_ohada_conteneur", "conteneur_id", "conteneurs", "id"),
        ("fk_facture_ohada_escale", "escale_id", "escales", "id"),
    ],
}


def _tables(bind):
    return set(sa.inspect(bind).get_table_names())


def _colonnes(bind, table):
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def _index_existants(bind, table):
    try:
        return {i["name"] for i in sa.inspect(bind).get_indexes(table)}
    except Exception:  # noqa: BLE001 - table sans index interrogeable
        return set()


def upgrade():
    bind = op.get_bind()
    tables = _tables(bind)
    for table, new_cols in COLONNES.items():
        if table not in tables:
            # Table creee hors chaine (create_all / parite 014) : rien a ajouter.
            continue
        have = _colonnes(bind, table)
        missing = {k: v for k, v in new_cols.items() if k not in have}
        if not missing and _index_existants(bind, table) >= {
            f"ix_{table}_{c}" for c in new_cols
        }:
            continue
        with op.batch_alter_table(table) as batch_op:
            for name, col_type in missing.items():
                batch_op.add_column(sa.Column(name, col_type, nullable=True))
            for (fk_name, col, ref_table, ref_col) in FKS.get(table, []):
                # Poser la FK seulement si la table mere existe et si la
                # contrainte n'est pas deja declaree en base.
                if ref_table not in tables:
                    continue
                existing_fks = {
                    fk["name"]
                    for fk in sa.Inspector(bind).get_foreign_keys(table)
                    if fk["name"]
                }
                if fk_name in existing_fks:
                    continue
                batch_op.create_foreign_key(
                    fk_name, ref_table, [col], [ref_col]
                )
        # Index de rattachement (idempotent, nommage ORM ix_<table>_<col>).
        idx = _index_existants(bind, table)
        for col in new_cols:
            name = f"ix_{table}_{col}"
            if name not in idx:
                op.create_index(name, table, [col])


def downgrade():
    bind = op.get_bind()
    tables = _tables(bind)
    for table, new_cols in reversed(list(COLONNES.items())):
        if table not in tables:
            continue
        have = _colonnes(bind, table)
        present = [k for k in new_cols if k in have]
        if not present:
            continue
        # SQLite : drop_column en mode batch recopie les index reflechis ;
        # supprimer d'abord ceux des colonnes retirees, sinon la recree
        # echoue ("no such column").
        idx = _index_existants(bind, table)
        for col in present:
            name = f"ix_{table}_{col}"
            if name in idx:
                op.drop_index(name, table_name=table)
        with op.batch_alter_table(table) as batch_op:
            for name in present:
                batch_op.drop_column(name)
