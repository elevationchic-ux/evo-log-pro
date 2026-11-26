"""071 : tables expansion parc-vehicules (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "071_parc_b_deep"
down_revision = "070_ferroviaire_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "parcb_driver_assignments",
    "parcb_geofence_zones",
    "parcb_inspection_checklists",
    "parcb_lease_contracts",
    "parcb_toll_passes",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("parcb_driver_assignments"):
        op.create_table(
            "parcb_driver_assignments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("chauffeur", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("kilometrage_debut", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_parcb_driver_assignments_uniq"),
        )

    if not _has("parcb_geofence_zones"):
        op.create_table(
            "parcb_geofence_zones",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_zone", sa.String(200), nullable=False, index=True),
            sa.Column("nom_zone", sa.String(200), nullable=True),
            sa.Column("centre_lat", sa.String(200), nullable=True),
            sa.Column("centre_lng", sa.String(200), nullable=True),
            sa.Column("rayon_m", sa.Integer, nullable=True),
            sa.Column("alerte_sortie", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_zone", name="uix_parcb_geofence_zones_uniq"),
        )

    if not _has("parcb_inspection_checklists"):
        op.create_table(
            "parcb_inspection_checklists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("chauffeur", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("points_controles", sa.Integer, nullable=True),
            sa.Column("anomalies_nb", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_parcb_inspection_checklists_uniq"),
        )

    if not _has("parcb_lease_contracts"):
        op.create_table(
            "parcb_lease_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_contrat", sa.String(200), nullable=False, index=True),
            sa.Column("loueur", sa.String(200), nullable=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("loyer_mensuel_xaf", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_contrat", name="uix_parcb_lease_contracts_uniq"),
        )

    if not _has("parcb_toll_passes"):
        op.create_table(
            "parcb_toll_passes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_badge", sa.String(200), nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("solde_xaf", sa.Integer, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_badge", name="uix_parcb_toll_passes_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
