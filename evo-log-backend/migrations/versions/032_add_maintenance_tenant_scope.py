"""032 : portee multi-tenant des ordres de maintenance (GMAO).

La table ``maintenances`` ne portait pas de ``company_id``. Le filtre tenant
global (``app/core/tenant_enforcement.py``) ne reecrit que les entites qui
possedent cette colonne : ``GET /api/v1/maintenance``, ``/stats`` et
``/analytics/kpis`` etaient donc lus **sans aucune isolation**  un utilisateur
authentifie voyait toute la GMAO de tous les tenants, y compris les couts
d'atelier et les immatriculations.

Aucune valeur n'est inventee pour les lignes deja en base : ``company_id`` est
derive de la seule relation reellement disponible, le vehicule rattache
(``maintenances.vehicule_id -> vehicules.company_id``). Un ordre sans vehicule,
ou dont le vehicule n'a pas d'entreprise, reste ``NULL`` et devient donc
invisible aux requetes scoping : mieux vaut une ligne non rattachee qu'une ligne
attribuee a un tenant choisi au hasard. Les nouvelles ecritures sont posees par
le ``before_flush`` de tenant_enforcement.

Proprietes (conventions 024/027/029/030/031) :
    - IDEMPOTENT par introspection : colonne/FK/index deja presents -> no-op ;
      table absente (base vierge alignee par create_all ou les migrations de
      parite) -> no-op.
    - FK en mode batch SQLite, native PostgreSQL.
    - downgrade sans effet assume : dropper la colonne supprimerait la portee
      d'ordres deja clotures et ferait rejouer le probleme d'isolation.

Revision ID: 032_add_maintenance_tenant_scope
Revises: 031_add_maintenance_priority_parts
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa


revision = "032_add_maintenance_tenant_scope"
down_revision = "031_add_maintenance_priority_parts"
branch_labels = None
depends_on = None


TABLE = "maintenances"
CIBLE_FK = "companies"
COLONNE = "company_id"
FK_NOM = "fk_maintenances_company_id_companies"


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if TABLE not in set(insp.get_table_names()):
        return
    dialect = op.get_context().dialect.name
    colonnes = {c["name"] for c in insp.get_columns(TABLE)}

    if COLONNE not in colonnes:
        op.add_column(TABLE, sa.Column(COLONNE, sa.Integer(), nullable=True))

    index_existants = {i["name"] for i in insp.get_indexes(TABLE)}
    nom_index = f"ix_{TABLE}_{COLONNE}"
    if nom_index not in index_existants:
        op.create_index(nom_index, TABLE, [COLONNE])

    # Rattrapage honnete : on ne choisit pas un tenant, on lit celui du vehicule.
    if CIBLE_FK in set(insp.get_table_names()) and "vehicules" in set(insp.get_table_names()):
        orphelines = bind.execute(
            sa.text(f"SELECT id, vehicule_id FROM {TABLE} WHERE {COLONNE} IS NULL")
        ).fetchall()
        for ident, vehicule_id in orphelines:
            if vehicule_id is None:
                continue
            entreprise = bind.execute(
                sa.text("SELECT company_id FROM vehicules WHERE id = :v"),
                {"v": vehicule_id},
            ).scalar()
            if entreprise is not None:
                bind.execute(
                    sa.text(f"UPDATE {TABLE} SET {COLONNE} = :c WHERE id = :i"),
                    {"c": entreprise, "i": ident},
                )

        fks_exist = {fk["name"] for fk in insp.get_foreign_keys(TABLE) if fk["name"]}
        if FK_NOM not in fks_exist:
            if dialect == "postgresql":
                op.create_foreign_key(FK_NOM, TABLE, CIBLE_FK, [COLONNE], ["id"])
            else:
                with op.batch_alter_table(TABLE) as batch_op:
                    batch_op.create_foreign_key(FK_NOM, CIBLE_FK, [COLONNE], ["id"])


def downgrade():
    """Volontairement sans effet (conventions 027/029/030/031).

    Retirer la colonne ramenerait la table hors du perimetre tenant : la
    portee redeviendrait globale, ce qui est exactement le defaut corrige ici.
    """
    pass
