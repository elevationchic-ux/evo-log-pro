"""053 : tables expansion parc-vehicules (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "053_parc_deep"
down_revision = "052_finance_deep"
branch_labels = None
depends_on = None


TABLES = [
    "vehicle_inventories",
    "tyre_records",
    "spare_parts",
    "workshop_appointments",
    "insurance_claims",
    "registration_records",
    "technical_visits",
    "fuel_consumptions",
    "vehicle_lifecycles",
    "cost_analyses",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("vehicle_inventories"):
        op.create_table(
            "vehicle_inventories",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_serie", sa.String(200), nullable=False, index=True),
            sa.Column("marque", sa.String(200), nullable=True),
            sa.Column("modele", sa.String(200), nullable=True),
            sa.Column("annee", sa.Integer, nullable=True),
            sa.Column("carrosserie", sa.String(200), nullable=True),
            sa.Column("energie", sa.String(50), nullable=True),
            sa.Column("kilometrage", sa.Numeric, nullable=True),
            sa.Column("cout_acquisition_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_argent_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_serie", name="uix_vehicle_inventories_uniq"),
        )

    if not _has("tyre_records"):
        op.create_table(
            "tyre_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_gomme", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("dimension", sa.String(200), nullable=True),
            sa.Column("marque", sa.String(200), nullable=True),
            sa.Column("position", sa.String(50), nullable=True),
            sa.Column("km_parcourus", sa.Numeric, nullable=True),
            sa.Column("profondeur_couronne_mm", sa.Numeric, nullable=True),
            sa.Column("date_montage", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_gomme", name="uix_tyre_records_uniq"),
        )

    if not _has("spare_parts"):
        op.create_table(
            "spare_parts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_piece", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("referencence_constructeur", sa.String(200), nullable=True),
            sa.Column("famille", sa.String(50), nullable=True),
            sa.Column("stock_actuel", sa.Numeric, nullable=True),
            sa.Column("seuil_mini", sa.Numeric, nullable=True),
            sa.Column("prix_unitaire_xaf", sa.Numeric, nullable=True),
            sa.Column("fournisseur_principal", sa.String(200), nullable=True),
            sa.Column("compatibilites", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_piece", name="uix_spare_parts_uniq"),
        )

    if not _has("workshop_appointments"):
        op.create_table(
            "workshop_appointments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date_horaire", sa.DateTime(timezone=True), nullable=True),
            sa.Column("type_intervention", sa.String(50), nullable=True),
            sa.Column("mecanicien", sa.String(200), nullable=True),
            sa.Column("duree_estimee_h", sa.Numeric, nullable=True),
            sa.Column("cout_estime_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_workshop_appointments_uniq"),
        )

    if not _has("insurance_claims"):
        op.create_table(
            "insurance_claims",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_sinistre", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date_sinistre", sa.Date, nullable=True),
            sa.Column("type_sinistre", sa.String(50), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("montant_estime_xaf", sa.Numeric, nullable=True),
            sa.Column("montant_indemnise_xaf", sa.Numeric, nullable=True),
            sa.Column("assureur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_sinistre", name="uix_insurance_claims_uniq"),
        )

    if not _has("registration_records"):
        op.create_table(
            "registration_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_immatriculation", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("proprietaire", sa.String(200), nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("autorite", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_immatriculation", name="uix_registration_records_uniq"),
        )

    if not _has("technical_visits"):
        op.create_table(
            "technical_visits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_pv", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date_visite", sa.Date, nullable=True),
            sa.Column("centre_controle", sa.String(200), nullable=True),
            sa.Column("resultat", sa.String(50), nullable=True),
            sa.Column("observations", sa.Text, nullable=True),
            sa.Column("contre_visite_possible", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_pv", name="uix_technical_visits_uniq"),
        )

    if not _has("fuel_consumptions"):
        op.create_table(
            "fuel_consumptions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("litres", sa.Numeric, nullable=True),
            sa.Column("prix_total_xaf", sa.Numeric, nullable=True),
            sa.Column("km_etape", sa.Numeric, nullable=True),
            sa.Column("conso_l100km", sa.Numeric, nullable=True),
            sa.Column("station", sa.String(200), nullable=True),
            sa.Column("carburant", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fuel_consumptions_uniq"),
        )

    if not _has("vehicle_lifecycles"):
        op.create_table(
            "vehicle_lifecycles",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date_acquisition", sa.Date, nullable=True),
            sa.Column("date_reforme", sa.Date, nullable=True),
            sa.Column("duree_detention_an", sa.Integer, nullable=True),
            sa.Column("km_final", sa.Numeric, nullable=True),
            sa.Column("mode_reforme", sa.String(50), nullable=True),
            sa.Column("valeur_recuperation_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_vehicle_lifecycles_uniq"),
        )

    if not _has("cost_analyses"):
        op.create_table(
            "cost_analyses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("cout_carburant_xaf", sa.Numeric, nullable=True),
            sa.Column("cout_maintenance_xaf", sa.Numeric, nullable=True),
            sa.Column("cout_assurance_xaf", sa.Numeric, nullable=True),
            sa.Column("cout_amortissement_xaf", sa.Numeric, nullable=True),
            sa.Column("cout_total_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cost_analyses_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
