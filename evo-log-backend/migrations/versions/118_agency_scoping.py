"""118 : perimetre agence — colonnes agency_id sur les donnees metier.

Le module Agences (routeur ``agences`` + ``app.core.agency_enforcement``)
scope les requetes ORM sur la colonne ``agency_id`` quand une agence est
active. Cette migration ajoute la colonne aux tables metier concernees :

  agencies        : + company_id (isolement tenant — avant, la table
                    n'avait que organization_id et n'etait pas scopee par
                    tenant_enforcement), + type_agence, + parent_id
                    (hierarchie siege -> agence -> extension/bureau)
  users           : + current_agency_id (agence ACTIVE de session, distincte
                    de agency_id = agence d'appartenance)
  tiers           : + agency_id (couvre clients/fournisseurs/partenaires,
                    heritage joint)
  camions, conducteurs, missions (transport)
  vehicules       (parc)
  navires, escales, conteneurs (acconage — port_id des escales pointe deja
                    vers agencies : coherence renforcee)
  factures        (finance — CA par agence pour le comparatif)
  tours, livraisons (transport_avance)

Toutes les colonnes sont NULLABLE sans defaut : les lignes existantes
deviennent « partagees / non rattachees » (visibles par toutes les
agences) — aucune donnee n'est masquee retroactivement. Les nouvelles
insertions sont marquees automatiquement par agency_enforcement.

SQLite : ADD COLUMN nullable = rejouable. PostgreSQL : idem. Les index
sont crees via create_index (IF NOT EXISTS gere par le dialecte).
"""
from alembic import op
import sqlalchemy as sa

revision = "118_agency_scoping"
down_revision = "117_transport_avance_fks"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {c["name"] for c in inspector.get_columns(table)}


def _add(table: str, column: str, col_type=sa.Integer, fk=None):
    if _has_column(table, column):
        return
    col = sa.Column(column, col_type, nullable=True)
    if fk:
        col.foreign_keys.add(sa.ForeignKey(fk))
    op.add_column(table, col)
    try:
        op.create_index(f"ix_{table}_{column}", table, [column])
    except Exception:
        pass  # index deja present ou nom reserve — non bloquant


def upgrade() -> None:
    # agencies : rattachement tenant + hierarchie + type
    _add("agencies", "company_id", fk="companies.id")
    _add("agencies", "parent_id", fk="agencies.id")
    if not _has_column("agencies", "type_agence"):
        op.add_column("agencies", sa.Column("type_agence", sa.String(20), nullable=True))

    # users : agence active de session
    _add("users", "current_agency_id", fk="agencies.id")

    # donnees metier : perimetre agence
    _add("tiers", "agency_id", fk="agencies.id")
    _add("camions", "agency_id", fk="agencies.id")
    _add("conducteurs", "agency_id", fk="agencies.id")
    _add("missions", "agency_id", fk="agencies.id")
    _add("vehicules", "agency_id", fk="agencies.id")
    _add("navires", "agency_id", fk="agencies.id")
    _add("escales", "agency_id", fk="agencies.id")
    _add("conteneurs", "agency_id", fk="agencies.id")
    _add("factures", "agency_id", fk="agencies.id")
    _add("tours", "agency_id", fk="agencies.id")
    _add("livraisons", "agency_id", fk="agencies.id")


def downgrade() -> None:
    for table, column in [
        ("livraisons", "agency_id"), ("tours", "agency_id"),
        ("factures", "agency_id"), ("conteneurs", "agency_id"),
        ("escales", "agency_id"), ("navires", "agency_id"),
        ("vehicules", "agency_id"), ("missions", "agency_id"),
        ("conducteurs", "agency_id"), ("camions", "agency_id"),
        ("tiers", "agency_id"),
        ("users", "current_agency_id"),
        ("agencies", "type_agence"), ("agencies", "parent_id"),
        ("agencies", "company_id"),
    ]:
        if _has_column(table, column):
            try:
                op.drop_index(f"ix_{table}_{column}", table_name=table)
            except Exception:
                pass
            try:
                op.drop_column(table, column)
            except Exception:
                # SQLite refuse DROP COLUMN sur une colonne portant une
                # contrainte REFERENCES (reconstruction de table requise).
                # La colonne restante est nullable et inoffensive ; le
                # re-upgrade reste idempotent via _has_column. PostgreSQL
                # supprime la colonne et sa contrainte sans erreur.
                pass
