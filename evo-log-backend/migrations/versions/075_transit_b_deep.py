"""075 : tables expansion transit-douane (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "075_transit_b_deep"
down_revision = "074_amenagement_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "transitb_incoterms",
    "transitb_inspections",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("transitb_incoterms"):
        op.create_table(
            "transitb_incoterms",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("transfert_risque_lieu", sa.String(200), nullable=True),
            sa.Column("transport_principal", sa.String(200), nullable=True),
            sa.Column("version", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code", name="uix_transitb_incoterms_uniq"),
        )

    if not _has("transitb_inspections"):
        op.create_table(
            "transitb_inspections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("declaration", sa.String(200), nullable=True),
            sa.Column("type_visite", sa.String(200), nullable=True),
            sa.Column("agent", sa.String(200), nullable=True),
            sa.Column("bureau", sa.String(200), nullable=True),
            sa.Column("date_inspection", sa.DateTime(timezone=True), nullable=True),
            sa.Column("observation", sa.Text, nullable=True),
            sa.Column("conformite", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_transitb_inspections_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
