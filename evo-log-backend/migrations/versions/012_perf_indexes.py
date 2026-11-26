"""012 composite performance indexes

Add revision ID here: 012_perf_indexes
Create Date: 2026-09-23

Index composes (company_id, statut, date) sur les tables chaudes : le filtre
ORM multi-tenant ajoute company_id a toute requete, et les ecrans de pilotage
(dashboards, KPIs, listes) filtrent ensuite par statut et trient par date.
Sans ces index, chaque agrégation de dashboard fait un full scan filtre.
"""
from alembic import op
import sqlalchemy as sa

revision = "012_perf_indexes"
down_revision = "011_tenant_scope_roots"
branch_labels = None
depends_on = None


INDEXES = [
    # (nom, table, colonnes)
    ("idx_perf_factures_company_statut_date", "factures", ["company_id", "statut", "date_emission"]),
    ("idx_perf_factures_company_date", "factures", ["company_id", "date_emission"]),
    ("idx_perf_paiements_company_date", "paiements", ["company_id", "date_paiement"]),
    ("idx_perf_paiements_company_statut", "paiements", ["company_id", "statut"]),
    ("idx_perf_missions_company_statut_date", "missions", ["company_id", "statut", "created_at"]),
    ("idx_perf_camions_company_status", "camions", ["company_id", "status"]),
    ("idx_perf_mouvements_company_date", "mouvements_stocks", ["company_id", "date_mouvement"]),
    ("idx_perf_dossiers_transit_company_statut", "dossiers_transit", ["company_id", "statut", "created_at"]),
    ("idx_perf_ecritures_company_date", "ecritures_comptables", ["company_id", "created_at"]),
    ("idx_perf_reglements_company_statut", "reglements", ["company_id", "statut"]),
    ("idx_perf_cotations_company_statut", "cotations_devis", ["company_id", "statut", "created_at"]),
    # Outbox : le pump selectionne status='pending' tri par created_at
    ("idx_perf_outbox_status_date", "outbox_events", ["status", "created_at"]),
]


def _existing_index_names():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    names = set()
    for table in {item[1] for item in INDEXES}:
        try:
            for idx in insp.get_indexes(table):
                names.add(idx["name"])
        except Exception:
            # table absente (installations partielles) : on cree quand meme
            pass
    return names


def _schema_state():
    """Retourne (tables existantes, {table: colonnes existantes}) pour ignorer
    les index dont la table ou une colonne fait defaut. Certaines tables
    chaudes et leur colonne company_id ne sont materialisees que par
    create_all() (modele ORM), jamais par la chaine de migrations : sans cette
    garde, 'alembic upgrade head' sur base vierge echoue sur
    'no such column: company_id'."""
    insp = sa.inspect(op.get_bind())
    tables = set(insp.get_table_names())
    cols = {}
    for t in tables:
        try:
            cols[t] = {c["name"] for c in insp.get_columns(t)}
        except Exception:
            cols[t] = set()
    return tables, cols


def upgrade() -> None:
    existing = _existing_index_names()
    tables, cols = _schema_state()
    for name, table, columns in INDEXES:
        if name in existing:
            continue
        if table not in tables:
            continue  # table inexistante sur cette installation
        if not set(columns) <= cols.get(table, set()):
            continue  # colonne absente (ex. company_id non materialise) : on
            # laisse create_all()/la consolidation ajouter index + colonne.
        op.create_index(name, table, columns)


def downgrade() -> None:
    for name, table, _columns in reversed(INDEXES):
        try:
            op.drop_index(name, table_name=table)
        except Exception:
            pass
