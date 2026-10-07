"""077 : tables expansion magasin-stock (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "077_magasin_b_deep"
down_revision = "076_transport_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "magasinb_stock_counts",
    "magasinb_goods_receipts",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("magasinb_stock_counts"):
        op.create_table(
            "magasinb_stock_counts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("emplacement", sa.String(200), nullable=True),
            sa.Column("quantite_theorique", sa.Integer, nullable=True),
            sa.Column("quantite_physique", sa.Integer, nullable=True),
            sa.Column("ecart", sa.Integer, nullable=True),
            sa.Column("date_inventaire", sa.Date, nullable=True),
            sa.Column("agent", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magasinb_stock_counts_uniq"),
        )

    if not _has("magasinb_goods_receipts"):
        op.create_table(
            "magasinb_goods_receipts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("bon_commande", sa.String(200), nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("date_reception", sa.DateTime(timezone=True), nullable=True),
            sa.Column("nb_articles", sa.Integer, nullable=True),
            sa.Column("quantite_recue", sa.Integer, nullable=True),
            sa.Column("controles_fait", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magasinb_goods_receipts_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
