"""073 : tables expansion port-operations (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "073_port_ops_b_deep"
# Re-parente sur la pointe existante 076_heavylift_deep pour garder une chaine
# lineaire (un seul head) : la branche pipeline->courier->coldchain->heavylift
# etait deja en attente sur 072_qhse_b_deep.
down_revision = "076_heavylift_deep"
branch_labels = None
depends_on = None


TABLES = [
    "portb_berth_schedules",
    "portb_vessel_traffic",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("portb_berth_schedules"):
        op.create_table(
            "portb_berth_schedules",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("navire", sa.String(200), nullable=True),
            sa.Column("numero_imo", sa.String(200), nullable=True),
            sa.Column("poste_amarrage", sa.String(200), nullable=True),
            sa.Column("date_arrivee_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_depart_prevu", sa.DateTime(timezone=True), nullable=True),
            sa.Column("type_cargo", sa.String(200), nullable=True),
            sa.Column("pilote", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_portb_berth_schedules_uniq"),
        )

    if not _has("portb_vessel_traffic"):
        op.create_table(
            "portb_vessel_traffic",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_navire", sa.String(200), nullable=True),
            sa.Column("numero_imo", sa.String(200), nullable=True),
            sa.Column("mouvement", sa.String(200), nullable=True),
            sa.Column("balise_vts", sa.String(200), nullable=True),
            sa.Column("horodatage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_portb_vessel_traffic_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
