"""isolation multi-tenant: company_id sur les racines transactionnelles

Merge des deux tetes existantes (010_add_outbox_events +
20260919_add_quote_company_scope) puis ajoute company_id (cle de cloisonnement
usee par app.core.tenant_enforcement) + index aux documents metiers qui en
etaient depourvus : tiers (=> clients/fournisseurs par heritage joined-table),
dossiers_transit, vehicules, reglements, ordres_transport, bons_commande,
bons_reception.

Idempotent : chaque colonne/index n'est cree que s'il manque, pour cohabiter
avec Base.metadata.create_all() utilise sur les deploiements neufs.

Revision ID: 011_tenant_scope_roots
Revises: 010_add_outbox_events, 20260919_add_quote_company_scope
"""
from alembic import op
import sqlalchemy as sa


revision = "011_tenant_scope_roots"
down_revision = ("010_add_outbox_events", "20260919_add_quote_company_scope")
branch_labels = None
depends_on = None


# (table, index_name) pour chaque racine transactionnelle a cloisonner.
_TABLES = [
    "tiers",
    "dossiers_transit",
    "vehicules",
    "reglements",
    "ordres_transport",
    "bons_commande",
    "bons_reception",
]


def _existing_columns(inspector, table):
    try:
        return {c["name"] for c in inspector.get_columns(table)}
    except Exception:
        return set()


def _existing_indexes(inspector, table):
    try:
        return {i["name"] for i in inspector.get_indexes(table)}
    except Exception:
        return set()


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables_seen = set(inspector.get_table_names())
    for table in _TABLES:
        if table not in tables_seen:
            continue
        cols = _existing_columns(inspector, table)
        if "company_id" not in cols:
            # batch_alter_table : ALTER ... ADD CONSTRAINT natif sur Postgres,
            # copy-and-move indispensable pour le rejouage SQLite sur base
            # vierge (sinon NotImplementedError du dialecte SQLite).
            with op.batch_alter_table(table) as batch_op:
                batch_op.add_column(
                    sa.Column("company_id", sa.Integer(), nullable=True),
                )
                batch_op.create_foreign_key(
                    f"fk_{table}_company_id",
                    "companies", ["company_id"], ["id"],
                )
        idx = _existing_indexes(inspector, table)
        if f"ix_{table}_company_id" not in idx:
            op.create_index(f"ix_{table}_company_id", table, ["company_id"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    tables_seen = set(inspector.get_table_names())
    for table in reversed(_TABLES):
        if table not in tables_seen:
            continue
        idx = _existing_indexes(inspector, table)
        if f"ix_{table}_company_id" in idx:
            op.drop_index(f"ix_{table}_company_id", table_name=table)
        cols = _existing_columns(inspector, table)
        if "company_id" in cols:
            # batch_alter_table : sur Postgres, DROP COLUMN cascade deja sur la
            # FK de cette colonne ; sur SQLite, un ALTER ... DROP CONSTRAINT /
            # DROP COLUMN natif n'existe pas -> le copy-and-move (RecreateStrategy)
            # recree la table sans company_id, ce qui retire aussi sa FK. On n'a
            # donc pas besoin d'un drop_constraint explicite (et SQLite ne garde
            # pas de nom de FK, ce qui ferait echouer un drop par nom).
            with op.batch_alter_table(table) as batch_op:
                batch_op.drop_column("company_id")
