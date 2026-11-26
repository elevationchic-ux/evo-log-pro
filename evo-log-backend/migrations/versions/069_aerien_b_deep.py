"""069 : tables expansion transport-aerien (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "069_aerien_b_deep"
down_revision = "068_fluvial_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "airb_house_waybills",
    "airb_perishable_cargo",
    "airb_live_animals",
    "airb_chartered_flights",
    "airb_customs_clearance",
    "airb_apron_movements",
    "airb_noise_compliance",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("airb_house_waybills"):
        op.create_table(
            "airb_house_waybills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_hawb", sa.String(200), nullable=False, index=True),
            sa.Column("numero_mawb", sa.String(200), nullable=True),
            sa.Column("expediteur", sa.String(200), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("nature_marchandise", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_hawb", name="uix_airb_house_waybills_uniq"),
        )

    if not _has("airb_perishable_cargo"):
        op.create_table(
            "airb_perishable_cargo",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_mawb", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("plage_temp_c", sa.String(200), nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("date_embarquement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_airb_perishable_cargo_uniq"),
        )

    if not _has("airb_live_animals"):
        op.create_table(
            "airb_live_animals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_mawb", sa.String(200), nullable=True),
            sa.Column("espece", sa.String(200), nullable=True),
            sa.Column("nb_animaux", sa.Integer, nullable=True),
            sa.Column("type_conteneur", sa.String(200), nullable=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_airb_live_animals_uniq"),
        )

    if not _has("airb_chartered_flights"):
        op.create_table(
            "airb_chartered_flights",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_affretement", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("depart_aeroport", sa.String(200), nullable=True),
            sa.Column("arrivee_aeroport", sa.String(200), nullable=True),
            sa.Column("capacite_tonnes", sa.Integer, nullable=True),
            sa.Column("date_vol", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_affretement", name="uix_airb_chartered_flights_uniq"),
        )

    if not _has("airb_customs_clearance"):
        op.create_table(
            "airb_customs_clearance",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_dossier", sa.String(200), nullable=False, index=True),
            sa.Column("numero_mawb", sa.String(200), nullable=True),
            sa.Column("type_operation", sa.String(200), nullable=True),
            sa.Column("bureau_douane", sa.String(200), nullable=True),
            sa.Column("droits_xaf", sa.Integer, nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_dossier", name="uix_airb_customs_clearance_uniq"),
        )

    if not _has("airb_apron_movements"):
        op.create_table(
            "airb_apron_movements",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("poste_parc", sa.String(200), nullable=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("type_mouvement", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_airb_apron_movements_uniq"),
        )

    if not _has("airb_noise_compliance"):
        op.create_table(
            "airb_noise_compliance",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("coefficient_bruit_db", sa.Integer, nullable=True),
            sa.Column("creneau", sa.String(200), nullable=True),
            sa.Column("date_mesure", sa.Date, nullable=True),
            sa.Column("quota_consomme", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_airb_noise_compliance_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
