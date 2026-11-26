"""076 : tables expansion transport-flotte (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "076_transport_b_deep"
down_revision = "075_transit_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "transportb_dispatches",
    "transportb_pods",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("transportb_dispatches"):
        op.create_table(
            "transportb_dispatches",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("chauffeur", sa.String(200), nullable=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("point_depart", sa.String(200), nullable=True),
            sa.Column("point_arrivee", sa.String(200), nullable=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_arrivee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("km_parcourus", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_transportb_dispatches_uniq"),
        )

    if not _has("transportb_pods"):
        op.create_table(
            "transportb_pods",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("date_livraison", sa.DateTime(timezone=True), nullable=True),
            sa.Column("nb_colis_livres", sa.Integer, nullable=True),
            sa.Column("incidents", sa.String(200), nullable=True),
            sa.Column("signature_recu", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_transportb_pods_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
