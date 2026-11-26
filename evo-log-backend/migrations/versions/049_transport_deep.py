"""049 : tables expansion transport-flotte (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "049_transport_deep"
down_revision = "048_transit_deep"
branch_labels = None
depends_on = None


TABLES = [
    "vehicle_registrations",
    "route_plans",
    "checkpoint_controls",
    "cargo_insurances",
    "freight_bills",
    "subcontractors",
    "dangerous_goods_loads",
    "vehicle_documents",
    "gps_devices",
    "traffic_penalties",
    "convoys",
    "fleet_kpis",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("vehicle_registrations"):
        op.create_table(
            "vehicle_registrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_immatriculation", sa.String(200), nullable=False, index=True),
            sa.Column("marque", sa.String(200), nullable=True),
            sa.Column("modele", sa.String(200), nullable=True),
            sa.Column("annee_mise_circulation", sa.Integer, nullable=True),
            sa.Column("type_vehicule", sa.String(50), nullable=True),
            sa.Column("ptt_tonnes", sa.Numeric, nullable=True),
            sa.Column("puissance_cv", sa.Integer, nullable=True),
            sa.Column("kilometrage_actuel", sa.Numeric, nullable=True),
            sa.Column("couleur", sa.String(200), nullable=True),
            sa.Column("carrosserie", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_immatriculation", name="uix_vehicle_registrations_uniq"),
        )

    if not _has("route_plans"):
        op.create_table(
            "route_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tournee", sa.String(200), nullable=False, index=True),
            sa.Column("date_tournee", sa.Date, nullable=True),
            sa.Column("chauffeur_id", sa.Integer, nullable=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("nb_points", sa.Integer, nullable=True),
            sa.Column("distance_km", sa.Numeric, nullable=True),
            sa.Column("duree_estimee_h", sa.Numeric, nullable=True),
            sa.Column("zonale", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tournee", name="uix_route_plans_uniq"),
        )

    if not _has("checkpoint_controls"):
        op.create_table(
            "checkpoint_controls",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_pv", sa.String(200), nullable=False, index=True),
            sa.Column("date_controle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("poids_reel_t", sa.Numeric, nullable=True),
            sa.Column("poids_autorise_t", sa.Numeric, nullable=True),
            sa.Column("type_controle", sa.String(50), nullable=True),
            sa.Column("agent", sa.String(200), nullable=True),
            sa.Column("sanction_appliquee", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_pv", name="uix_checkpoint_controls_uniq"),
        )

    if not _has("cargo_insurances"):
        op.create_table(
            "cargo_insurances",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_police", sa.String(200), nullable=False, index=True),
            sa.Column("assureur", sa.String(200), nullable=True),
            sa.Column("type_garantie", sa.String(50), nullable=True),
            sa.Column("plafond_xaf", sa.Numeric, nullable=True),
            sa.Column("franchise_xaf", sa.Numeric, nullable=True),
            sa.Column("prime_xaf", sa.Numeric, nullable=True),
            sa.Column("date_effet", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_police", name="uix_cargo_insurances_uniq"),
        )

    if not _has("freight_bills"):
        op.create_table(
            "freight_bills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_facture", sa.String(200), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("mission_id", sa.Integer, nullable=True),
            sa.Column("montant_ht_xaf", sa.Numeric, nullable=True),
            sa.Column("tva_xaf", sa.Numeric, nullable=True),
            sa.Column("total_ttc_xaf", sa.Numeric, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_facture", name="uix_freight_bills_uniq"),
        )

    if not _has("subcontractors"):
        op.create_table(
            "subcontractors",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_sous_traitant", sa.String(200), nullable=False, index=True),
            sa.Column("raison_sociale", sa.String(200), nullable=True),
            sa.Column("niu", sa.String(200), nullable=True),
            sa.Column("contact", sa.String(200), nullable=True),
            sa.Column("telephone", sa.String(200), nullable=True),
            sa.Column("nb_camions", sa.Integer, nullable=True),
            sa.Column("zones_couvertes", sa.Text, nullable=True),
            sa.Column("agreement_numero", sa.String(200), nullable=True),
            sa.Column("date_expiration_agreement", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_sous_traitant", name="uix_subcontractors_uniq"),
        )

    if not _has("dangerous_goods_loads"):
        op.create_table(
            "dangerous_goods_loads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("mission_id", sa.Integer, nullable=True),
            sa.Column("onu_number", sa.String(200), nullable=True),
            sa.Column("classe_adr", sa.String(200), nullable=True),
            sa.Column("designation_officielle", sa.String(200), nullable=True),
            sa.Column("groupe_emballage", sa.String(50), nullable=True),
            sa.Column("quantite_kg", sa.Numeric, nullable=True),
            sa.Column("etiquettes", sa.String(200), nullable=True),
            sa.Column("formation_chauffeur", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dangerous_goods_loads_uniq"),
        )

    if not _has("vehicle_documents"):
        op.create_table(
            "vehicle_documents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_document", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("type_document", sa.String(50), nullable=True),
            sa.Column("autorite_emission", sa.String(200), nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("numero_police_associe", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_document", name="uix_vehicle_documents_uniq"),
        )

    if not _has("gps_devices"):
        op.create_table(
            "gps_devices",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_serial_gps", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("modele", sa.String(200), nullable=True),
            sa.Column("numero_sim", sa.String(200), nullable=True),
            sa.Column("date_installation", sa.Date, nullable=True),
            sa.Column("date_derniere_communication", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_serial_gps", name="uix_gps_devices_uniq"),
        )

    if not _has("traffic_penalties"):
        op.create_table(
            "traffic_penalties",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_pv", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule_id", sa.Integer, nullable=True),
            sa.Column("date_infraction", sa.Date, nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("type_infraction", sa.String(50), nullable=True),
            sa.Column("montant_amende_xaf", sa.Numeric, nullable=True),
            sa.Column("points_retires", sa.Integer, nullable=True),
            sa.Column("chauffeur_id", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_pv", name="uix_traffic_penalties_uniq"),
        )

    if not _has("convoys"):
        op.create_table(
            "convoys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_convoi", sa.String(200), nullable=False, index=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_arrivee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("nb_vehicules", sa.Integer, nullable=True),
            sa.Column("type_escorte", sa.String(50), nullable=True),
            sa.Column("chef_convoi", sa.String(200), nullable=True),
            sa.Column("itineraire", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_convoi", name="uix_convoys_uniq"),
        )

    if not _has("fleet_kpis"):
        op.create_table(
            "fleet_kpis",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("cout_total_xaf", sa.Numeric, nullable=True),
            sa.Column("km_parcourus", sa.Numeric, nullable=True),
            sa.Column("cout_par_km", sa.Numeric, nullable=True),
            sa.Column("taux_dispo_pct", sa.Numeric, nullable=True),
            sa.Column("taux_service_pct", sa.Numeric, nullable=True),
            sa.Column("nb_accidents", sa.Integer, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fleet_kpis_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
