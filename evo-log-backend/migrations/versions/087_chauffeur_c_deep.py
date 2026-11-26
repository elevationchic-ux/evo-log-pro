"""087 : tables expansion portail-chauffeur (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "087_chauffeur_c_deep"
down_revision = "086_admin_tenant_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "chf_trip_sheets",
    "chf_daily_vehicle_checks",
    "chf_fuel_logs",
    "chf_driving_times",
    "chf_rest_breaks",
    "chf_toll_receipts",
    "chf_parking_sessions",
    "chf_cargo_seals",
    "chf_roadside_incidents",
    "chf_delivery_stops",
    "chf_mileage_logs",
    "chf_load_securing",
    "chf_border_crossings",
    "chf_delivery_appointments",
    "chf_ppe_issues",
    "chf_shift_handovers",
    "chf_breakdown_reports",
    "chf_tyre_checks",
    "chf_cargo_photos",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("chf_trip_sheets"):
        op.create_table(
            "chf_trip_sheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("km_debut", sa.Integer, nullable=True),
            sa.Column("km_fin", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_trip_sheets_uniq"),
        )

    if not _has("chf_daily_vehicle_checks"):
        op.create_table(
            "chf_daily_vehicle_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("points_controles", sa.Integer, nullable=True),
            sa.Column("anomalies", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_daily_vehicle_checks_uniq"),
        )

    if not _has("chf_fuel_logs"):
        op.create_table(
            "chf_fuel_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("litres", sa.Numeric, nullable=True),
            sa.Column("prix", sa.Numeric, nullable=True),
            sa.Column("station", sa.String(200), nullable=True),
            sa.Column("date_plein", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_fuel_logs_uniq"),
        )

    if not _has("chf_driving_times"):
        op.create_table(
            "chf_driving_times",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("chauffeur", sa.String(200), nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("minutes_conduite", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_driving_times_uniq"),
        )

    if not _has("chf_rest_breaks"):
        op.create_table(
            "chf_rest_breaks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("chauffeur", sa.String(200), nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_min", sa.Integer, nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_rest_breaks_uniq"),
        )

    if not _has("chf_toll_receipts"):
        op.create_table(
            "chf_toll_receipts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("peage", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("date_passage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("troncon", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_toll_receipts_uniq"),
        )

    if not _has("chf_parking_sessions"):
        op.create_table(
            "chf_parking_sessions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("entree", sa.DateTime(timezone=True), nullable=True),
            sa.Column("sortie", sa.DateTime(timezone=True), nullable=True),
            sa.Column("frais", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_parking_sessions_uniq"),
        )

    if not _has("chf_cargo_seals"):
        op.create_table(
            "chf_cargo_seals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("numero_plomb", sa.String(200), nullable=True),
            sa.Column("pose_datetime", sa.DateTime(timezone=True), nullable=True),
            sa.Column("retrait_datetime", sa.DateTime(timezone=True), nullable=True),
            sa.Column("intact", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_cargo_seals_uniq"),
        )

    if not _has("chf_roadside_incidents"):
        op.create_table(
            "chf_roadside_incidents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_incident", sa.String(200), nullable=True),
            sa.Column("localisation", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("decrit", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_roadside_incidents_uniq"),
        )

    if not _has("chf_delivery_stops"):
        op.create_table(
            "chf_delivery_stops",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("tournee", sa.String(200), nullable=True),
            sa.Column("adresse", sa.String(200), nullable=True),
            sa.Column("ordre", sa.Integer, nullable=True),
            sa.Column("arrivee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("departure", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_delivery_stops_uniq"),
        )

    if not _has("chf_mileage_logs"):
        op.create_table(
            "chf_mileage_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("km_debut", sa.Integer, nullable=True),
            sa.Column("km_fin", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_mileage_logs_uniq"),
        )

    if not _has("chf_load_securing"):
        op.create_table(
            "chf_load_securing",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("sangles_ok", sa.Boolean, nullable=True),
            sa.Column("poids_equilibre", sa.String(200), nullable=True),
            sa.Column("controle_datetime", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_load_securing_uniq"),
        )

    if not _has("chf_border_crossings"):
        op.create_table(
            "chf_border_crossings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("poste", sa.String(200), nullable=True),
            sa.Column("pays", sa.String(200), nullable=True),
            sa.Column("entree_sortie", sa.String(200), nullable=True),
            sa.Column("horodatage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("documents_ok", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_border_crossings_uniq"),
        )

    if not _has("chf_delivery_appointments"):
        op.create_table(
            "chf_delivery_appointments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("creneau", sa.DateTime(timezone=True), nullable=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("contact", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_delivery_appointments_uniq"),
        )

    if not _has("chf_ppe_issues"):
        op.create_table(
            "chf_ppe_issues",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("equipement", sa.String(200), nullable=True),
            sa.Column("taille", sa.String(200), nullable=True),
            sa.Column("date_remise", sa.Date, nullable=True),
            sa.Column("etat", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_ppe_issues_uniq"),
        )

    if not _has("chf_shift_handovers"):
        op.create_table(
            "chf_shift_handovers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("sortant", sa.String(200), nullable=True),
            sa.Column("entrant", sa.String(200), nullable=True),
            sa.Column("datetime", sa.DateTime(timezone=True), nullable=True),
            sa.Column("consignes", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_shift_handovers_uniq"),
        )

    if not _has("chf_breakdown_reports"):
        op.create_table(
            "chf_breakdown_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("panne", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("date_signalement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("immobilise", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_breakdown_reports_uniq"),
        )

    if not _has("chf_tyre_checks"):
        op.create_table(
            "chf_tyre_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("numero_essieu", sa.Integer, nullable=True),
            sa.Column("pression_bar", sa.Numeric, nullable=True),
            sa.Column("usure_mm", sa.Numeric, nullable=True),
            sa.Column("date_controle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_tyre_checks_uniq"),
        )

    if not _has("chf_cargo_photos"):
        op.create_table(
            "chf_cargo_photos",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("prise", sa.DateTime(timezone=True), nullable=True),
            sa.Column("legende", sa.String(200), nullable=True),
            sa.Column("fichier", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_chf_cargo_photos_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
