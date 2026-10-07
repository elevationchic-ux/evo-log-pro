"""063 : tables expansion transport-aerien (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "063_aerien_deep"
down_revision = "062_ferroviaire_deep"
branch_labels = None
depends_on = None


TABLES = [
    "air_aircraft",
    "air_waybills",
    "air_slots",
    "air_handling_jobs",
    "air_uld",
    "air_cargo_security",
    "air_dg_shipments",
    "air_flight_operations",
    "air_crew_rosters",
    "air_mro_checks",
    "air_cargo_warehouses",
    "air_tariffs",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("air_aircraft"):
        op.create_table(
            "air_aircraft",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=False, index=True),
            sa.Column("modele", sa.String(200), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("capacite_tonnes", sa.Integer, nullable=True),
            sa.Column("autonomie_km", sa.Integer, nullable=True),
            sa.Column("heures_vol_total", sa.Integer, nullable=True),
            sa.Column("certificat_navigabilite_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "immatriculation", name="uix_air_aircraft_uniq"),
        )

    if not _has("air_waybills"):
        op.create_table(
            "air_waybills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_awb", sa.String(200), nullable=False, index=True),
            sa.Column("type_awb", sa.String(200), nullable=True),
            sa.Column("expediteur", sa.String(200), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("aeroport_depart", sa.String(200), nullable=True),
            sa.Column("aeroport_arrivee", sa.String(200), nullable=True),
            sa.Column("nb_pieces", sa.Integer, nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("valeur_declaree_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_awb", name="uix_air_waybills_uniq"),
        )

    if not _has("air_slots"):
        op.create_table(
            "air_slots",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("aeroport", sa.String(200), nullable=True),
            sa.Column("season", sa.String(200), nullable=True),
            sa.Column("vol_attribue", sa.String(200), nullable=True),
            sa.Column("journee", sa.String(200), nullable=True),
            sa.Column("heure_obtc", sa.String(200), nullable=True),
            sa.Column("slot_historique", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_slots_uniq"),
        )

    if not _has("air_handling_jobs"):
        op.create_table(
            "air_handling_jobs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vol", sa.String(200), nullable=True),
            sa.Column("aeroport", sa.String(200), nullable=True),
            sa.Column("date_traitement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("nb_pieces_fret", sa.Integer, nullable=True),
            sa.Column("poids_fret_kg", sa.Integer, nullable=True),
            sa.Column("cout_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_handling_jobs_uniq"),
        )

    if not _has("air_uld"):
        op.create_table(
            "air_uld",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_uld", sa.String(200), nullable=False, index=True),
            sa.Column("type_uld", sa.String(200), nullable=True),
            sa.Column("proprietaire", sa.String(200), nullable=True),
            sa.Column("position_actuelle", sa.String(200), nullable=True),
            sa.Column("etat", sa.String(200), nullable=True),
            sa.Column("date_derniere_inspection", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_uld", name="uix_air_uld_uniq"),
        )

    if not _has("air_cargo_security"):
        op.create_table(
            "air_cargo_security",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_awb", sa.String(200), nullable=True),
            sa.Column("statut_expediteur", sa.String(200), nullable=True),
            sa.Column("methode_screening", sa.String(200), nullable=True),
            sa.Column("date_screening", sa.DateTime(timezone=True), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("resultat", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_cargo_security_uniq"),
        )

    if not _has("air_dg_shipments"):
        op.create_table(
            "air_dg_shipments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_awb", sa.String(200), nullable=True),
            sa.Column("un_number", sa.String(200), nullable=True),
            sa.Column("classe", sa.String(200), nullable=True),
            sa.Column("packaging_group", sa.String(200), nullable=True),
            sa.Column("quantite", sa.String(200), nullable=True),
            sa.Column("etiquettes", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_dg_shipments_uniq"),
        )

    if not _has("air_flight_operations"):
        op.create_table(
            "air_flight_operations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_vol", sa.String(200), nullable=True),
            sa.Column("aeronef", sa.String(200), nullable=True),
            sa.Column("aeroport_depart", sa.String(200), nullable=True),
            sa.Column("aeroport_arrivee", sa.String(200), nullable=True),
            sa.Column("date_std", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_sta", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_ata", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_flight_operations_uniq"),
        )

    if not _has("air_crew_rosters"):
        op.create_table(
            "air_crew_rosters",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_membre", sa.String(200), nullable=True),
            sa.Column("role", sa.String(200), nullable=True),
            sa.Column("licence", sa.String(200), nullable=True),
            sa.Column("qualification", sa.String(200), nullable=True),
            sa.Column("date_prise_service", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin_service", sa.DateTime(timezone=True), nullable=True),
            sa.Column("heures_vol_mois", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_crew_rosters_uniq"),
        )

    if not _has("air_mro_checks"):
        op.create_table(
            "air_mro_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("type_check", sa.String(200), nullable=True),
            sa.Column("atelier", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin_prevue", sa.Date, nullable=True),
            sa.Column("date_retour_service", sa.Date, nullable=True),
            sa.Column("heures_arret", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_air_mro_checks_uniq"),
        )

    if not _has("air_cargo_warehouses"):
        op.create_table(
            "air_cargo_warehouses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_entrepot", sa.String(200), nullable=False, index=True),
            sa.Column("aeroport", sa.String(200), nullable=True),
            sa.Column("superficie_m2", sa.Integer, nullable=True),
            sa.Column("capacite_palettes", sa.Integer, nullable=True),
            sa.Column("zones_froides", sa.Boolean, nullable=True),
            sa.Column("zone_douaniere", sa.Boolean, nullable=True),
            sa.Column("zone_surete", sa.Boolean, nullable=True),
            sa.Column("occupation_pct", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_entrepot", name="uix_air_cargo_warehouses_uniq"),
        )

    if not _has("air_tariffs"):
        op.create_table(
            "air_tariffs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(200), nullable=False, index=True),
            sa.Column("origine", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("poids_min_kg", sa.Integer, nullable=True),
            sa.Column("type_cargo", sa.String(200), nullable=True),
            sa.Column("prix_par_kg_xaf", sa.Integer, nullable=True),
            sa.Column("surcharges_xaf", sa.Integer, nullable=True),
            sa.Column("validite_debut", sa.Date, nullable=True),
            sa.Column("validite_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_air_tariffs_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
