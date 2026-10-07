"""073 : tables expansion pipeline-oleoduc (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "073_pipeline_deep"
down_revision = "072_qhse_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "pipeline_sections",
    "pipeline_pump_stations",
    "pipeline_storage_tanks",
    "pipeline_metering_points",
    "pipeline_product_batches",
    "pipeline_pressure_readings",
    "pipeline_leak_detections",
    "pipeline_maintenance_works",
    "pipeline_injection_campaigns",
    "pipeline_ship_nominations",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("pipeline_sections"):
        op.create_table(
            "pipeline_sections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_section", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("type_produit", sa.String(150), nullable=True),
            sa.Column("diametre_mm", sa.Integer, nullable=True),
            sa.Column("epaisseur_paroi_mm", sa.Integer, nullable=True),
            sa.Column("longueur_km", sa.Integer, nullable=True),
            sa.Column("origine", sa.String(150), nullable=True),
            sa.Column("destination", sa.String(150), nullable=True),
            sa.Column("date_mise_service", sa.Date, nullable=True),
            sa.Column("pression_max_bar", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_section", name="uix_pipeline_sections_uniq"),
        )

    if not _has("pipeline_pump_stations"):
        op.create_table(
            "pipeline_pump_stations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_station", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("type_station", sa.String(150), nullable=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("nb_pompes", sa.Integer, nullable=True),
            sa.Column("puissance_totale_kw", sa.Integer, nullable=True),
            sa.Column("debit_nominal_m3h", sa.Integer, nullable=True),
            sa.Column("pression_refoulement_bar", sa.Integer, nullable=True),
            sa.Column("energie_annuelle_kwh", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_station", name="uix_pipeline_pump_stations_uniq"),
        )

    if not _has("pipeline_storage_tanks"):
        op.create_table(
            "pipeline_storage_tanks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_cuve", sa.String(150), nullable=False, index=True),
            sa.Column("type_cuve", sa.String(150), nullable=True),
            sa.Column("capacite_m3", sa.Integer, nullable=True),
            sa.Column("niveau_actuel_pct", sa.Integer, nullable=True),
            sa.Column("temperature_stockage_c", sa.Integer, nullable=True),
            sa.Column("produit_stocke", sa.String(150), nullable=True),
            sa.Column("date_dernier_nettoyage", sa.Date, nullable=True),
            sa.Column("prochaine_inspection", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_cuve", name="uix_pipeline_storage_tanks_uniq"),
        )

    if not _has("pipeline_metering_points"):
        op.create_table(
            "pipeline_metering_points",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_point", sa.String(150), nullable=False, index=True),
            sa.Column("usage", sa.String(150), nullable=True),
            sa.Column("technologie", sa.String(150), nullable=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("precision_pct", sa.Integer, nullable=True),
            sa.Column("debit_max_m3h", sa.Integer, nullable=True),
            sa.Column("date_etalonnage", sa.Date, nullable=True),
            sa.Column("prochain_etalonnage", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_point", name="uix_pipeline_metering_points_uniq"),
        )

    if not _has("pipeline_product_batches"):
        op.create_table(
            "pipeline_product_batches",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_lot", sa.String(150), nullable=False, index=True),
            sa.Column("produit", sa.String(150), nullable=True),
            sa.Column("volume_m3", sa.Integer, nullable=True),
            sa.Column("densite_api", sa.Integer, nullable=True),
            sa.Column("teneur_soufre_pct", sa.Integer, nullable=True),
            sa.Column("injection_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("arrivee_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("destinataire", sa.String(150), nullable=True),
            sa.Column("section_utilisee", sa.String(150), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_lot", name="uix_pipeline_product_batches_uniq"),
        )

    if not _has("pipeline_pressure_readings"):
        op.create_table(
            "pipeline_pressure_readings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("date_releve", sa.DateTime(timezone=True), nullable=True),
            sa.Column("pression_entree_bar", sa.Integer, nullable=True),
            sa.Column("pression_sortie_bar", sa.Integer, nullable=True),
            sa.Column("debit_m3h", sa.Integer, nullable=True),
            sa.Column("temperature_c", sa.Integer, nullable=True),
            sa.Column("qualite", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipeline_pressure_readings_uniq"),
        )

    if not _has("pipeline_leak_detections"):
        op.create_table(
            "pipeline_leak_detections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("date_detection", sa.DateTime(timezone=True), nullable=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("technologie", sa.String(150), nullable=True),
            sa.Column("perte_estimee_m3", sa.Integer, nullable=True),
            sa.Column("severite", sa.String(150), nullable=True),
            sa.Column("lat_localisation", sa.String(150), nullable=True),
            sa.Column("lon_localisation", sa.String(150), nullable=True),
            sa.Column("delai_reparation_h", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipeline_leak_detections_uniq"),
        )

    if not _has("pipeline_maintenance_works"):
        op.create_table(
            "pipeline_maintenance_works",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("type_travaux", sa.String(150), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin_prevue", sa.Date, nullable=True),
            sa.Column("date_fin_reelle", sa.Date, nullable=True),
            sa.Column("cout_xaf", sa.Integer, nullable=True),
            sa.Column("prestataire", sa.String(150), nullable=True),
            sa.Column("arret_production_h", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipeline_maintenance_works_uniq"),
        )

    if not _has("pipeline_injection_campaigns"):
        op.create_table(
            "pipeline_injection_campaigns",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("type", sa.String(150), nullable=True),
            sa.Column("section_associee", sa.String(150), nullable=True),
            sa.Column("produit_chimique", sa.String(150), nullable=True),
            sa.Column("debit_injection_lh", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("volume_total_l", sa.Integer, nullable=True),
            sa.Column("cout_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipeline_injection_campaigns_uniq"),
        )

    if not _has("pipeline_ship_nominations"):
        op.create_table(
            "pipeline_ship_nominations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("nom_navire", sa.String(150), nullable=True),
            sa.Column("imo", sa.String(150), nullable=True),
            sa.Column("terminal", sa.String(150), nullable=True),
            sa.Column("produit_charge", sa.String(150), nullable=True),
            sa.Column("volume_m3", sa.Integer, nullable=True),
            sa.Column("eta", sa.Date, nullable=True),
            sa.Column("etb", sa.Date, nullable=True),
            sa.Column("etc", sa.Date, nullable=True),
            sa.Column("vacis", sa.String(150), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipeline_ship_nominations_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
