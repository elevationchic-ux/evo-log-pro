"""018 tables Tranche C : fleet (carburant, documents) + customers CRM
+ support (tickets, incidents)

Revision ID: 018_add_customer_support_fleet_tables
Revises: 017_add_parc_purchase_tables
Create Date: 2026-09-24

Tables creees :
    fleet_carburant_records, fleet_documents,
    crm_customers, crm_customer_contracts,
    support_tickets, support_incidents

NOTE : fleet/vehicles est un proxy sur la table VEHICULES existante (parc.py)
-> aucune table nouvelle pour les vehicules.

Meme voie que 014/016/017 : DDL generee depuis la metadata ORM (parite
stricte), idempotente (garde d'existence + checkfirst).
"""
from alembic import op
import sqlalchemy as sa


revision = "018_add_customer_support_fleet_tables"
down_revision = "017_add_parc_purchase_tables"
branch_labels = None
depends_on = None


# Topologique : les contrats référencent crm_customers.
TRANCHE_C_TABLES = [
    "crm_customers",
    "crm_customer_contracts",
    "fleet_carburant_records",
    "fleet_documents",
    "support_tickets",
    "support_incidents",
]


def _orm_metadata():
    import app.models  # noqa: F401 - enregistre toute la metadata ORM
    from app.core.database import Base
    return Base.metadata


def upgrade():
    bind = op.get_bind()
    metadata = _orm_metadata()
    existing = set(sa.inspect(bind).get_table_names())

    tables = [metadata.tables[name] for name in TRANCHE_C_TABLES if name not in existing]
    if not tables:
        return
    metadata.create_all(bind=bind, tables=tables, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())
    for name in reversed(TRANCHE_C_TABLES):
        if name not in existing:
            continue
        try:
            sa.Table(name, sa.MetaData(), autoload_with=bind).drop(
                bind=bind, checkfirst=True
            )
        except Exception:  # pragma: no cover - downgrade best-effort
            pass
